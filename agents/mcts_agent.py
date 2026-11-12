import math
import random

from agents.heuristic_agent import evaluate_move, would_win
from agents.search_utils import (
    candidate_moves,
    copy_board,
    evaluate_position,
    wins_at,
)


class _Node:
    def __init__(self, board, to_move, root_player, candidate_limit, parent=None, move=None, winner=None):
        self.board = board
        self.to_move = to_move
        self.root_player = root_player
        self.parent = parent
        self.move = move
        self.winner = winner
        self.visits = 0
        self.value = 0.0
        self.children = []
        self.untried_moves = [] if winner is not None else candidate_moves(
            board, to_move, candidate_limit
        )
        if not self.untried_moves and winner is None:
            self.winner = 0


class MCTSAgent:
    """Monte Carlo Tree Search with UCT selection and bounded rollouts."""

    def __init__(self, iterations=100, rollout_depth=12, candidate_limit=7, seed=None):
        self.iterations = max(1, iterations)
        self.rollout_depth = max(1, rollout_depth)
        self.candidate_limit = max(2, candidate_limit)
        self.rng = random.Random(seed)

    def choose_move(self, game):
        root_player = game.current_player
        opponent = 3 - root_player
        immediate_moves = candidate_moves(
            game.board, root_player, self.candidate_limit
        )
        winning_move = next(
            (move for move in immediate_moves if would_win(game.board, *move, root_player)),
            None,
        )
        if winning_move is not None:
            return winning_move
        blocking_move = next(
            (move for move in immediate_moves if would_win(game.board, *move, opponent)),
            None,
        )
        if blocking_move is not None:
            return blocking_move

        root = _Node(
            copy_board(game.board),
            root_player,
            root_player,
            self.candidate_limit,
        )
        if not root.untried_moves:
            return None

        for _ in range(self.iterations):
            node = root
            while node.winner is None and not node.untried_moves and node.children:
                node = self._select_child(node)

            if node.winner is None and node.untried_moves:
                node = self._expand(node)

            reward = self._rollout(node)
            while node is not None:
                node.visits += 1
                node.value += reward
                node = node.parent

        best = max(
            root.children,
            key=lambda child: (child.visits, child.value / max(child.visits, 1)),
        )
        return best.move

    def _select_child(self, node):
        logarithm = math.log(max(node.visits, 1))

        def uct(child):
            mean = child.value / max(child.visits, 1)
            exploitation = mean if node.to_move == node.root_player else 1.0 - mean
            exploration = math.sqrt(logarithm / max(child.visits, 1))
            return exploitation + math.sqrt(2.0) * exploration

        return max(node.children, key=uct)

    def _expand(self, node):
        move = self.rng.choice(node.untried_moves)
        node.untried_moves.remove(move)
        row, col = move
        next_board = copy_board(node.board)
        next_board[row][col] = node.to_move
        winner = node.to_move if wins_at(next_board, row, col, node.to_move) else None
        child = _Node(
            next_board,
            3 - node.to_move,
            node.root_player,
            self.candidate_limit,
            parent=node,
            move=move,
            winner=winner,
        )
        node.children.append(child)
        return child

    def _rollout(self, node):
        if node.winner is not None:
            if node.winner == 0:
                return 0.5
            return 1.0 if node.winner == node.root_player else 0.0

        board = copy_board(node.board)
        player = node.to_move
        for _ in range(self.rollout_depth):
            moves = candidate_moves(board, player, self.candidate_limit)
            if not moves:
                return 0.5

            opponent = 3 - player
            winning = next(
                (move for move in moves if would_win(board, *move, player)),
                None,
            )
            blocking = next(
                (move for move in moves if would_win(board, *move, opponent)),
                None,
            )
            if winning is not None:
                move = winning
            elif blocking is not None:
                move = blocking
            else:
                ranked = sorted(
                    moves,
                    key=lambda move: evaluate_move(board, *move, player, opponent),
                    reverse=True,
                )
                move = self.rng.choice(ranked[: min(3, len(ranked))])

            row, col = move
            board[row][col] = player
            if wins_at(board, row, col, player):
                return 1.0 if player == node.root_player else 0.0
            player = opponent

        position_score = evaluate_position(board, node.root_player)
        return 0.5 + position_score / (2.0 * (abs(position_score) + 2_500.0))
