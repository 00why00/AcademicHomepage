import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from google_scholar_crawler.main import collect_author, normalize_author, write_json_atomic

AUTHOR = {"name": "Test Author", "citedby": 4, "publications": [
    {"author_pub_id": "author:paper", "num_citations": 4, "bib": {"title": "Test paper"}}
]}


class CrawlerTests(unittest.TestCase):
    def test_retries_stop_and_do_not_sleep_after_last_failure(self):
        fetch = Mock(side_effect=TimeoutError("offline"))
        sleep = Mock()
        with self.assertRaisesRegex(RuntimeError, "All 3"):
            collect_author("author", attempts=3, wait_seconds=2, fetch=fetch, sleep=sleep)
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_partial_response_is_retried_before_publishing(self):
        fetch = Mock(side_effect=[{"name": "Test Author"}, copy.deepcopy(AUTHOR)])
        result = collect_author("author", fetch=fetch, sleep=Mock())
        self.assertIn("author:paper", result["publications"])
        self.assertTrue(result["updated"].endswith("+00:00"))

    def test_invalid_counts_and_empty_or_mismatched_publications_fail(self):
        for patch in [{"citedby": -1}, {"citedby": True}, {"publications": []},
                      {"publications": [{"author_pub_id": "other:paper", "num_citations": 1}]}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                normalize_author({**copy.deepcopy(AUTHOR), **patch}, "author")

    def test_failed_refresh_preserves_existing_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gs_data.json"
            path.write_text('{"citedby": 4}')
            with self.assertRaises(RuntimeError):
                data = collect_author("author", attempts=1, fetch=Mock(side_effect=ValueError("bad")), sleep=Mock())
                write_json_atomic(path, data)
            self.assertEqual(json.loads(path.read_text()), {"citedby": 4})

    def test_successful_snapshot_is_complete_and_atomic(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gs_data.json"
            write_json_atomic(path, normalize_author(copy.deepcopy(AUTHOR), "author"))
            self.assertEqual(json.loads(path.read_text())["publications"]["author:paper"]["num_citations"], 4)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
