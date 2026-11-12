from agents.heuristic_agent import DIRECTIONS, evaluate_move


def copy_board(board):
    return [row[:] for row in board]


def is_inside(board, row, col):
    return 0 <= row < len(board) and 0 <= col < len(board[row])


def wins_at(board, row, col, player):
    for dr, dc in DIRECTIONS:
        length = 1
        for sign in (-1, 1):
            r = row + sign * dr
            c = col + sign * dc
            while is_inside(board, r, c) and board[r][c] == player:
                length += 1
                r += sign * dr
                c += sign * dc
        if length == 5:
            return True
    return False


def candidate_moves(board, player, limit=7):
    legal = [
        (row, col)
        for row in range(len(board))
        for col in range(len(board[row]))
        if board[row][col] == 0
    ]
    if not legal:
        return []

    occupied = [
        (row, col)
        for row in range(len(board))
        for col in range(len(board[row]))
        if board[row][col] != 0
    ]
    if not occupied:
        center = (len(board) // 2, len(board[0]) // 2)
        return [center]

    nearby = [
        move for move in legal
        if any(
            max(abs(move[0] - r), abs(move[1] - c)) <= 2
            for r, c in occupied
        )
    ]
    opponent = 3 - player
    nearby.sort(
        key=lambda move: (
            evaluate_move(board, *move, player, opponent),
            -abs(move[0] - len(board) // 2) - abs(move[1] - len(board[0]) // 2),
        ),
        reverse=True,
    )
    return nearby[:limit]


def evaluate_position(board, player):
    opponent = 3 - player
    own_moves = candidate_moves(board, player, limit=6)
    opponent_moves = candidate_moves(board, opponent, limit=6)
    own_score = max(
        (evaluate_move(board, *move, player, opponent) for move in own_moves),
        default=0,
    )
    opponent_score = max(
        (evaluate_move(board, *move, opponent, player) for move in opponent_moves),
        default=0,
    )
    return own_score - 0.9 * opponent_score
