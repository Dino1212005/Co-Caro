from agents.heuristic_agent import HeuristicAgent
from core.game import CaroGame


def encode_board(board, player):
    opponent = 3 - player
    return [
        1.0 if cell == player else -1.0 if cell == opponent else 0.0
        for row in board
        for cell in row
    ]


def generate_teacher_dataset(games=100, board_size=9, seed=0):
    """Collect state-to-move examples from HeuristicAgent self-play."""
    features = []
    labels = []

    for game_index in range(games):
        game = CaroGame(board_size)
        teacher = HeuristicAgent(seed=seed + game_index)
        while not game.game_over:
            move = teacher.choose_move(game)
            if move is None:
                break
            row, col = move
            features.append(encode_board(game.board, game.current_player))
            labels.append(row * board_size + col)
            if not game.make_move(row, col):
                raise RuntimeError(f"Teacher returned an illegal move: {move}")

    return features, labels
