#!/usr/bin/env python3
"""Build a GitHub profile from verified public repositories and activity."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    "activity": ("<!-- activity_summary:start -->", "<!-- activity_summary:end -->"),
    "cards": ("<!-- project_cards:start -->", "<!-- project_cards:end -->"),
    "blog": ("<!-- recent_posts:start -->", "<!-- recent_posts:end -->"),
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
    license_id: str
    primary_language: str
    topics: tuple[str, ...]
    default_branch: str
    pushed_at: str


@dataclass(frozen=True)
class RepositorySnapshot:
    repository: Repository
    commits: list[dict[str, object]]
    workflow: dict[str, object] | None
    workflow_conclusion: str
    readme_size: int
    test_files: int
    documentation_files: int


@dataclass(frozen=True)
class RepositoryEvaluation:
    snapshot: RepositorySnapshot
    score: int
    authored_commits: int
    signals: tuple[str, ...]


@dataclass(frozen=True)
class Profile:
    name: str
    login: str
    bio: str
    blog: str
    email: str
    url: str


@dataclass(frozen=True)
class ActivitySummary:
    from_date: str
    to_date: str
    total_contributions: int
    commit_contributions: int
    pull_requests: int
    issues: int
    reviews: int
    restricted_contributions: int
    repositories: int


@dataclass(frozen=True)
class BlogPost:
    slug: str
    name: str
    subtitle: str
    published_at: str
    order: int
    tags: tuple[str, ...]


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


def public_text_request(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "woonyong-profile-index"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Public content {error.code}: {detail}") from error


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
      licenseInfo { spdxId }
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
            license_id=str((node.get("licenseInfo") or {}).get("spdxId") or "—"),
            primary_language=str(language),
            topics=topics,
            default_branch=str(branch),
            pushed_at=str(node["pushedAt"]),
        )

    def eligible(repository: Repository) -> bool:
        return (
            not repository.is_fork
            and not repository.is_archived
            and "profile-exclude" not in repository.topics
            and repository.name_with_owner != f"{login}/{login}"
        )

    return [
        repository
        for repository in map(parse, user["repositories"]["nodes"])
        if eligible(repository)
    ]


def discover_activity(login: str, token: str) -> ActivitySummary:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar { totalContributions }
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          restrictedContributionsCount
          commitContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner }
          }
          issueContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner }
          }
          pullRequestContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner }
          }
          pullRequestReviewContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner }
          }
        }
      }
    }
    """
    response = github_request(
        "https://api.github.com/graphql",
        token,
        payload={
            "query": query,
            "variables": {
                "login": login,
                "from": start.isoformat(),
                "to": now.isoformat(),
            },
        },
    )
    if not isinstance(response, dict) or response.get("errors"):
        raise RuntimeError(f"GitHub contribution query failed: {response}")
    collection = response.get("data", {}).get("user", {}).get("contributionsCollection")
    if not collection:
        raise RuntimeError("GitHub contribution summary is empty")
    repository_names: set[str] = set()
    for key in (
        "commitContributionsByRepository",
        "issueContributionsByRepository",
        "pullRequestContributionsByRepository",
        "pullRequestReviewContributionsByRepository",
    ):
        repository_names.update(
            item["repository"]["nameWithOwner"] for item in collection.get(key, [])
        )
    return ActivitySummary(
        from_date=start.date().isoformat(),
        to_date=now.date().isoformat(),
        total_contributions=int(collection["contributionCalendar"]["totalContributions"]),
        commit_contributions=int(collection["totalCommitContributions"]),
        pull_requests=int(collection["totalPullRequestContributions"]),
        issues=int(collection["totalIssueContributions"]),
        reviews=int(collection["totalPullRequestReviewContributions"]),
        restricted_contributions=int(collection["restrictedContributionsCount"]),
        repositories=len(repository_names),
    )


def discover_blog_posts(login: str) -> list[BlogPost]:
    base_url = (
        "https://raw.githubusercontent.com/"
        f"{login}/{login}.github.io/main/"
    )
    manifest = json.loads(public_text_request(f"{base_url}asset-manifest.json"))
    main_path = str(manifest.get("files", {}).get("main.js") or "").removeprefix(
        "./"
    )
    if not main_path:
        raise RuntimeError("Published blog JavaScript entrypoint is missing")
    bundle = public_text_request(f"{base_url}{main_path}")
    js_string = r'(?:"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
    pattern = re.compile(
        r'\{type:"post",slug:(?P<slug>'
        + js_string
        + r"),name:(?P<name>"
        + js_string
        + r").*?,subtitle:(?P<subtitle>"
        + js_string
        + r").*?,date:(?P<date>"
        + js_string
        + r"),tags:\[(?P<tags>.*?)\]\}",
        re.S,
    )
    posts: list[BlogPost] = []
    for order, match in enumerate(pattern.finditer(bundle)):
        decode = ast.literal_eval
        published_at = str(decode(match.group("date")))
        posts.append(
            BlogPost(
                slug=str(decode(match.group("slug"))),
                name=str(decode(match.group("name"))),
                subtitle=str(decode(match.group("subtitle"))),
                published_at=published_at,
                order=order,
                tags=tuple(
                    str(decode(item.group(0)))
                    for item in re.finditer(js_string, match.group("tags"))
                ),
            )
        )
    if not posts:
        raise RuntimeError("Published blog posts were not found")
    return sorted(
        posts,
        key=lambda post: (post.published_at, post.order, post.slug),
        reverse=True,
    )[:6]


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
        if not isinstance(commits, list):
            raise RuntimeError(f"Commit history lookup failed: {repository.name_with_owner}")
        if not commits:
            continue
        tree_response = github_request(
            f"https://api.github.com/repos/{repository.name_with_owner}/git/trees/"
            f"{urllib.parse.quote(repository.default_branch)}?recursive=1",
            token,
        )
        tree = tree_response.get("tree", []) if isinstance(tree_response, dict) else []
        files = [
            item
            for item in tree
            if item.get("type") == "blob" and isinstance(item.get("path"), str)
        ]
        readme_size = max(
            (
                int(item.get("size") or 0)
                for item in files
                if re.fullmatch(r"readme(?:\.[a-z0-9]+)?", str(item["path"]), re.I)
            ),
            default=0,
        )
        excluded_parts = {"node_modules", "vendor", "third_party", "dist", "build"}

        def project_file(item: dict[str, object]) -> bool:
            parts = set(str(item["path"]).lower().split("/"))
            return not parts.intersection(excluded_parts)

        test_files = sum(
            1
            for item in files
            if project_file(item)
            and (
                set(str(item["path"]).lower().split("/")).intersection(
                    {"test", "tests", "spec", "specs", "eval", "evals"}
                )
                or re.search(
                    r"(?:^|[._-])(test|spec)(?:[._-]|$)",
                    Path(str(item["path"])).name.lower(),
                )
            )
        )
        documentation_files = sum(
            1
            for item in files
            if project_file(item)
            and (
                str(item["path"]).lower().startswith("docs/")
                or Path(str(item["path"])).suffix.lower() in {".md", ".mdx"}
            )
        )
        response = github_request(
            f"https://api.github.com/repos/{repository.name_with_owner}/actions/workflows?per_page=100",
            token,
        )
        workflows = response.get("workflows", []) if isinstance(response, dict) else []
        workflow = select_workflow(workflows)
        conclusion = ""
        if workflow is not None:
            runs = github_request(
                f"https://api.github.com/repos/{repository.name_with_owner}/actions/"
                f"workflows/{workflow['id']}/runs?branch="
                f"{urllib.parse.quote(repository.default_branch)}&status=completed&per_page=1",
                token,
            )
            workflow_runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
            if workflow_runs:
                conclusion = str(workflow_runs[0].get("conclusion") or "")
        snapshots.append(
            RepositorySnapshot(
                repository,
                commits,
                workflow,
                conclusion,
                readme_size,
                test_files,
                documentation_files,
            )
        )
    return snapshots


def authored_commits(
    snapshot: RepositorySnapshot, login: str
) -> list[dict[str, object]]:
    return [
        commit
        for commit in snapshot.commits
        if human_commit(commit)
        and (commit.get("author") or {}).get("login") == login
    ]


def evaluate_repository(
    snapshot: RepositorySnapshot, login: str, now: datetime
) -> RepositoryEvaluation | None:
    repository = snapshot.repository
    authored = authored_commits(snapshot, login)
    if not authored or not repository.description.strip() or snapshot.readme_size <= 0:
        return None

    score = min(25, 5 + len(authored) * 2)
    signals = [f"본인 커밋 {len(authored)}"]

    if snapshot.workflow_conclusion == "success":
        score += 25
        signals.append("CI 성공")
    elif snapshot.workflow is not None:
        score += 5
        signals.append("CI 구성")

    test_score = min(15, snapshot.test_files * 3)
    score += test_score
    if snapshot.test_files:
        signals.append(f"테스트 파일 {snapshot.test_files}")

    if snapshot.readme_size >= 5_000:
        score += 7
    elif snapshot.readme_size >= 1_000:
        score += 5
    else:
        score += 3
    score += min(3, snapshot.documentation_files)

    latest_authored = datetime.fromisoformat(
        str(authored[0]["commit"]["author"]["date"]).replace("Z", "+00:00")
    )
    age_days = max(0, (now - latest_authored).days)
    if age_days <= 30:
        score += 10
    elif age_days <= 90:
        score += 7
    elif age_days <= 365:
        score += 4
    signals.append(f"최근 변경 {latest_authored.date().isoformat()}")

    score += 3
    score += min(4, len(repository.topics))
    if repository.license_id != "—":
        score += 3
        signals.append(repository.license_id)
    score += min(5, repository.stargazer_count + repository.fork_count * 2)

    return RepositoryEvaluation(snapshot, score, len(authored), tuple(signals))


def select_featured(
    snapshots: list[RepositorySnapshot], login: str
) -> list[RepositoryEvaluation]:
    now = datetime.now(timezone.utc)
    evaluated = [
        evaluation
        for snapshot in snapshots
        if (evaluation := evaluate_repository(snapshot, login, now)) is not None
    ]
    selected = sorted(
        evaluated,
        key=lambda evaluation: (
            evaluation.score,
            evaluation.snapshot.repository.pushed_at,
            evaluation.snapshot.repository.name.lower(),
        ),
        reverse=True,
    )[:6]
    if len(selected) != 6:
        raise RuntimeError("Six repositories did not pass the automatic evidence gate")
    return selected


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
    eligible_repositories: set[str],
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
            items = (
                item
                for item in items
                if meaningful_subject(item["title"])
                and item["repository"] in eligible_repositories
            )
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


def render_card_svg(evaluation: RepositoryEvaluation) -> str:
    snapshot = evaluation.snapshot
    repository = snapshot.repository
    description = repository.description.strip() or "설명 없음"
    description_lines = textwrap.wrap(
        description, width=48, break_long_words=False, break_on_hyphens=False
    )[:2]
    while len(description_lines) < 2:
        description_lines.append("")
    language = repository.primary_language or "Unknown"
    language_color = LANGUAGE_COLORS.get(language, "#8b949e")
    if snapshot.workflow_conclusion == "success":
        ci_label = "CI pass"
    elif snapshot.workflow is not None:
        ci_label = "CI configured"
    else:
        ci_label = "No CI"
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
  <text class="meta" x="112" y="105">{ci_label}</text>
  <text class="meta" x="188" y="105">Test files {snapshot.test_files}</text>
  <text class="meta" x="282" y="105">Updated {repository.pushed_at[:10]}</text>
</svg>
'''


def write_cards(
    evaluations: list[RepositoryEvaluation], directory: Path
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    expected = {
        card_filename(evaluation.snapshot.repository) for evaluation in evaluations
    }
    for existing in directory.glob("repo-*.svg"):
        if existing.name not in expected:
            existing.unlink()
    for evaluation in evaluations:
        repository = evaluation.snapshot.repository
        write_if_changed(
            directory / card_filename(repository), render_card_svg(evaluation)
        )


def render_intro(profile: Profile) -> str:
    lines = [f"# {profile.name}", ""]
    if profile.bio:
        lines.append(f"**{profile.bio}**")
        lines.append("")
    links: list[str] = []
    if profile.blog:
        blog = profile.blog if "://" in profile.blog else f"https://{profile.blog}"
        links.append(f"[블로그]({blog})")
    if profile.email:
        links.append(f"[이메일](mailto:{profile.email})")
    if links:
        lines.append(" · ".join(links))
    return "\n".join(lines)


def shields_segment(value: str) -> str:
    return urllib.parse.quote(value.replace("-", "--").replace("_", "__").replace(" ", "_"))


def render_activity(
    activity: ActivitySummary,
    featured_snapshots: list[RepositorySnapshot],
    profile: Profile,
) -> str:
    verified = [snapshot for snapshot in featured_snapshots if snapshot.workflow_conclusion]
    passing = sum(snapshot.workflow_conclusion == "success" for snapshot in verified)
    metrics = [
        ("Contributions", f"{activity.total_contributions:,}", "0969DA"),
        ("Commits", f"{activity.commit_contributions:,}", "238636"),
        ("Pull Requests", f"{activity.pull_requests:,}", "8250DF"),
        ("Issues", f"{activity.issues:,}", "D29922"),
        ("Reviews", f"{activity.reviews:,}", "1F6FEB"),
        ("Repositories", f"{activity.repositories:,}", "57606A"),
    ]
    if verified:
        color = "238636" if passing == len(verified) else "D29922"
        metrics.append(("CI", f"{passing}/{len(verified)} passing", color))
    contribution_url = (
        f"{profile.url}?tab=overview&from={activity.from_date}&to={activity.to_date}"
    )
    badges = []
    for label, value, color in metrics:
        source = (
            "https://img.shields.io/badge/"
            f"{shields_segment(label)}-{shields_segment(value)}-{color}?style=flat-square"
        )
        badges.append(
            f'<a href="{contribution_url}"><img alt="{label} {value}" src="{source}"></a>'
        )
    return "\n".join(badges)


def render_cards(evaluations: list[RepositoryEvaluation]) -> str:
    lines = [
        "<sub>자동 선발 · 공개 증거 순위: 본인 커밋 25 · CI 25 · 테스트 구조 15 · 문서 10 · 최근 유지보수 10 · 메타데이터 10 · 공개 반응 5</sub>",
        "",
        '<p align="center">',
    ]
    for index, evaluation in enumerate(evaluations):
        repository = evaluation.snapshot.repository
        lines.append(
            f'  <a href="{repository.url}"><img width="410" '
            f'src="assets/generated/{card_filename(repository)}" '
            f'alt="{repository.name} 저장소"></a>'
        )
        if index in {1, 3}:
            lines.append("  <br>")
    lines.append("</p>")
    return "\n".join(lines)


def escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_blog(posts: list[BlogPost]) -> str:
    rows: list[str] = []
    for post in posts:
        url = (
            "https://woonyong-kr.github.io/#/posts/"
            f"{urllib.parse.quote(post.slug)}"
        )
        tags = " · ".join(escape_table(tag) for tag in post.tags) or "기록"
        row = (
            f'- <span lang="ko">**{tags}** · '
            f"[{escape_table(post.name)}]({url}) · {post.published_at}"
        )
        if post.subtitle:
            row += f"<br><sub>{escape_table(post.subtitle)}</sub>"
        rows.append(f"{row}</span>")
    return "\n".join(rows)


def render_ci(snapshots: list[RepositorySnapshot]) -> str:
    rows = [
        '<table width="100%">',
        "  <thead>",
        "    <tr>",
        '      <th align="left" width="34%">저장소</th>',
        '      <th align="left" width="30%">CI</th>',
        '      <th align="right" width="18%">테스트 파일</th>',
        '      <th align="right" width="18%">라이선스</th>',
        "    </tr>",
        "  </thead>",
        "  <tbody>",
    ]
    for snapshot in snapshots:
        workflow = snapshot.workflow
        repository = snapshot.repository
        ci = "—"
        if workflow is not None:
            path = str(workflow["path"])
            path_url = urllib.parse.quote(path.rsplit("/", 1)[-1], safe="")
            badge = (
                f"https://github.com/{repository.name_with_owner}/actions/workflows/"
                f"{path_url}/badge.svg?branch={urllib.parse.quote(repository.default_branch)}"
            )
            actions = f"https://github.com/{repository.name_with_owner}/actions"
            ci = (
                f'<a href="{actions}"><img alt="{escape(repository.name)} CI" '
                f'src="{badge}"></a>'
            )
        rows.extend(
            [
                "    <tr>",
                f'      <td><a href="{repository.url}">{escape(repository.name)}</a></td>',
                f"      <td>{ci}</td>",
                f'      <td align="right">{snapshot.test_files}</td>',
                f'      <td align="right">{escape(repository.license_id)}</td>',
                "    </tr>",
            ]
        )
    rows.extend(["  </tbody>", "</table>"])
    return "\n".join(rows)


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
        f"- <span lang=\"ko\">**{item['project']}** · "
        f"[{item['title']}]({item['url']}) · {item['occurred_at'][:10]}</span>"
        for item in items
    )


def recent_collaboration(
    history: dict[str, list[dict[str, str]]], limit: int = 6
) -> str:
    items = history["pull_requests"][:limit]
    if not items:
        return "현재 공개된 merged PR 기록 없음"
    return "\n".join(
        f"- <span lang=\"ko\">**{item['repository']}** · "
        f"[{item['title']}]({item['url']}) · {item['occurred_at'][:10]}</span>"
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
    activity = discover_activity(args.login, token)
    blog_posts = discover_blog_posts(args.login)
    public_repositories = discover_repositories(args.login, token)
    snapshots = collect_snapshots(public_repositories, token)
    featured = select_featured(snapshots, args.login)
    featured_snapshots = [evaluation.snapshot for evaluation in featured]
    featured_repositories = [
        evaluation.snapshot.repository for evaluation in featured
    ]
    history = merge_history(
        args.history,
        collect_commits(snapshots, args.login),
        collect_merged_prs(args.login, token),
        {repository.name_with_owner for repository in public_repositories},
    )

    readme = args.readme.read_text(encoding="utf-8")
    readme = replace_section(readme, "intro", render_intro(profile))
    readme = replace_section(
        readme, "activity", render_activity(activity, featured_snapshots, profile)
    )
    readme = replace_section(readme, "cards", render_cards(featured))
    readme = replace_section(readme, "blog", render_blog(blog_posts))
    readme = replace_section(readme, "ci", render_ci(featured_snapshots))
    readme = replace_section(readme, "collaboration", recent_collaboration(history))
    readme = replace_section(readme, "recent", recent_commits(history))
    readme = replace_section(
        readme,
        "technologies",
        render_technologies(featured_repositories, featured_snapshots),
    )
    write_cards(featured, args.readme.parent / "assets" / "generated")
    write_if_changed(args.readme, readme)
    write_if_changed(
        args.history,
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
    )


if __name__ == "__main__":
    main()
