import os
import unittest

import aether_routes
from tools import build_aether_routes


class RouteLibraryTests(unittest.TestCase):
    def test_fixed_routes_cover_a_full_episode(self):
        self.assertEqual(len(aether_routes.RNGRNG_P0), 719)
        self.assertEqual(len(aether_routes.MTN_P1), 719)

    def test_route_provenance_is_recorded(self):
        self.assertEqual(
            aether_routes.METADATA["seat0_source"],
            "exact RngRng public episode 104686146, seat 0",
        )
        self.assertEqual(
            aether_routes.METADATA["seat1_source"],
            "exact MtN public episode 104683334, seat 1",
        )
        self.assertEqual(aether_routes.METADATA["seat0_submission_id"], 55948382)
        self.assertEqual(aether_routes.METADATA["seat1_submission_id"], 55947910)
        self.assertEqual(aether_routes.METADATA["steps"], 719)

    def test_generated_route_library_is_reproducible(self):
        p0_corpus = os.path.join(
            build_aether_routes.CLIMBER_CORPUS, "RngRng", "manifest.json"
        )
        p1_corpus = os.path.join(
            build_aether_routes.CONSISTENT_CORPUS, "MtN", "manifest.json"
        )
        if not os.path.exists(p0_corpus) or not os.path.exists(p1_corpus):
            self.skipTest("public replay corpus is intentionally gitignored")
        generated = build_aether_routes.build_source()
        self.assertIn("RNGRNG_P0 = _decode", generated)
        self.assertIn("MTN_P1 = _decode", generated)
        self.assertIn("exact MtN public episode 104683334, seat 1", generated)


if __name__ == "__main__":
    unittest.main()
