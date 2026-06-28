import json
import tempfile
import unittest
from pathlib import Path

from hermes.storage import JsonlStore


class JsonlStoreTest(unittest.TestCase):
    def test_jsonl_store_appends_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            store = JsonlStore(tmp_path)

            store.append("events", {"role": "ops_log", "text": "hello"})

            line = (tmp_path / "events.jsonl").read_text(encoding="utf-8").strip()
            record = json.loads(line)
            self.assertEqual(record["role"], "ops_log")
            self.assertEqual(record["text"], "hello")
            self.assertIn("created_at", record)


if __name__ == "__main__":
    unittest.main()
