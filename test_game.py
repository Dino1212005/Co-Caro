import unittest

from game import CaroGame


class TestCaroGame(unittest.TestCase):

    def test_horizontal_win(self):
        game = CaroGame()

        for col in range(5):
            game.board[4][col] = 1

        result = game.check_winner(4, 2, 1)

        self.assertEqual(len(result), 5)

    def test_vertical_win(self):
        game = CaroGame()

        for row in range(5):
            game.board[row][3] = 1

        result = game.check_winner(2, 3, 1)

        self.assertEqual(len(result), 5)

    def test_diagonal_win(self):
        game = CaroGame()

        for i in range(5):
            game.board[i][i] = 1

        result = game.check_winner(2, 2, 1)

        self.assertEqual(len(result), 5)

    def test_blocked_five_still_wins(self):
        game = CaroGame()

        game.board[4][0] = 2

        for col in range(1, 6):
            game.board[4][col] = 1

        game.board[4][6] = 2

        result = game.check_winner(4, 3, 1)

        self.assertEqual(len(result), 5)

    def test_six_in_a_row_is_not_win(self):
        game = CaroGame()

        for col in range(6):
            game.board[4][col] = 1

        result = game.check_winner(4, 3, 1)

        self.assertIsNone(result)

    def test_invalid_move(self):
        game = CaroGame()

        self.assertTrue(game.make_move(0, 0))

        # Không thể đánh lại ô đã có quân
        self.assertFalse(game.make_move(0, 0))

    def test_reset(self):
        game = CaroGame()

        game.make_move(0, 0)
        game.reset()

        self.assertEqual(game.board[0][0], 0)
        self.assertEqual(game.current_player, 1)
        self.assertFalse(game.game_over)


if __name__ == "__main__":
    unittest.main()