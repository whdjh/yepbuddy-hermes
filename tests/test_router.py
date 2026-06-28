import json
import tempfile
import unittest
from pathlib import Path

from termux_telegram_assistant.plugins.stubs import default_plugins
from termux_telegram_assistant.router import TopicRouter


class TopicRouterTest(unittest.TestCase):
    def test_router_loads_topic_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            routes_path = Path(tmp) / "topic_routes.json"
            routes_path.write_text(
                json.dumps(
                    {
                        "default_role": "ops_log",
                        "routes": {
                            "111": "app_promo",
                            "222": "health_research",
                        },
                    }
                ),
                encoding="utf-8",
            )

            router = TopicRouter.from_file(routes_path, default_plugins())

            self.assertEqual(router.resolve(111).role, "app_promo")
            self.assertEqual(router.resolve(222).role, "health_research")
            self.assertEqual(router.resolve(999).role, "ops_log")

    def test_router_missing_file_has_no_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            router = TopicRouter.from_file(Path(tmp) / "missing.json", default_plugins())

            self.assertIsNone(router.resolve(111))


if __name__ == "__main__":
    unittest.main()
