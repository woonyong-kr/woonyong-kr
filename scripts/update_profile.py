#!/usr/bin/env python3
"""Accumulate public GitHub activity and refresh profile README indexes."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request


BOT_LOGINS = {"dependabot[bot]", "github-actions[bot]"}
SKIP_SUBJECT_PREFIXES = ("chore:", "ci:", "docs:", "merge ")
MARKERS = {
    "health": ("<!-- repository_health:start -->", "<!-- repository_health:end -->"),
    "collaboration": ("<!-- collaboration:start -->", "<!-- collaboration:end -->"),
    "recent": ("<!-- recent_work:start -->", "<!-- recent_work:end -->"),
}


@dataclass(frozen=True)
class Project:
    name: str
    repository: str
    workflow: str
    proof: str


def github_json(url: str, token: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "woonyong-profile-index",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {error.code}: {detail}") from error


def human_commit(commit: dict[str, object]) -> bool:
    author = commit.get("author") or {}
    subject = str(commit["commit"]["message"]).splitlines()[0].lower()
    return (
        author.get("login") not in BOT_LOGINS
        and not subject.startswith(SKIP_SUBJECT_PREFIXES)
    )


def collect_commits(
    projects: list[Project], login: str, token: str
) -> list[dict[str, str]]:
    collected: list[dict[str, str]] = []
    for project in projects:
        commits = github_json(
            f"https://api.github.com/repos/{project.repository}/commits?per_page=100",
            token,
        )
        if not isinstance(commits, list):
            raise RuntimeError(f"Unexpected commits response: {project.repository}")
        for commit in commits:
            author = commit.get("author") or {}
            if not human_commit(commit) or author.get("login") != login:
                continue
            metadata = commit["commit"]
            collected.append(
                {
                    "id": f"{project.repository}@{commit['sha']}",
                    "kind": "commit",
                    "project": project.name,
                    "repository": project.repository,
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
    response = github_json(f"https://api.github.com/search/issues?{query}", token)
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
    history_path: Path, commits: list[dict[str, str]], pull_requests: list[dict[str, str]]
) -> dict[str, list[dict[str, str]]]:
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"commits": [], "pull_requests": []}

    for key, incoming in (("commits", commits), ("pull_requests", pull_requests)):
        merged = {item["id"]: item for item in history.get(key, [])}
        merged.update({item["id"]: item for item in incoming})
        history[key] = sorted(
            merged.values(), key=lambda item: item["occurred_at"], reverse=True
        )[:1000]

    history_path.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return history


def repository_health(projects: list[Project], token: str) -> str:
    rows = ["| 저장소 | 상태 | 주 언어 | 검증 | 최근 변경 |", "|---|---|---|---|---|"]
    for project in projects:
        repository = github_json(
            f"https://api.github.com/repos/{project.repository}", token
        )
        commits = github_json(
            f"https://api.github.com/repos/{project.repository}/commits?per_page=30",
            token,
        )
        latest = next(commit for commit in commits if human_commit(commit))
        subject = str(latest["commit"]["message"]).splitlines()[0]
        badge = (
            f"[![{project.name} CI](https://github.com/{project.repository}/actions/"
            f"workflows/{project.workflow}/badge.svg?branch=main)](https://github.com/"
            f"{project.repository}/actions/workflows/{project.workflow})"
        )
        language = str(repository.get("language") or "-")
        rows.append(
            f"| [{project.name}](https://github.com/{project.repository}) | {badge} | "
            f"{language} | {project.proof} | [{subject}]({latest['html_url']}) |"
        )
    return "\n".join(rows)


def recent_commits(history: dict[str, list[dict[str, str]]], limit: int = 6) -> str:
    return "\n".join(
        f"- **{item['project']}** · [{item['title']}]({item['url']}) · "
        f"{item['occurred_at'][:10]}"
        for item in history["commits"][:limit]
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


def load_projects(path: Path) -> list[Project]:
    return [Project(**item) for item in json.loads(path.read_text(encoding="utf-8"))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", required=True)
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--readme", type=Path, required=True)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN", "")
    projects = load_projects(args.projects)
    history = merge_history(
        args.history,
        collect_commits(projects, args.login, token),
        collect_merged_prs(args.login, token),
    )

    readme = args.readme.read_text(encoding="utf-8")
    readme = replace_section(readme, "health", repository_health(projects, token))
    readme = replace_section(readme, "collaboration", recent_collaboration(history))
    readme = replace_section(readme, "recent", recent_commits(history))
    args.readme.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
