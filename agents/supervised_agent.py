from pathlib import Path

from agents.heuristic_agent import HeuristicAgent


DEFAULT_CHECKPOINT = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "checkpoints"
    / "caro_policy.pt"
)


def _load_torch():
    try:
        import torch
        from training.model import CaroPolicyNet
    except (ImportError, OSError):
        return None, None
    return torch, CaroPolicyNet


class SupervisedAgent:
    """Policy-network agent; uses the teacher policy until a model is trained."""

    def __init__(self, checkpoint=DEFAULT_CHECKPOINT, seed=None):
        self.checkpoint = Path(checkpoint)
        self.teacher = HeuristicAgent(seed=seed)
        self.torch, self.model_class = _load_torch()
        self.is_available = self.torch is not None
        self.model = None
        self.is_trained = False
        self._load_checkpoint()

    def _load_checkpoint(self):
        if not self.is_available or not self.checkpoint.is_file():
            return

        try:
            payload = self.torch.load(
                self.checkpoint,
                map_location="cpu",
                weights_only=True,
            )
            if payload.get("board_size") != 9:
                return
            model = self.model_class(board_size=9)
            model.load_state_dict(payload["model_state_dict"])
            model.eval()
        except (OSError, KeyError, RuntimeError, TypeError, ValueError):
            return

        self.model = model
        self.is_trained = True

    def choose_move(self, game):
        if not game.legal_actions():
            return None
        if self.model is None or not self.is_available:
            return self.teacher.choose_move(game)

        from training.dataset import encode_board

        features = encode_board(game.board, game.current_player)
        board_tensor = self.torch.tensor([features], dtype=self.torch.float32)
        with self.torch.inference_mode():
            logits = self.model(board_tensor)[0]

        for row in range(game.size):
            for col in range(game.size):
                if game.board[row][col] != 0:
                    logits[row * game.size + col] = float("-inf")

        action = int(self.torch.argmax(logits).item())
        return divmod(action, game.size)
