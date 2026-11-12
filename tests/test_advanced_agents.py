import json
import tempfile
import unittest
from pathlib import Path

from agents.mcts_agent import MCTSAgent
from agents.minimax_agent import MinimaxAgent
from agents.heuristic_agent import HeuristicAgent
from agents.random_agent import RandomAgent
from agents.supervised_agent import SupervisedAgent
from core.game import CaroGame
from evaluation.tournament import run_tournament


class AdvancedAgentTests(unittest.TestCase):
    def test_minimax_and_mcts_take_immediate_win(self):
        game = CaroGame(9)
        game.board[4][0:4] = [1, 1, 1, 1]
        game.current_player = 1

        self.assertEqual(MinimaxAgent().choose_move(game), (4, 4))
        self.assertEqual(MCTSAgent(iterations=8, seed=2).choose_move(game), (4, 4))

    def test_minimax_and_mcts_block_immediate_loss(self):
        game = CaroGame(9)
        game.board[4][0:4] = [2, 2, 2, 2]
        game.current_player = 1

        self.assertEqual(MinimaxAgent().choose_move(game), (4, 4))
        self.assertEqual(MCTSAgent(iterations=8, seed=3).choose_move(game), (4, 4))

    def test_supervised_agent_falls_back_when_checkpoint_is_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            agent = SupervisedAgent(checkpoint=Path(folder) / "missing.pt", seed=1)
            game = CaroGame(9)

            move = agent.choose_move(game)

        self.assertFalse(agent.is_trained)
        self.assertIn(move, game.legal_actions())

    def test_tournament_records_and_persists_results(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "result.json"
            result = run_tournament(
                games_per_pair=2,
                board_size=3,
                seed=4,
                agent_factories={
                    "Random": lambda seed: RandomAgent(seed),
                    "Heuristic": lambda seed: HeuristicAgent(seed),
                },
                results_path=output,
            )
            saved = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(len(result["matches"]), 2)
        self.assertEqual(saved["ranking"], result["ranking"])
        self.assertEqual(result["standings"]["Random"]["played"], 2)
        self.assertEqual(result["standings"]["Heuristic"]["played"], 2)


if __name__ == "__main__":
    unittest.main()
