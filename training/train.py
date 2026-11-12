import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from training.dataset import generate_teacher_dataset
from training.model import CaroPolicyNet


def train(games=50, epochs=12, output=None, seed=0):
    torch.manual_seed(seed)
    features, labels = generate_teacher_dataset(games=games, seed=seed)
    if not labels:
        raise RuntimeError("No training examples were generated")

    inputs = torch.tensor(features, dtype=torch.float32)
    targets = torch.tensor(labels, dtype=torch.long)
    loader = DataLoader(
        TensorDataset(inputs, targets),
        batch_size=128,
        shuffle=True,
    )

    model = CaroPolicyNet()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
    loss_function = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for batch_inputs, batch_targets in loader:
            optimizer.zero_grad()
            loss = loss_function(model(batch_inputs), batch_targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(batch_targets)
        print(f"Epoch {epoch + 1}/{epochs}: loss={total_loss / len(targets):.4f}")

    destination = Path(output) if output else (
        Path(__file__).resolve().parents[1]
        / "models"
        / "checkpoints"
        / "caro_policy.pt"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "board_size": 9,
            "model_state_dict": model.state_dict(),
            "training_games": games,
            "training_examples": len(labels),
        },
        destination,
    )
    print(f"Saved supervised policy to {destination}")
    return destination


def main():
    parser = argparse.ArgumentParser(description="Train the Caro policy from HeuristicAgent games")
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    train(args.games, args.epochs, args.output, args.seed)


if __name__ == "__main__":
    main()
