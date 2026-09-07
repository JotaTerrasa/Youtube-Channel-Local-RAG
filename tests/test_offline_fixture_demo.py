import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO_PATH = ROOT / "scripts" / "offline_fixture_demo.py"


def _load_demo_module():
    spec = importlib.util.spec_from_file_location("offline_fixture_demo", DEMO_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OfflineFixtureDemoTests(unittest.TestCase):
    def test_demo_exercises_the_cached_pipeline_without_external_services(self):
        output = _load_demo_module().render_demo()

        self.assertIn("Cached pipeline result: cached; chunks passed to the adapter: 1.", output)
        self.assertIn("External services used: none", output)
        self.assertIn("https://example.invalid/youtube-rag-offline-fixture?t=0s", output)


if __name__ == "__main__":
    unittest.main()
