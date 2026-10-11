import argparse
import unittest

from study_book.ingest import instagram_url


class InstagramUrlTest(unittest.TestCase):
    def test_accepts_instagram_and_rejects_other_hosts(self) -> None:
        url = "https://www.instagram.com/reel/example/"
        self.assertEqual(instagram_url(url), url)
        with self.assertRaises(argparse.ArgumentTypeError):
            instagram_url("https://example.com/video")


if __name__ == "__main__":
    unittest.main()
