class Board:
    """Mutable square grid for the Caro game engine."""

    def __init__(self, size=9):
        if size < 1:
            raise ValueError("Board size must be positive")
        self.size = size
        self.cells = [[0 for _ in range(size)] for _ in range(size)]

    def is_inside(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, row, col):
        return self.is_inside(row, col) and self.cells[row][col] == 0

    def place_piece(self, row, col, player):
        if player not in (1, 2):
            raise ValueError("Player must be 1 or 2")
        if not self.is_empty(row, col):
            return False
        self.cells[row][col] = player
        return True

    def legal_actions(self):
        return [
            (row, col)
            for row in range(self.size)
            for col in range(self.size)
            if self.cells[row][col] == 0
        ]

    def is_full(self):
        return all(cell != 0 for row in self.cells for cell in row)

    def clone(self):
        copied = Board(self.size)
        copied.cells = [row[:] for row in self.cells]
        return copied
