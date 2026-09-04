import unittest
from unittest.mock import patch

from update_profile import (
    GitHubApiError,
    Repository,
    collect_snapshots,
    decode_javascript_string,
    parse_blog_posts,
    parse_jekyll_blog_posts,
    render_blog,
)


class BlogDiscoveryTest(unittest.TestCase):
    def test_parses_vite_backtick_literals_and_ignores_following_fields(self) -> None:
        bundle = (
            "const posts=["
            "{type:`post`,slug:`first`,name:`첫 글`,description:`본문`,"
            "subtitle:`첫 설명`,date:`2026-08-02`,tags:[`AI`,`Python`],readingTime:2},"
            "{type:`post`,slug:`second`,name:`둘째 글`,description:`본문`,"
            "subtitle:`둘째 설명`,date:`2026-08-01`,tags:[`회고`],readingTime:1}];"
        )
        posts = parse_blog_posts(bundle)
        self.assertEqual([post.slug for post in posts], ["first", "second"])
        self.assertEqual(posts[0].tags, ("AI", "Python"))

    def test_decodes_backtick_escape_without_corrupting_korean(self) -> None:
        self.assertEqual(decode_javascript_string("`한글\\n테스트`"), "한글\n테스트")

    def test_parses_jekyll_archive(self) -> None:
        archive = """
        <h2 id="first"><a href="#first">#</a>
          <a href="/blog/first/">첫 글 &amp; 기록</a>
        </h2>
        <p>2026.08.02 · 프로젝트, Python</p>
        <p>첫 설명</p>
        <h2 id="second"><a href="#second">#</a>
          <a href="/blog/second/">둘째 글</a>
        </h2>
        <p>2026.08.01 · 회고</p>
        <p>둘째 설명</p>
        """
        posts = parse_jekyll_blog_posts(archive)
        self.assertEqual([post.slug for post in posts], ["first", "second"])
        self.assertEqual(posts[0].name, "첫 글 & 기록")
        self.assertEqual(posts[0].published_at, "2026-08-02")
        self.assertEqual(posts[0].tags, ("프로젝트", "Python"))
        rendered = render_blog(posts)
        self.assertIn("https://woonyong-kr.github.io/blog/first/", rendered)
        self.assertNotIn("#/posts/", rendered)

    def test_skips_empty_repository_commit_api_conflict(self) -> None:
        repository = Repository(
            name="empty",
            name_with_owner="woonyong-kr/empty",
            description="",
            url="https://github.com/woonyong-kr/empty",
            is_fork=False,
            is_archived=False,
            stargazer_count=0,
            fork_count=0,
            license_id="",
            primary_language="",
            topics=(),
            default_branch="main",
            pushed_at="",
        )
        with patch(
            "update_profile.github_request",
            side_effect=GitHubApiError(409, "Git Repository is empty."),
        ):
            self.assertEqual(collect_snapshots([repository], "token"), [])


if __name__ == "__main__":
    unittest.main()
