import torch
from torch import nn


class CaroPolicyNet(nn.Module):
    """Small policy network mapping a board state to one score per cell."""

    def __init__(self, board_size=9, hidden_size=256):
        super().__init__()
        cell_count = board_size * board_size
        self.board_size = board_size
        self.network = nn.Sequential(
            nn.Linear(cell_count, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, cell_count),
        )

    def forward(self, board_tensor):
        return self.network(board_tensor)
