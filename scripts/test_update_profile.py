import unittest

from update_profile import decode_javascript_string, parse_blog_posts


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


if __name__ == "__main__":
    unittest.main()
