import argparse
import json
from datetime import datetime
from pathlib import Path

from agents.heuristic_agent import HeuristicAgent
from agents.mcts_agent import MCTSAgent
from agents.minimax_agent import MinimaxAgent
from agents.random_agent import RandomAgent
from agents.supervised_agent import SupervisedAgent
from core.game import CaroGame
from evaluation.statistics import create_standings, rank_standings, record_result


RESULTS_PATH = Path(__file__).resolve().parent / "results" / "latest_tournament.json"


def default_agent_factories():
    supervised = SupervisedAgent()
    supervised_name = "Supervised" if supervised.is_trained else "Supervised (teacher fallback)"
    return {
        "Random": lambda seed: RandomAgent(seed=seed),
        "Heuristic": lambda seed: HeuristicAgent(seed=seed),
        "Minimax": lambda seed: MinimaxAgent(depth=2, candidate_limit=5),
        "MCTS": lambda seed: MCTSAgent(
            iterations=30,
            rollout_depth=8,
            candidate_limit=5,
            seed=seed,
        ),
        supervised_name: lambda seed: SupervisedAgent(seed=seed),
    }


def run_tournament(
    games_per_pair=2,
    board_size=9,
    seed=0,
    agent_factories=None,
    results_path=RESULTS_PATH,
):
    """Run a round robin, alternate sides, and persist standings and game records."""
    if games_per_pair < 1:
        raise ValueError("games_per_pair must be at least 1")

    factories = agent_factories or default_agent_factories()
    names = list(factories)
    standings = create_standings(names)
    matches = []
    game_number = 0

    for first_index, first_name in enumerate(names):
        for second_name in names[first_index + 1:]:
            for series_game in range(games_per_pair):
                game_number += 1
                first_factory = factories[first_name]
                second_factory = factories[second_name]
                if series_game % 2:
                    player_factories = {1: second_factory, 2: first_factory}
                    player_names = {1: second_name, 2: first_name}
                else:
                    player_factories = {1: first_factory, 2: second_factory}
                    player_names = {1: first_name, 2: second_name}

                game = CaroGame(board_size)
                agents = {
                    player: factory(seed + game_number * 10 + player)
                    for player, factory in player_factories.items()
                }
                illegal_by = None
                while not game.game_over:
                    player = game.current_player
                    move = agents[player].choose_move(game)
                    if move is None or not game.make_move(*move):
                        illegal_by = player
                        break

                if illegal_by is not None:
                    winner_name = player_names[3 - illegal_by]
                    result = "forfeit"
                elif game.winner in (1, 2):
                    winner_name = player_names[game.winner]
                    result = "win"
                else:
                    winner_name = None
                    result = "draw"

                record_result(
                    standings,
                    winner_name,
                    first_name,
                    second_name,
                )
                matches.append(
                    {
                        "agent_a": first_name,
                        "agent_b": second_name,
                        "player_x": player_names[1],
                        "player_o": player_names[2],
                        "winner": winner_name,
                        "result": result,
                        "moves": game.moves_count,
                    }
                )

    payload = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "board_size": board_size,
        "games_per_pair": games_per_pair,
        "standings": standings,
        "ranking": [
            {"agent": name, **stats}
            for name, stats in rank_standings(standings)
        ],
        "matches": matches,
    }
    destination = Path(results_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser(description="Run a Caro AI round-robin tournament")
    parser.add_argument("--games-per-pair", type=int, default=2)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, default=RESULTS_PATH)
    args = parser.parse_args()
    result = run_tournament(
        games_per_pair=args.games_per_pair,
        seed=args.seed,
        results_path=args.output,
    )
    for position, row in enumerate(result["ranking"], start=1):
        print(
            f"{position}. {row['agent']}: {row['points']} points "
            f"({row['wins']}W/{row['draws']}D/{row['losses']}L)"
        )
    print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()
