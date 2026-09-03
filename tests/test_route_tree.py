import unittest

from tools.route_tree import analyze_games, render_tree


def action(name):
    return {"farmer": [name], "hands": [], "market": []}


def game(episode_id, names, margin):
    return {
        "episode_id": episode_id,
        "actions": [action(name) for name in names],
        "margin": margin,
        "opponent": "test",
        "seat": 0,
    }


class RouteTreeTests(unittest.TestCase):
    def test_shared_prefix_branches_without_synthetic_routes(self):
        games = [
            game(1, ["A", "B", "C", "D"], 10),
            game(2, ["A", "B", "X", "D"], 5),
            game(3, ["A", "B", "C", "D"], -1),
        ]
        result = analyze_games(games, min_support=2, min_branch_fraction=0.2)

        self.assertEqual(result["episodes"], 3)
        self.assertEqual(result["unique_routes"], 2)
        self.assertEqual(result["duplicate_routes"], 1)
        self.assertEqual(result["first_branch_step"], 2)
        self.assertEqual(len(result["tree"]["children"]), 2)
        self.assertTrue(result["tree"]["children"][0]["parent_path"])
        self.assertEqual(
            sorted(result["tree"]["route_ids"]),
            sorted(route["route_id"] for route in result["routes"]),
        )
        rendered = render_tree(result["tree"])
        self.assertIn("branch at step 2", rendered)
        self.assertIn("parent support=2", rendered)

    def test_support_and_outcomes_drive_plausibility(self):
        games = [
            game(1, ["A", "B"], 10),
            game(2, ["A", "B"], 4),
            game(3, ["A", "X"], -8),
        ]
        result = analyze_games(games, min_support=2, min_branch_fraction=0.5)
        by_support = sorted(result["routes"], key=lambda route: route["support"], reverse=True)

        self.assertTrue(by_support[0]["plausible"])
        self.assertEqual(by_support[0]["evidence"], "high")
        self.assertFalse(by_support[1]["plausible"])
        self.assertEqual(by_support[1]["evidence"], "low")


if __name__ == "__main__":
    unittest.main()
