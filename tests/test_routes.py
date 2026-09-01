import os
import unittest

import aether_routes
from tools import build_aether_routes


class RouteLibraryTests(unittest.TestCase):
    def test_fixed_route_covers_a_full_episode(self):
        self.assertEqual(len(aether_routes.TETSUYA_EP104466724_P1), 719)

    def test_route_provenance_is_recorded(self):
        self.assertEqual(
            aether_routes.METADATA["source"],
            "tetsuya episode 104466724 player 1",
        )
        self.assertEqual(aether_routes.METADATA["steps"], 719)

    def test_generated_route_library_is_reproducible(self):
        corpus = os.path.join(build_aether_routes.CORPUS, "tetsuya", "manifest.json")
        if not os.path.exists(corpus):
            self.skipTest("public replay corpus is intentionally gitignored")
        generated = build_aether_routes.build_source()
        self.assertIn("TETSUYA_EP104466724_P1 = _decode", generated)
        self.assertIn("tetsuya episode 104466724 player 1", generated)


if __name__ == "__main__":
    unittest.main()
