import os
import tempfile
import unittest

import main
from tools import benchmark, build_submission


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_67 = os.path.join(PROJECT_ROOT, "opponents", "mapleleaf_6_7.py")


class AgentTests(unittest.TestCase):
    def test_version_is_aether_1(self):
        self.assertEqual(main.__version__, "aether-1.0-route-fusion")

    def test_public_route_fingerprint(self):
        def observation(wool, milk):
            return {"market": {"inventory": {"WOOL": wool, "MILK": milk}}}

        self.assertEqual(main._public_route_mode(observation(9995, 9999)), "animal_pressure")
        self.assertEqual(main._public_route_mode(observation(9999, 9995)), "dairy_pressure")
        self.assertEqual(main._public_route_mode(observation(9999, 9999)), "crop_pressure")

    def test_generated_submission_loads_by_file_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, "main.py")
            with open(output, "w", encoding="utf-8") as handle:
                handle.write(build_submission.build_merged_source())
            build_submission.self_test(output)

    def test_full_episode_reaches_done(self):
        from kaggle_environments import make

        env = make(
            "kaggriculture",
            configuration={"episodeSteps": 720, "seed": 1_000_073},
            debug=True,
        )
        env.run([main.agent, benchmark.load_agent(REFERENCE_67)])
        self.assertTrue(all(player.status == "DONE" for player in env.steps[-1]))
        self.assertTrue(all(player.reward is not None for player in env.steps[-1]))


if __name__ == "__main__":
    unittest.main()
