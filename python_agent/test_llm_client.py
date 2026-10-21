import json
import unittest
from unittest.mock import patch

from llm_client import GroqClient, GroqClientError, GroqSettings


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class GroqClientTests(unittest.TestCase):
    @patch("llm_client.urlopen")
    def test_complete_returns_message_content(self, urlopen):
        urlopen.return_value = FakeResponse(
            {"choices": [{"message": {"content": " smoke test passed. "}}]}
        )

        result = GroqClient(
            "test-key",
            GroqSettings(endpoint="https://example.test", model="test-model"),
        ).complete("Say hello")

        self.assertEqual(result, "smoke test passed.")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(
            json.loads(request.data.decode("utf-8"))["model"], "test-model"
        )

    def test_empty_key_is_rejected(self):
        with self.assertRaisesRegex(GroqClientError, "missing or empty"):
            GroqClient(" ")

    def test_empty_prompt_is_rejected(self):
        with self.assertRaisesRegex(GroqClientError, "must not be empty"):
            GroqClient("test-key").complete(" ")


if __name__ == "__main__":
    unittest.main()
