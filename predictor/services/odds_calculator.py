from predictor.models import Game, GamePrediction


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def weigh_game(game_stats):
    score = 0

    # goaltending and shooting (50%)
    score += normalize(game_stats["save_pctg"], 0.85, 0.96) * 0.25
    score += normalize(game_stats["shooting_pctg"], 0.05, 0.20) * 0.25

    # special teams (25%)
    pp_diff = game_stats.get("power_play_goals_scored", 0) - game_stats.get(
        "power_play_goals_against", 0
    )
    sh_diff = game_stats.get("shorthanded_goals_scored", 0) - game_stats.get(
        "shorthanded_goals_against", 0
    )
    score += normalize(pp_diff, -3, 3) * 0.125
    score += normalize(sh_diff, -2, 2) * 0.125

    # discipline (7%)
    pim_diff = game_stats.get("penalty_minutes", 0) - game_stats.get(
        "opponent_penalty_minutes", 0
    )
    score += normalize(pim_diff, -20, 20) * -0.07  # more PIM is bad

    # possession proxies (15%)
    score += normalize(game_stats["face_off_win_pctg"], 0.35, 0.65) * 0.08
    takeaway_diff = game_stats.get("takeaways", 0) - game_stats.get("giveaways", 0)
    score += normalize(takeaway_diff, -15, 15) * 0.07

    # physicality (3%)
    hit_diff = game_stats.get("hits", 0) - game_stats.get("hits_taken", 0)
    score += normalize(hit_diff, -20, 20) * 0.03

    return score


RECENCY_WEIGHTS = [0.25, 0.20, 0.15, 0.13, 0.10, 0.08, 0.05, 0.04]


def average_weighted_score(game_scores):
    return sum(s * w for s, w in zip(game_scores, RECENCY_WEIGHTS))


def blend_zone_time(avg_score, zone_stats):
    all_strength = zone_stats[0]
    zone_diff = (
        all_strength["offensiveZonePctg"] - all_strength["offensiveZoneLeagueAvg"]
    )
    zone_score = normalize(zone_diff, -0.05, 0.05)
    return (avg_score * 0.92) + (zone_score * 0.08)  # was 0.85/0.15


def calculate_win_probability(
    utah_final_score,
    opponent_final_score,
    utah_is_home,
    utah_win_rate,
    opponent_win_rate,
):
    import math

    total = utah_final_score + opponent_final_score
    if total == 0:
        perf_raw = 0.5
    else:
        perf_raw = utah_final_score / total

    # Win rate as its own signal
    win_total = utah_win_rate + opponent_win_rate
    win_raw = utah_win_rate / win_total if win_total > 0 else 0.5

    # Blend performance score (60%) with win rate (40%)
    raw = perf_raw * 0.50 + win_raw * 0.50  # was 0.60/0.40

    centered = raw - 0.5
    stretched = 1 / (1 + math.exp(-12 * centered))  # increased steepness

    if utah_is_home:
        stretched = min(stretched + 0.04, 1.0)
    return round(stretched, 3)
