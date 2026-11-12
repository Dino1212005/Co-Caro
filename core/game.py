from core.board import Board


DIRECTIONS = (
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1),
)


class CaroGame:
    def __init__(self, size=9):
        self.size = size
        self.reset()

    def reset(self):
        self._board = Board(self.size)
        self.current_player = 1
        self.winner = None
        self.winning_cells = []
        self.game_over = False
        self.moves_count = 0

    @property
    def board(self):
        return self._board.cells

    def legal_actions(self):
        return self._board.legal_actions()

    def is_valid_move(self, row, col):
        return not self.game_over and self._board.is_empty(row, col)

    def count_direction(self, row, col, dr, dc, player):
        count = 0
        r = row + dr
        c = col + dc
        while self._board.is_inside(r, c) and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def check_winner(self, row, col, player):
        for dr, dc in DIRECTIONS:
            before = self.count_direction(row, col, -dr, -dc, player)
            after = self.count_direction(row, col, dr, dc, player)
            if before + 1 + after != 5:
                continue

            start_row = row - before * dr
            start_col = col - before * dc
            return [
                (start_row + offset * dr, start_col + offset * dc)
                for offset in range(5)
            ]
        return None

    def make_move(self, row, col):
        if not self.is_valid_move(row, col):
            return False

        player = self.current_player
        if not self._board.place_piece(row, col, player):
            return False
        self.moves_count += 1

        winning_cells = self.check_winner(row, col, player)
        if winning_cells:
            self.winner = player
            self.winning_cells = winning_cells
            self.game_over = True
        elif self._board.is_full():
            self.winner = 0
            self.game_over = True
        else:
            self.current_player = 3 - player
        return True

    def result(self):
        if not self.game_over:
            return None
        if self.winner == 0:
            return "DRAW"
        return "X" if self.winner == 1 else "O"

    def clone(self):
        copied = CaroGame(self.size)
        copied._board = self._board.clone()
        copied.current_player = self.current_player
        copied.winner = self.winner
        copied.winning_cells = self.winning_cells[:]
        copied.game_over = self.game_over
        copied.moves_count = self.moves_count
        return copied
