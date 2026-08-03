#!/usr/bin/env python3
"""Update the clickable recent-work index in the profile README."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request


START = "<!-- recent_work:start -->"
END = "<!-- recent_work:end -->"
BOT_LOGINS = {"dependabot[bot]", "github-actions[bot]"}
SKIP_SUBJECT_PREFIXES = ("chore:", "ci:", "docs:")


def github_json(url: str, token: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "woonyong-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {error.code}: {detail}") from error


def latest_human_commit(repository: str, token: str) -> dict[str, object]:
    commits = github_json(
        f"https://api.github.com/repos/{repository}/commits?per_page=10", token
    )
    if not isinstance(commits, list):
        raise RuntimeError(f"Unexpected commit response for {repository}")

    for commit in commits:
        author = commit.get("author") or {}
        subject = str(commit["commit"]["message"]).splitlines()[0].lower()
        if (
            author.get("login") not in BOT_LOGINS
            and not subject.startswith(SKIP_SUBJECT_PREFIXES)
        ):
            return commit
    raise RuntimeError(f"No human commit found for {repository}")


def recent_lines(projects: list[dict[str, str]], token: str) -> str:
    rows: list[tuple[str, str]] = []
    for project in projects:
        commit = latest_human_commit(project["repository"], token)
        metadata = commit["commit"]
        subject = str(metadata["message"]).splitlines()[0]
        date = str(metadata["author"]["date"])[:10]
        url = str(commit["html_url"])
        rows.append(
            (
                str(metadata["author"]["date"]),
                f"- **{project['name']}** · [{subject}]({url}) · {date}",
            )
        )
    return "\n".join(row for _, row in sorted(rows, reverse=True))


def update_readme(readme: Path, replacement: str) -> None:
    source = readme.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(START)}.*?{re.escape(END)}", flags=re.DOTALL
    )
    updated, count = pattern.subn(f"{START}\n{replacement}\n{END}", source)
    if count != 1:
        raise RuntimeError("README recent-work markers must appear exactly once")
    readme.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--readme", type=Path, required=True)
    args = parser.parse_args()

    projects = json.loads(args.projects.read_text(encoding="utf-8"))
    update_readme(
        args.readme,
        recent_lines(projects, os.environ.get("GH_TOKEN", "")),
    )


if __name__ == "__main__":
    main()
