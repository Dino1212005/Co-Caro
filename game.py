# game.py

class CaroGame:
    def __init__(self, size=9):
        self.size = size
        self.reset()

    # Khởi tạo ván cờ mới
    def reset(self):
        self.board = [
            [0 for _ in range(self.size)]
            for _ in range(self.size)
        ]

        self.current_player = 1  # 1 = X, 2 = O
        self.winner = None
        self.winning_cells = []
        self.game_over = False
        self.moves_count = 0

    # Lấy danh sách các ô còn trống
    def legal_actions(self):
        actions = []

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    actions.append((row, col))

        return actions

    # Kiểm tra vị trí có hợp lệ không
    def is_valid_move(self, row, col):
        return (
            0 <= row < self.size
            and 0 <= col < self.size
            and self.board[row][col] == 0
            and not self.game_over
        )

    # Đếm số quân liên tiếp theo một hướng
    def count_direction(self, row, col, dr, dc, player):
        count = 0

        r = row + dr
        c = col + dc

        while (
            0 <= r < self.size
            and 0 <= c < self.size
            and self.board[r][c] == player
        ):
            count += 1
            r += dr
            c += dc

        return count

    # Kiểm tra có đúng 5 quân liên tiếp không
    def check_winner(self, row, col, player):
        directions = [
            (0, 1),   # Ngang
            (1, 0),   # Dọc
            (1, 1),   # Chéo chính
            (1, -1)   # Chéo phụ
        ]

        for dr, dc in directions:
            count_before = self.count_direction(
                row, col, -dr, -dc, player
            )

            count_after = self.count_direction(
                row, col, dr, dc, player
            )

            total = count_before + 1 + count_after

            if total == 5:
                cells = []

                start_row = row - count_before * dr
                start_col = col - count_before * dc

                for i in range(5):
                    cells.append((
                        start_row + i * dr,
                        start_col + i * dc
                    ))

                return cells

        return None

    # Thực hiện một nước đi
    def make_move(self, row, col):
        if not self.is_valid_move(row, col):
            return False

        player = self.current_player

        self.board[row][col] = player
        self.moves_count += 1

        # Kiểm tra thắng
        winning_cells = self.check_winner(
            row, col, player
        )

        if winning_cells:
            self.winner = player
            self.winning_cells = winning_cells
            self.game_over = True
            return True

        # Kiểm tra hòa
        if self.moves_count == self.size * self.size:
            self.game_over = True
            self.winner = 0
            return True

        # Chuyển lượt
        self.current_player = 3 - player

        return True

    # Trả về kết quả ván cờ
    def result(self):
        if not self.game_over:
            return None

        if self.winner == 0:
            return "DRAW"

        if self.winner == 1:
            return "X"

        return "O"