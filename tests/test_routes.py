import os
import unittest

import aether_routes
from tools import build_aether_routes


class RouteLibraryTests(unittest.TestCase):
    def test_all_routes_cover_a_full_episode(self):
        for name in (
            "P0_ANIMAL_PRESSURE",
            "P0_DAIRY_PRESSURE",
            "P0_CROP_PRESSURE",
            "P1_MTN_CONSENSUS",
        ):
            self.assertGreaterEqual(len(getattr(aether_routes, name)), 719)

    def test_mtn_consistency_gate_is_recorded(self):
        self.assertGreaterEqual(aether_routes.METADATA["seat1_consistency"], 0.99)

    def test_generated_route_library_is_reproducible(self):
        corpus = os.path.join(build_aether_routes.CORPUS, "MtN", "manifest.json")
        if not os.path.exists(corpus):
            self.skipTest("public replay corpus is intentionally gitignored")
        generated = build_aether_routes.build_source()
        self.assertIn("P1_MTN_CONSENSUS = _decode", generated)
        self.assertIn("seat1_consistency", generated)


if __name__ == "__main__":
    unittest.main()
