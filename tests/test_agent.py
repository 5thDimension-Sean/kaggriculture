import os
import tempfile
import unittest

import main
from tools import benchmark, build_submission
from tuning import space
from tuning.build_candidate import make_agent, write_candidate


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_67 = os.path.join(PROJECT_ROOT, "opponents", "mapleleaf_6_7.py")


class AgentTests(unittest.TestCase):
    def test_version_is_7_2(self):
        self.assertEqual(main.__version__, "mapleleaf-7.2-heuristic-cma-lite")

    def test_default_candidate_matches_main(self):
        candidate = make_agent(space.default_vector())
        reference_a = benchmark.load_agent(REFERENCE_67)
        reference_b = benchmark.load_agent(REFERENCE_67)
        candidate_scores = benchmark.run_game(candidate, reference_a, 6_800_013)
        main_scores = benchmark.run_game(main.agent, reference_b, 6_800_013)
        self.assertEqual(candidate_scores, main_scores)

    def test_standalone_candidate_loads_by_file_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = write_candidate(space.default_vector(), os.path.join(directory, "main.py"))
            build_submission.self_test(output)

    def test_full_episode_reaches_done(self):
        from kaggle_environments import make

        env = make(
            "kaggriculture",
            configuration={"episodeSteps": 720, "seed": 6_800_068},
            debug=True,
        )
        env.run([main.agent, benchmark.load_agent(REFERENCE_67)])
        self.assertTrue(all(player.status == "DONE" for player in env.steps[-1]))
        self.assertTrue(all(player.reward is not None for player in env.steps[-1]))


if __name__ == "__main__":
    unittest.main()
