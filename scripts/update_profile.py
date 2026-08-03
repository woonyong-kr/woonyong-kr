#!/usr/bin/env python3
"""Build a GitHub profile from pinned repositories and verified public activity."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from html import escape
import json
import os
from pathlib import Path
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request


BOT_LOGINS = {"dependabot[bot]", "github-actions[bot]"}
SKIP_SUBJECT_PREFIXES = ("chore:", "ci:", "docs:", "merge ")
SKIP_SUBJECTS = {"initial commit", "update", "updates"}
MARKERS = {
    "intro": ("<!-- profile_intro:start -->", "<!-- profile_intro:end -->"),
    "cards": ("<!-- project_cards:start -->", "<!-- project_cards:end -->"),
    "ci": ("<!-- ci_status:start -->", "<!-- ci_status:end -->"),
    "collaboration": ("<!-- collaboration:start -->", "<!-- collaboration:end -->"),
    "recent": ("<!-- recent_work:start -->", "<!-- recent_work:end -->"),
    "technologies": ("<!-- technologies:start -->", "<!-- technologies:end -->"),
}
TECHNOLOGIES = {
    "c": ("C", "A8B9CC", "c", "https://www.c-language.org/"),
    "c++": ("C++", "00599C", "cplusplus", "https://isocpp.org/"),
    "csharp": ("C#", "512BD4", "dotnet", "https://dotnet.microsoft.com/"),
    "fastapi": ("FastAPI", "009688", "fastapi", "https://fastapi.tiangolo.com/"),
    "gitops": ("GitOps", "F05032", "git", "https://opengitops.dev/"),
    "html": ("HTML", "E34F26", "html5", "https://html.spec.whatwg.org/"),
    "kubernetes": ("Kubernetes", "326CE5", "kubernetes", "https://kubernetes.io/"),
    "nats": ("NATS", "27AAE1", "natsdotio", "https://nats.io/"),
    "postgresql": ("PostgreSQL", "4169E1", "postgresql", "https://www.postgresql.org/"),
    "python": ("Python", "3776AB", "python", "https://www.python.org/"),
    "sql": ("SQL", "4479A1", "sqlite", "https://en.wikipedia.org/wiki/SQL"),
    "typescript": ("TypeScript", "3178C6", "typescript", "https://www.typescriptlang.org/"),
    "github-actions": (
        "GitHub Actions",
        "2088FF",
        "githubactions",
        "https://github.com/features/actions",
    ),
}


@dataclass(frozen=True)
class Repository:
    name: str
    name_with_owner: str
    description: str
    url: str
    is_fork: bool
    is_archived: bool
    stargazer_count: int
    fork_count: int
    primary_language: str
    topics: tuple[str, ...]
    default_branch: str
    pushed_at: str


@dataclass(frozen=True)
class RepositorySnapshot:
    repository: Repository
    commits: list[dict[str, object]]
    workflow: dict[str, object] | None


@dataclass(frozen=True)
class Profile:
    name: str
    login: str
    bio: str
    blog: str
    email: str
    url: str


def github_request(
    url: str,
    token: str,
    *,
    payload: dict[str, object] | None = None,
) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "woonyong-profile-index",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, headers=headers, data=data)
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {error.code}: {detail}") from error


def repository_fields() -> str:
    return """
      name
      nameWithOwner
      description
      url
      isFork
      isArchived
      stargazerCount
      forkCount
      pushedAt
      defaultBranchRef { name }
      primaryLanguage { name }
      repositoryTopics(first: 20) { nodes { topic { name } } }
    """


def discover_profile(login: str, token: str) -> Profile:
    response = github_request(f"https://api.github.com/users/{login}", token)
    if not isinstance(response, dict) or not response.get("login"):
        raise RuntimeError(f"GitHub profile discovery failed: {login}")
    return Profile(
        name=str(response.get("name") or response["login"]),
        login=str(response["login"]),
        bio=str(response.get("bio") or ""),
        blog=str(response.get("blog") or ""),
        email=str(response.get("email") or ""),
        url=str(response["html_url"]),
    )


def discover_repositories(login: str, token: str) -> list[Repository]:
    if not token:
        raise RuntimeError("GH_TOKEN is required for repository discovery")
    query = f"""
    query($login: String!) {{
      user(login: $login) {{
        pinnedItems(first: 6, types: REPOSITORY) {{
          nodes {{ ... on Repository {{ {repository_fields()} }} }}
        }}
        repositories(
          first: 100
          ownerAffiliations: OWNER
          privacy: PUBLIC
          orderBy: {{field: PUSHED_AT, direction: DESC}}
        ) {{
          nodes {{ {repository_fields()} }}
        }}
      }}
    }}
    """
    response = github_request(
        "https://api.github.com/graphql",
        token,
        payload={"query": query, "variables": {"login": login}},
    )
    if not isinstance(response, dict) or response.get("errors"):
        raise RuntimeError(f"GitHub GraphQL failed: {response}")
    user = response.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {login}")

    def parse(node: dict[str, object]) -> Repository:
        topics = tuple(
            item["topic"]["name"]
            for item in node.get("repositoryTopics", {}).get("nodes", [])
        )
        language = (node.get("primaryLanguage") or {}).get("name") or ""
        branch = (node.get("defaultBranchRef") or {}).get("name") or "main"
        return Repository(
            name=str(node["name"]),
            name_with_owner=str(node["nameWithOwner"]),
            description=str(node.get("description") or ""),
            url=str(node["url"]),
            is_fork=bool(node["isFork"]),
            is_archived=bool(node["isArchived"]),
            stargazer_count=int(node["stargazerCount"]),
            fork_count=int(node["forkCount"]),
            primary_language=str(language),
            topics=topics,
            default_branch=str(branch),
            pushed_at=str(node["pushedAt"]),
        )

    def eligible(repository: Repository) -> bool:
        return (
            not repository.is_fork
            and not repository.is_archived
            and repository.name_with_owner != f"{login}/{login}"
            and bool(repository.description)
        )

    pinned = [parse(node) for node in user["pinnedItems"]["nodes"]]
    owned = [parse(node) for node in user["repositories"]["nodes"]]
    selected: list[Repository] = []
    seen: set[str] = set()
    for repository in [*pinned, *owned]:
        if (
            eligible(repository)
            and repository.name_with_owner not in seen
            and len(selected) < 6
        ):
            selected.append(repository)
            seen.add(repository.name_with_owner)
    if len(selected) != 6:
        raise RuntimeError("Six eligible repositories are required for a full card grid")
    return selected


def meaningful_subject(subject: str) -> bool:
    normalized = subject.strip().lower()
    return normalized not in SKIP_SUBJECTS and not normalized.startswith(
        SKIP_SUBJECT_PREFIXES
    )


def human_commit(commit: dict[str, object]) -> bool:
    author = commit.get("author") or {}
    subject = str(commit["commit"]["message"]).splitlines()[0]
    return author.get("login") not in BOT_LOGINS and meaningful_subject(subject)


def select_workflow(workflows: list[dict[str, object]]) -> dict[str, object] | None:
    active = [
        workflow
        for workflow in workflows
        if workflow.get("state") == "active"
        and str(workflow.get("path") or "").startswith(".github/workflows/")
    ]
    if not active:
        return None

    def priority(workflow: dict[str, object]) -> tuple[int, str]:
        path = str(workflow.get("path") or "").lower()
        filename = path.rsplit("/", 1)[-1]
        if filename in {"ci.yml", "ci.yaml"}:
            rank = 0
        elif re.search(r"(^|[-_.])ci([-_.]|$)", filename):
            rank = 1
        elif "test" in filename:
            rank = 2
        elif "deploy" in filename or "pages" in filename:
            rank = 3
        else:
            rank = 4
        return rank, path

    return sorted(active, key=priority)[0]


def collect_snapshots(
    repositories: list[Repository], token: str
) -> list[RepositorySnapshot]:
    snapshots: list[RepositorySnapshot] = []
    for repository in repositories:
        commits = github_request(
            f"https://api.github.com/repos/{repository.name_with_owner}/commits?per_page=100",
            token,
        )
        if not isinstance(commits, list) or not commits:
            raise RuntimeError(f"Commit history is empty: {repository.name_with_owner}")
        response = github_request(
            f"https://api.github.com/repos/{repository.name_with_owner}/actions/workflows?per_page=100",
            token,
        )
        workflows = response.get("workflows", []) if isinstance(response, dict) else []
        snapshots.append(
            RepositorySnapshot(repository, commits, select_workflow(workflows))
        )
    return snapshots


def collect_commits(
    snapshots: list[RepositorySnapshot], login: str
) -> list[dict[str, str]]:
    collected: list[dict[str, str]] = []
    for snapshot in snapshots:
        for commit in snapshot.commits:
            author = commit.get("author") or {}
            if not human_commit(commit) or author.get("login") != login:
                continue
            metadata = commit["commit"]
            collected.append(
                {
                    "id": f"{snapshot.repository.name_with_owner}@{commit['sha']}",
                    "kind": "commit",
                    "project": snapshot.repository.name,
                    "repository": snapshot.repository.name_with_owner,
                    "title": str(metadata["message"]).splitlines()[0],
                    "url": str(commit["html_url"]),
                    "occurred_at": str(metadata["author"]["date"]),
                }
            )
    return collected


def collect_merged_prs(login: str, token: str) -> list[dict[str, str]]:
    query = urllib.parse.urlencode(
        {
            "q": f"author:{login} is:pr is:merged",
            "sort": "updated",
            "order": "desc",
            "per_page": 100,
        }
    )
    response = github_request(f"https://api.github.com/search/issues?{query}", token)
    items = response.get("items", []) if isinstance(response, dict) else []
    collected: list[dict[str, str]] = []
    for item in items:
        repository = str(item["repository_url"]).split("/repos/", 1)[-1]
        if repository.startswith(f"{login}/"):
            continue
        number = str(item["number"])
        collected.append(
            {
                "id": f"{repository}#{number}",
                "kind": "pull_request",
                "project": repository,
                "repository": repository,
                "title": str(item["title"]),
                "url": str(item["html_url"]),
                "occurred_at": str(item.get("closed_at") or item["updated_at"]),
            }
        )
    return collected


def merge_history(
    history_path: Path,
    commits: list[dict[str, str]],
    pull_requests: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"commits": [], "pull_requests": []}
    for key, incoming in (("commits", commits), ("pull_requests", pull_requests)):
        merged = {item["id"]: item for item in history.get(key, [])}
        merged.update({item["id"]: item for item in incoming})
        items = merged.values()
        if key == "commits":
            items = (item for item in items if meaningful_subject(item["title"]))
        history[key] = sorted(
            items, key=lambda item: item["occurred_at"], reverse=True
        )[:1000]
    return history


LANGUAGE_COLORS = {
    "C": "#555555",
    "C#": "#178600",
    "C++": "#f34b7d",
    "HTML": "#e34c26",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
}


def card_filename(repository: Repository) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", repository.name).strip("-")
    return f"repo-{slug}.svg"


def render_card_svg(repository: Repository) -> str:
    description = repository.description.strip() or "설명 없음"
    description_lines = textwrap.wrap(
        description, width=48, break_long_words=False, break_on_hyphens=False
    )[:2]
    while len(description_lines) < 2:
        description_lines.append("")
    language = repository.primary_language or "Unknown"
    language_color = LANGUAGE_COLORS.get(language, "#8b949e")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="410" height="132" viewBox="0 0 410 132" role="img" aria-label="{escape(repository.name)} repository card">
  <style>
    .card {{ fill: #ffffff; stroke: #d0d7de; }}
    .title {{ fill: #0969da; font: 600 16px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .body {{ fill: #57606a; font: 12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .meta {{ fill: #57606a; font: 11px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    @media (prefers-color-scheme: dark) {{
      .card {{ fill: #0d1117; stroke: #30363d; }}
      .title {{ fill: #58a6ff; }}
      .body, .meta {{ fill: #8b949e; }}
    }}
  </style>
  <rect class="card" x="0.5" y="0.5" width="409" height="131" rx="6"/>
  <text class="title" x="18" y="28">{escape(repository.name)}</text>
  <text class="body" x="18" y="54">{escape(description_lines[0])}</text>
  <text class="body" x="18" y="72">{escape(description_lines[1])}</text>
  <circle cx="21" cy="101" r="5" fill="{language_color}"/>
  <text class="meta" x="32" y="105">{escape(language)}</text>
  <text class="meta" x="145" y="105">Stars {repository.stargazer_count}</text>
  <text class="meta" x="207" y="105">Forks {repository.fork_count}</text>
  <text class="meta" x="282" y="105">Updated {repository.pushed_at[:10]}</text>
</svg>
'''


def write_cards(repositories: list[Repository], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    expected = {card_filename(repository) for repository in repositories}
    for existing in directory.glob("repo-*.svg"):
        if existing.name not in expected:
            existing.unlink()
    for repository in repositories:
        write_if_changed(directory / card_filename(repository), render_card_svg(repository))


def render_intro(profile: Profile) -> str:
    lines = [f"# {profile.name}", ""]
    if profile.bio:
        lines.append(f"**{profile.bio}**")
        lines.append("")
    links = [f"[GitHub]({profile.url})"]
    if profile.blog:
        blog = profile.blog if "://" in profile.blog else f"https://{profile.blog}"
        links.append(f"[기술 기록]({blog})")
    if profile.email:
        links.append(f"[Email](mailto:{profile.email})")
    lines.append(" · ".join(links))
    return "\n".join(lines)


def render_cards(repositories: list[Repository]) -> str:
    lines = ['<p align="center">']
    for index, repository in enumerate(repositories):
        lines.append(
            f'  <a href="{repository.url}"><img width="410" '
            f'src="assets/generated/{card_filename(repository)}" '
            f'alt="{repository.name} 저장소"></a>'
        )
        if index in {1, 3}:
            lines.append("  <br>")
    lines.append("</p>")
    return "\n".join(lines)


def render_ci(snapshots: list[RepositorySnapshot]) -> str:
    badges: list[str] = []
    for snapshot in snapshots:
        workflow = snapshot.workflow
        if workflow is None:
            continue
        repository = snapshot.repository
        path = str(workflow["path"])
        path_url = urllib.parse.quote(path.rsplit("/", 1)[-1], safe="")
        badge = (
            f"https://github.com/{repository.name_with_owner}/actions/workflows/"
            f"{path_url}/badge.svg?branch={urllib.parse.quote(repository.default_branch)}"
        )
        actions = f"https://github.com/{repository.name_with_owner}/actions"
        badges.append(
            f'<a href="{actions}"><img alt="{repository.name} CI" src="{badge}"></a>'
        )
    return "\n".join(badges) or "Actions workflow가 확인된 저장소 없음"


def render_technologies(
    repositories: list[Repository], snapshots: list[RepositorySnapshot]
) -> str:
    keys: list[str] = []
    for repository in repositories:
        if repository.primary_language:
            keys.append(repository.primary_language.lower())
        keys.extend(topic.lower() for topic in repository.topics)
    if any(snapshot.workflow is not None for snapshot in snapshots):
        keys.append("github-actions")
    counts = Counter(key for key in keys if key in TECHNOLOGIES)
    ordered = sorted(counts, key=lambda key: (-counts[key], TECHNOLOGIES[key][0]))
    badges: list[str] = []
    for key in ordered:
        label, color, logo, url = TECHNOLOGIES[key]
        badge_label = urllib.parse.quote(label.replace("-", "--").replace("_", "__"))
        badge = (
            f"https://img.shields.io/badge/{badge_label}-{color}"
            f"?style=flat-square&logo={urllib.parse.quote(logo)}&logoColor=white"
        )
        badges.append(f'<a href="{url}"><img alt="{label}" src="{badge}"></a>')
    return "\n".join(badges)


def recent_commits(history: dict[str, list[dict[str, str]]], limit: int = 6) -> str:
    items = history["commits"][:limit]
    return "\n".join(
        f"- **{item['project']}** · [{item['title']}]({item['url']}) · "
        f"{item['occurred_at'][:10]}"
        for item in items
    )


def recent_collaboration(
    history: dict[str, list[dict[str, str]]], limit: int = 6
) -> str:
    items = history["pull_requests"][:limit]
    if not items:
        return "현재 공개된 merged PR 기록 없음"
    return "\n".join(
        f"- **{item['repository']}** · [{item['title']}]({item['url']}) · "
        f"{item['occurred_at'][:10]}"
        for item in items
    )


def replace_section(source: str, key: str, replacement: str) -> str:
    start, end = MARKERS[key]
    pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    updated, count = pattern.subn(f"{start}\n{replacement}\n{end}", source)
    if count != 1:
        raise RuntimeError(f"README marker must appear exactly once: {key}")
    return updated


def write_if_changed(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--readme", type=Path, required=True)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN", "")
    profile = discover_profile(args.login, token)
    repositories = discover_repositories(args.login, token)
    snapshots = collect_snapshots(repositories, token)
    history = merge_history(
        args.history,
        collect_commits(snapshots, args.login),
        collect_merged_prs(args.login, token),
    )

    readme = args.readme.read_text(encoding="utf-8")
    readme = replace_section(readme, "intro", render_intro(profile))
    readme = replace_section(readme, "cards", render_cards(repositories))
    readme = replace_section(readme, "ci", render_ci(snapshots))
    readme = replace_section(readme, "collaboration", recent_collaboration(history))
    readme = replace_section(readme, "recent", recent_commits(history))
    readme = replace_section(
        readme, "technologies", render_technologies(repositories, snapshots)
    )
    write_cards(repositories, args.readme.parent / "assets" / "generated")
    write_if_changed(args.readme, readme)
    write_if_changed(
        args.history,
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
    )


if __name__ == "__main__":
    main()
