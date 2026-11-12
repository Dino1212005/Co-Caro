"""AI cấp 1: chọn ngẫu nhiên một nước đi hợp lệ."""

import random


class RandomAgent:
    """Agent chọn ngẫu nhiên trong game.legal_actions().

    Args:
        seed: số nguyên để có thể lặp lại chuỗi nước đi khi kiểm thử.
    """

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose_move(self, game):
        """Trả về (row, col), hoặc None nếu không còn nước đi hợp lệ."""
        actions = game.legal_actions()
        if not actions:
            return None
        return self.rng.choice(actions)
