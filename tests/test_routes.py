import os
import unittest

import aether_routes
from tools import build_aether_routes


class RouteLibraryTests(unittest.TestCase):
    def test_fixed_routes_cover_a_full_episode(self):
        self.assertEqual(len(aether_routes.MTN_REFRESHED_P0), 719)
        self.assertEqual(len(aether_routes.MTN_REFRESHED_P1), 719)

    def test_route_provenance_is_recorded(self):
        self.assertEqual(
            aether_routes.METADATA["seat0_source"],
            "majority of refreshed MtN seat-0 public replays",
        )
        self.assertEqual(
            aether_routes.METADATA["seat1_source"],
            "majority of refreshed MtN seat-1 public replays",
        )
        self.assertEqual(aether_routes.METADATA["submission_id"], 55947910)
        self.assertEqual(aether_routes.METADATA["steps"], 719)

    def test_generated_route_library_is_reproducible(self):
        corpus = os.path.join(build_aether_routes.CORPUS, "MtN", "manifest.json")
        if not os.path.exists(corpus):
            self.skipTest("public replay corpus is intentionally gitignored")
        generated = build_aether_routes.build_source()
        self.assertIn("MTN_REFRESHED_P0 = _decode", generated)
        self.assertIn("MTN_REFRESHED_P1 = _decode", generated)
        self.assertIn("majority of refreshed MtN seat-1 public replays", generated)


if __name__ == "__main__":
    unittest.main()
