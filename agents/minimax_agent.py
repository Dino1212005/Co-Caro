from agents.search_utils import candidate_moves, copy_board, evaluate_position, wins_at


class MinimaxAgent:
    """Shallow minimax search with alpha-beta pruning for exact-five Caro."""

    def __init__(self, depth=2, candidate_limit=7):
        self.depth = max(1, depth)
        self.candidate_limit = max(2, candidate_limit)

    def choose_move(self, game):
        player = game.current_player
        opponent = 3 - player
        board = game.board
        moves = candidate_moves(board, player, self.candidate_limit)
        if not moves:
            return None

        best_move = moves[0]
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for row, col in moves:
            next_board = copy_board(board)
            next_board[row][col] = player
            if wins_at(next_board, row, col, player):
                return row, col

            score = self._search(
                next_board,
                opponent,
                self.depth - 1,
                alpha,
                beta,
                player,
                (row, col, player),
            )
            if score > best_score:
                best_score = score
                best_move = (row, col)
            alpha = max(alpha, best_score)

        return best_move

    def _search(
        self,
        board,
        current_player,
        depth,
        alpha,
        beta,
        root_player,
        previous_move,
    ):
        row, col, previous_player = previous_move
        if wins_at(board, row, col, previous_player):
            if previous_player == root_player:
                return 1_000_000 + depth
            return -1_000_000 - depth

        if depth <= 0:
            return evaluate_position(board, root_player)

        moves = candidate_moves(board, current_player, self.candidate_limit)
        if not moves:
            return 0

        maximizing = current_player == root_player
        value = float("-inf") if maximizing else float("inf")
        for move_row, move_col in moves:
            next_board = copy_board(board)
            next_board[move_row][move_col] = current_player
            score = self._search(
                next_board,
                3 - current_player,
                depth - 1,
                alpha,
                beta,
                root_player,
                (move_row, move_col, current_player),
            )

            if maximizing:
                value = max(value, score)
                alpha = max(alpha, value)
            else:
                value = min(value, score)
                beta = min(beta, value)
            if beta <= alpha:
                break

        return value
