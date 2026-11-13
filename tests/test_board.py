import unittest

from core.board import Board


class TestBoard(unittest.TestCase):
	def test_size_must_be_positive(self):
		for size in (0, -1):
			with self.subTest(size=size):
				with self.assertRaises(ValueError):
					Board(size)

	def test_bounds_and_empty_cells(self):
		board = Board(2)

		self.assertTrue(board.is_inside(0, 0))
		self.assertTrue(board.is_inside(1, 1))
		self.assertFalse(board.is_inside(-1, 0))
		self.assertFalse(board.is_inside(0, 2))
		self.assertTrue(board.is_empty(0, 0))
		self.assertFalse(board.is_empty(-1, 0))

	def test_place_piece_rejects_invalid_player_and_occupied_cell(self):
		board = Board(2)

		with self.assertRaises(ValueError):
			board.place_piece(0, 0, 0)
		self.assertTrue(board.place_piece(0, 0, 1))
		self.assertFalse(board.place_piece(0, 0, 2))
		self.assertEqual(board.cells[0][0], 1)

	def test_legal_actions_and_full_board(self):
		board = Board(2)
		self.assertEqual(len(board.legal_actions()), 4)
		self.assertFalse(board.is_full())

		for row in range(2):
			for col in range(2):
				board.place_piece(row, col, 1)

		self.assertEqual(board.legal_actions(), [])
		self.assertTrue(board.is_full())

	def test_clone_copies_cells_independently(self):
		board = Board(2)
		board.place_piece(0, 1, 2)

		copied = board.clone()
		copied.place_piece(1, 0, 1)

		self.assertEqual(board.cells, [[0, 2], [0, 0]])
		self.assertEqual(copied.cells, [[0, 2], [1, 0]])


if __name__ == "__main__":
	unittest.main()
