import os
import tempfile
import unittest

import main
from tools import benchmark, build_submission


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_67 = os.path.join(PROJECT_ROOT, "opponents", "mapleleaf_6_7.py")


class AgentTests(unittest.TestCase):
    def test_version_is_aether_1(self):
        self.assertEqual(main.__version__, "aether-1.0-mtn-refreshed-consensus")

    def test_both_seats_use_mtn_fixed_consensus_route(self):
        for player in (0, 1):
            observation = {
                "player": player,
                "step": 0,
                "farms": [{"hands": []}, {"hands": []}],
                "market": {"inventory": {"WOOL": 10000, "MILK": 10000}},
            }
            self.assertEqual(main._act(observation), main._route_action(main._ROUTES[player], 0))

    def test_action_ignores_farm_tile_state(self):
        """A weed under a scheduled BUILD/PLANT tile must not change the
        action or fall the agent behind schedule -- the real Kaggle
        validation episode (episode 104481488) showed seat 0 and seat 1
        drifting to 460/720 different actions because a prior per-worker
        weed-recovery delay was farm-state dependent and the two farms spawn
        weeds independently. main.py must depend only on `step`."""
        weedy_farm = {
            "farmer": [0, 0],
            "hands": [[0, 0]] * 8,
            "tiles": [[{"kind": "WEED"}] * 10 for _ in range(10)],
        }
        for player in (0, 1):
            for step in (0, 73, 186, 300):
                observation = {
                    "player": player,
                    "step": step,
                    "farms": [weedy_farm, weedy_farm],
                    "market": {"inventory": {"WOOL": 10000, "MILK": 10000}},
                }
                self.assertEqual(
                    main._act(observation),
                    main._act({**observation, "farms": [{"hands": []}, {"hands": []}]}),
                )

    def test_market_schedules_are_exact_seat_matched_copies(self):
        for player, route in enumerate(main._ROUTES):
            for step in range(len(route)):
                observation = {"player": player, "step": step, "farms": [{}, {}]}
                self.assertEqual(main._act(observation)["market"], route[step]["market"])

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
