#!/usr/bin/env python3
"""Append an auditable public-repository language summary to a metrics SVG."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path


DEFAULT_REPOSITORIES = (
    "woonyong-kr/k8s-ops",
    "woonyong-kr/minidb",
    "woonyong-kr/pintos",
    "woonyong-kr/dx_framework",
)

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "C++": "#f34b7d",
    "C#": "#178600",
    "C": "#555555",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Perl": "#0298c3",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Makefile": "#427819",
    "Assembly": "#6E4C13",
    "Dockerfile": "#384d54",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def repositories_from_env() -> tuple[str, ...]:
    configured = os.getenv("PROFILE_REPOSITORIES", "")
    if not configured.strip():
        return DEFAULT_REPOSITORIES
    return tuple(item.strip() for item in configured.split(",") if item.strip())


def fetch_languages(repository: str, token: str | None) -> dict[str, int]:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/languages",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "woonyong-profile-metrics",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError(f"Unexpected languages response for {repository}")
    return {str(language): int(size) for language, size in payload.items()}


def format_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    number = float(value)
    for unit in units:
        if number < 1024 or unit == units[-1]:
            return f"{number:.1f} {unit}" if unit != "B" else f"{int(number)} B"
        number /= 1024
    raise AssertionError("unreachable")


def build_section(languages: Counter[str], repositories: tuple[str, ...]) -> str:
    total = sum(languages.values())
    if total <= 0:
        raise ValueError("No language bytes returned from GitHub")

    ranked = languages.most_common(8)
    widths = [(language, size, size / total * 100) for language, size in ranked]

    cursor = 0.0
    bars: list[str] = []
    labels: list[str] = []
    for language, size, percentage in widths:
        color = LANGUAGE_COLORS.get(language, "#8b949e")
        width = 920 * percentage / 100
        bars.append(
            f'<rect x="{cursor:.2f}" y="0" width="{width:.2f}" height="10" '
            f'fill="{color}" mask="url(#portfolio-language-mask)"/>'
        )
        cursor += width
        labels.append(
            '<div style="display:flex;align-items:center;gap:7px;width:23%;min-width:180px;">'
            f'<span style="width:10px;height:10px;border-radius:50%;background:{color};"></span>'
            f'<span>{html.escape(language)}</span>'
            f'<small style="margin-left:auto;">{percentage:.1f}%</small>'
            '</div>'
        )

    repository_links = " · ".join(
        f'<a href="https://github.com/{html.escape(repository)}">{html.escape(repository.split("/", 1)[1])}</a>'
        for repository in repositories
    )
    return f"""
            <section id="portfolio-languages" style="margin-top:12px;">
                <h2 style="margin:0 5px 5px;color:#0366d6;font-size:16px;font-weight:400;">대표 저장소 언어 비중</h2>
                <small style="display:block;margin:0 5px 8px;">GitHub Linguist · 공개 저장소 {len(repositories)}개 · {format_bytes(total)}</small>
                <svg xmlns="http://www.w3.org/2000/svg" width="920" height="10" style="margin:3px 8px 9px;">
                    <mask id="portfolio-language-mask"><rect width="920" height="10" rx="5" fill="white"/></mask>
                    {''.join(bars)}
                </svg>
                <div style="display:flex;flex-wrap:wrap;gap:5px 2%;margin:0 8px 7px;">{''.join(labels)}</div>
                <small style="display:block;margin:0 8px;">{repository_links}</small>
            </section>"""


def append_section(svg: str, section: str) -> str:
    marker = '        </div>\n        <div xmlns="http://www.w3.org/1999/xhtml" id="metrics-end"></div>'
    if marker not in svg:
        raise ValueError("Could not find metrics content boundary")
    svg = svg.replace(marker, f"{section}\n{marker}", 1)

    height_pattern = re.compile(r'(<svg[^>]+height=")(\d+)("[^>]*>)', re.DOTALL)
    match = height_pattern.search(svg)
    if not match:
        raise ValueError("Could not find SVG height")
    height = int(match.group(2)) + 145
    return height_pattern.sub(rf"\g<1>{height}\g<3>", svg, count=1)


def main() -> None:
    args = parse_args()
    repositories = repositories_from_env()
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    languages: Counter[str] = Counter()
    for repository in repositories:
        languages.update(fetch_languages(repository, token))

    base_svg = args.input.read_text(encoding="utf-8")
    rendered = append_section(base_svg, build_section(languages, repositories))
    args.output.write_text(rendered, encoding="utf-8")
    summary = ", ".join(f"{name}={size}" for name, size in languages.most_common())
    print(f"repositories={len(repositories)} total={sum(languages.values())} {summary}")


if __name__ == "__main__":
    main()
