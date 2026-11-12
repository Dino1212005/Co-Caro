def create_standings(agent_names):
    return {
        name: {
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0.0,
        }
        for name in agent_names
    }


def record_result(standings, winner_name, first_name, second_name):
    standings[first_name]["played"] += 1
    standings[second_name]["played"] += 1

    if winner_name is None:
        standings[first_name]["draws"] += 1
        standings[second_name]["draws"] += 1
        standings[first_name]["points"] += 0.5
        standings[second_name]["points"] += 0.5
    else:
        loser_name = second_name if winner_name == first_name else first_name
        standings[winner_name]["wins"] += 1
        standings[winner_name]["points"] += 1.0
        standings[loser_name]["losses"] += 1


def rank_standings(standings):
    return sorted(
        standings.items(),
        key=lambda item: (
            item[1]["points"],
            item[1]["wins"],
            item[1]["draws"],
            item[0],
        ),
        reverse=True,
    )
