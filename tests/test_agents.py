import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.heuristic_agent import HeuristicAgent
from agents.random_agent import RandomAgent
from agents.supervised_agent import SupervisedAgent
from core.game import CaroGame


class TestAgents(unittest.TestCase):
	def test_random_agent_returns_legal_move_without_mutating_game(self):
		game = CaroGame(5)
		game.make_move(2, 2)
		original_board = [row[:] for row in game.board]
		original_player = game.current_player

		move = RandomAgent(seed=7).choose_move(game)

		self.assertIn(move, game.legal_actions())
		self.assertEqual(game.board, original_board)
		self.assertEqual(game.current_player, original_player)

	def test_random_agent_is_reproducible_with_same_seed(self):
		game = CaroGame()

		first_move = RandomAgent(seed=12).choose_move(game)
		second_move = RandomAgent(seed=12).choose_move(game)

		self.assertEqual(first_move, second_move)

	def test_heuristic_agent_takes_immediate_win(self):
		game = CaroGame()
		game.board[4][0:4] = [1, 1, 1, 1]

		self.assertEqual(HeuristicAgent(seed=1).choose_move(game), (4, 4))

	def test_heuristic_agent_blocks_immediate_loss(self):
		game = CaroGame()
		game.board[4][0:4] = [2, 2, 2, 2]

		self.assertEqual(HeuristicAgent(seed=1).choose_move(game), (4, 4))

	def test_agents_return_none_when_no_moves_remain(self):
		game = CaroGame(1)
		game.make_move(0, 0)

		self.assertIsNone(RandomAgent(seed=1).choose_move(game))
		self.assertIsNone(HeuristicAgent(seed=1).choose_move(game))

	def test_supervised_agent_falls_back_when_torch_is_unavailable(self):
		with tempfile.TemporaryDirectory() as folder:
			checkpoint = Path(folder) / "missing.pt"
			with patch(
				"agents.supervised_agent._load_torch",
				return_value=(None, None),
			):
				agent = SupervisedAgent(checkpoint=checkpoint, seed=3)
				game = CaroGame()
				move = agent.choose_move(game)

		self.assertFalse(agent.is_available)
		self.assertFalse(agent.is_trained)
		self.assertIn(move, game.legal_actions())


if __name__ == "__main__":
	unittest.main()
