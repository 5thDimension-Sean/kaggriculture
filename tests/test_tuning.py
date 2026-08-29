import unittest

import main
from tuning import space
from tuning.build_candidate import make_agent, validate_vector


class TuningSpaceTests(unittest.TestCase):
    def test_compact_space_stays_compact(self):
        self.assertEqual(space.DIM, 16)
        self.assertEqual(space.DIM, len(space.NAMES))

    def test_default_round_trip(self):
        default = space.default_vector()
        restored = space.from_normalized(space.to_normalized(default))
        for expected, actual in zip(default, restored):
            self.assertAlmostEqual(expected, actual)

    def test_default_config_matches_main(self):
        base, heuristics = space.vector_to_config(space.default_vector())
        self.assertEqual(base, main._BAKED_BASE_PARAMS)
        self.assertEqual(heuristics, main._BAKED_OVERLAY_PARAMS)

    def test_invalid_vector_rejected(self):
        invalid = space.default_vector()
        invalid[0] = space.LOWS[0] - 1
        with self.assertRaises(ValueError):
            validate_vector(invalid)

    def test_candidate_modules_are_isolated(self):
        first = make_agent(space.default_vector())
        second = make_agent(space.default_vector())
        first_heuristics = first.__globals__["heuristics"]
        second_heuristics = second.__globals__["heuristics"]
        self.assertIsNot(first_heuristics, second_heuristics)


if __name__ == "__main__":
    unittest.main()
