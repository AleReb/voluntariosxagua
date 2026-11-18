import io
import json
import unittest

from fetch_kobo_data import ASSET, SERVER, download


class FakeOpener:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        return io.StringIO(json.dumps(next(self.pages)))


class DownloadTests(unittest.TestCase):
    def test_collects_every_page_with_authentication(self):
        opener = FakeOpener([
            {"results": [{"_id": 1}], "next": f"{SERVER}/api/v2/assets/{ASSET}/data/?start=1"},
            {"results": [{"_id": 2}], "next": None},
        ])
        self.assertEqual(download("test-token", opener), [{"_id": 1}, {"_id": 2}])
        self.assertEqual(len(opener.requests), 2)
        for request in opener.requests:
            self.assertEqual(request.get_header("Authorization"), "Token test-token")

    def test_does_not_send_token_to_another_host(self):
        opener = FakeOpener([{"results": [], "next": "https://example.com/data/"}])
        with self.assertRaises(ValueError):
            download("test-token", opener)
        self.assertEqual(len(opener.requests), 1)

    def test_repeated_page_fails_instead_of_looping(self):
        url = f"{SERVER}/api/v2/assets/{ASSET}/data/?format=json&limit=1000"
        opener = FakeOpener([{"results": [], "next": url}])
        with self.assertRaises(ValueError):
            download("test-token", opener)

    def test_malformed_response_fails_instead_of_saving_empty_data(self):
        with self.assertRaises(ValueError):
            download("test-token", FakeOpener([{"detail": "error"}]))


if __name__ == "__main__":
    unittest.main()
