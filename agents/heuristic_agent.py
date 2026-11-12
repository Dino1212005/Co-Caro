"""AI cấp 2: Heuristic cho Caro 9x9 theo luật exact-five.

Luật thắng được dùng ở đây:
- Chỉ thắng nếu sau nước đi có đúng 5 quân liên tiếp theo ít nhất một hướng.
- Không cần hai đầu chuỗi phải mở; chuỗi 5 bị chặn vẫn thắng.
- Chuỗi từ 6 quân trở lên không thắng theo hướng đó.
"""

import random

DIRECTIONS = (
    (0, 1),   # ngang
    (1, 0),   # dọc
    (1, 1),   # chéo xuôi
    (1, -1),  # chéo ngược
)


class HeuristicAgent:
    """Agent ưu tiên thắng, chặn, rồi mới chấm điểm thế cờ.

    Thứ tự quyết định:
    1. Nếu có nước đi thắng ngay thì đánh nước đó.
    2. Nếu đối thủ có nước thắng ngay thì chiếm ô đó để chặn.
    3. Nếu không có tình huống kết thúc ngay, chấm điểm tấn công + phòng thủ.
    """

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose_move(self, game):
        actions = game.legal_actions()
        if not actions:
            return None

        board = game.board
        player = game.current_player
        opponent = 3 - player

        # 1. Ưu tiên nước thắng ngay của mình.
        winning_moves = [
            move for move in actions
            if would_win(board, move[0], move[1], player)
        ]
        if winning_moves:
            return self._best_scored_move(board, winning_moves, player, opponent)

        # 2. Nếu đối thủ có thể thắng ở một ô, chiếm ô đó.
        opponent_winning_moves = [
            move for move in actions
            if would_win(board, move[0], move[1], opponent)
        ]
        if opponent_winning_moves:
            return self._best_scored_move(
                board, opponent_winning_moves, player, opponent
            )

        # 3. Không có nước thắng/chặn bắt buộc: chọn nước có điểm cao nhất.
        return self._best_scored_move(board, actions, player, opponent)

    def _best_scored_move(self, board, moves, player, opponent):
        scored = []
        for row, col in moves:
            score = evaluate_move(board, row, col, player, opponent)
            scored.append((score, self.rng.random(), (row, col)))

        # Số ngẫu nhiên chỉ dùng phá hòa; seed giúp tái lập kết quả.
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return scored[0][2]


def _shape(board):
    return len(board), len(board[0]) if board else 0


def _inside(board, row, col):
    rows, cols = _shape(board)
    return 0 <= row < rows and 0 <= col < cols


def _value_after_move(board, row, col, player, r, c):
    """Đọc bàn cờ giả định đã đặt player tại (row, col), không sửa board."""
    if r == row and c == col:
        return player
    return board[r][c]


def _run_length_after_move(board, row, col, player, dr, dc):
    """Đếm chuỗi liên tiếp qua ô vừa đánh, bao gồm cả hai phía."""
    total = 1

    for sign in (1, -1):
        r = row + sign * dr
        c = col + sign * dc
        while _inside(board, r, c):
            if _value_after_move(board, row, col, player, r, c) != player:
                break
            total += 1
            r += sign * dr
            c += sign * dc

    return total


def would_win(board, row, col, player):
    """Return whether placing player here makes exactly five in a row."""
    if not _inside(board, row, col) or board[row][col] != 0:
        return False

    return any(
        _run_length_after_move(board, row, col, player, dr, dc) == 5
        for dr, dc in DIRECTIONS
    )


def _direction_score(board, row, col, player, dr, dc):
    run_length = 1
    open_ends = 0

    for sign in (1, -1):
        r = row + sign * dr
        c = col + sign * dc
        while _inside(board, r, c) and board[r][c] == player:
            run_length += 1
            r += sign * dr
            c += sign * dc
        if _inside(board, r, c) and board[r][c] == 0:
            open_ends += 1

    if run_length == 5:
        return 100_000
    if run_length > 5:
        return 0

    scores = (0, 2, 12, 90, 1_200)
    score = scores[run_length] * (1.0 if open_ends == 1 else 1.8 if open_ends == 2 else 0.15)
    return int(score)


def _position_score(board, row, col, player):
    return sum(
        _direction_score(board, row, col, player, dr, dc)
        for dr, dc in DIRECTIONS
    )


def evaluate_move(board, row, col, player, opponent):
    """Score an empty intersection for attack, defense, and centrality."""
    if not _inside(board, row, col) or board[row][col] != 0:
        return float("-inf")

    if would_win(board, row, col, player):
        return 100_000
    if would_win(board, row, col, opponent):
        return 50_000

    attack_score = _position_score(board, row, col, player)
    defense_score = _position_score(board, row, col, opponent)
    center = (len(board) - 1) / 2
    center_bonus = max(0, 8 - abs(row - center) - abs(col - center))
    return attack_score + defense_score * 0.9 + center_bonus