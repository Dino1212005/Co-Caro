from pathlib import Path

import torch

from agents.heuristic_agent import HeuristicAgent
from training.dataset import encode_board
from training.model import CaroPolicyNet


DEFAULT_CHECKPOINT = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "checkpoints"
    / "caro_policy.pt"
)


class SupervisedAgent:
    """Policy-network agent; uses the teacher policy until a model is trained."""

    def __init__(self, checkpoint=DEFAULT_CHECKPOINT, seed=None):
        self.checkpoint = Path(checkpoint)
        self.teacher = HeuristicAgent(seed=seed)
        self.model = None
        self.is_trained = False
        self._load_checkpoint()

    def _load_checkpoint(self):
        if not self.checkpoint.is_file():
            return

        try:
            payload = torch.load(self.checkpoint, map_location="cpu", weights_only=True)
            if payload.get("board_size") != 9:
                return
            model = CaroPolicyNet(board_size=9)
            model.load_state_dict(payload["model_state_dict"])
            model.eval()
        except (OSError, KeyError, RuntimeError, TypeError, ValueError):
            return

        self.model = model
        self.is_trained = True

    def choose_move(self, game):
        if not game.legal_actions():
            return None
        if self.model is None:
            return self.teacher.choose_move(game)

        features = encode_board(game.board, game.current_player)
        board_tensor = torch.tensor([features], dtype=torch.float32)
        with torch.inference_mode():
            logits = self.model(board_tensor)[0]

        for row in range(game.size):
            for col in range(game.size):
                if game.board[row][col] != 0:
                    logits[row * game.size + col] = float("-inf")

        action = int(torch.argmax(logits).item())
        return divmod(action, game.size)
