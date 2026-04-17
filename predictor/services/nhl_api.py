import requests
from datetime import datetime
from bs4 import BeautifulSoup

# get current date formatted as YYYY-MM-DD
GAME_TYPE = 2  # regular season  TODO: add logic to update later
NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
CURRENT_YEAR = NOW.year
SWITCH_MONTH = datetime(NOW.year, 9, 1)

if NOW >= SWITCH_MONTH:
    OTHER_YEAR = CURRENT_YEAR + 1
else:
    OTHER_YEAR = CURRENT_YEAR - 1

if CURRENT_YEAR <= OTHER_YEAR:
    CURRENT_SEASON = str(CURRENT_YEAR) + str(OTHER_YEAR)
else:
    CURRENT_SEASON = str(OTHER_YEAR) + str(CURRENT_YEAR)


def get_next_game():
    url = "https://api-web.nhle.com/v1/club-schedule/UTA/week/now"
    response = requests.get(url)
    games = response.json()["games"]
    for game in games:
        if game["gameDate"] >= TODAY:
            return game


def get_next_teams(game):
    away_team = game["awayTeam"]
    home_team = game["homeTeam"]
    if away_team["id"] == 68:
        utah = away_team
        opponent = home_team
    else:
        utah = home_team
        opponent = away_team
    return utah, opponent


def get_injured_players(team_abbrev):
    url = f"https://www.hockey-reference.com/teams/{team_abbrev}/{CURRENT_YEAR}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    injury_table = soup.find("table", {"id": "injuries"})

    if not injury_table:
        return {}

    caption = injury_table.find("caption").text
    total_injured = int(caption.split()[0])

    injuries = {}
    rows = injury_table.find("tbody").find_all("tr")

    for i, row in enumerate(rows):
        player = row.find("th", {"data-stat": "player"}).text
        date = row.find("td", {"data-stat": "date_injury"}).text
        injury_type = row.find("td", {"data-stat": "injury_type"}).text
        note = row.find("td", {"data-stat": "injury_note"}).text

        injuries[i] = {
            "player": player,
            "injuryDate": date,
            "injuryType": injury_type,
            "injuryNote": note,
        }

    return {"total": total_injured, "players": injuries}


def prev_five_games(team_abbrev):
    # example url: "https://api-web.nhle.com/v1/club-schedule-season/UTA/20252026"
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team_abbrev}/{CURRENT_SEASON}"
    response = requests.get(url)
    games = response.json()["games"]
    # get most recent games first
    games.reverse()
    game_map = {}
    for game in games:
        if game["gameDate"] < TODAY:
            game_map[game["gameDate"]] = game["id"]
            if len(game_map) == 5:
                return game_map
    return {}


def get_stats_from_game(game_id, team_abbrev):
    output = {}
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    response = requests.get(url)
    team_one = response.json()["homeTeam"]
    team_two = response.json()["awayTeam"]
    if team_one["abbrev"] != team_abbrev:
        team_we_check = "awayTeam"
        output["opponent_abbrev"] = team_one["abbrev"]
        output["total_goals_scored"] = team_one["score"]
        output["total_goals_allowed"] = team_two["score"]
        other_team = "homeTeam"
    else:
        team_we_check = "homeTeam"
        other_team = "awayTeam"
        output["opponent_abbrev"] = team_two["abbrev"]
        output["total_goals_scored"] = team_two["score"]
        output["total_goals_allowed"] = team_one["score"]
    goalies = response.json()["playerByGameStats"][team_we_check]["goalies"]
    for goalie in goalies:
        if goalie["saves"] > 0:
            if goalie["decision"]:
                output["decision"] = goalie["decision"]
            output["shots_against"] = goalie["shotsAgainst"] + output.get(
                "shots_against", 0
            )
            output["saves"] = goalie["saves"] + output.get("saves", 0)
            output["goals_allowed"] = goalie["goalsAgainst"] + output.get(
                "goals_allowed", 0
            )
            output["save_pctg"] = output["saves"] / output["shots_against"]
            output["power_play_goals_against"] = goalie[
                "powerPlayGoalsAgainst"
            ] + output.get("power_play_goals_against", 0)
            output["shorthanded_goals_against"] = goalie[
                "shorthandedGoalsAgainst"
            ] + output.get("shorthanded_goals_against", 0)
            output["even_strength_goals_against"] = goalie[
                "evenStrengthGoalsAgainst"
            ] + output.get("even_strength_goals_against", 0)

    goalies = response.json()["playerByGameStats"][other_team]["goalies"]
    for goalie in goalies:
        if goalie["saves"] > 0:
            output["goals_scored"] = goalie["goalsAgainst"] + output.get(
                "goals_scored", 0
            )
            output["shots_on_goal"] = goalie["shotsAgainst"] + output.get(
                "shots_attempted", 0
            )
            output["shots_missed"] = goalie["saves"] + output.get("shots_missed", 0)
            output["shooting_pctg"] = output["goals_scored"] / output["shots_on_goal"]
            output["power_play_goals_scored"] = goalie[
                "powerPlayGoalsAgainst"
            ] + output.get("power_play_goals_scored", 0)
            output["shorthanded_goals_scored"] = goalie[
                "shorthandedGoalsAgainst"
            ] + output.get("shorthanded_goals_scored", 0)
            output["even_strength_goals_scored"] = goalie[
                "evenStrengthGoalsAgainst"
            ] + output.get("even_strength_goals_scored", 0)

    faceoffs = []
    forwards = response.json()["playerByGameStats"][team_we_check]["forwards"]
    defense = response.json()["playerByGameStats"][team_we_check]["defense"]
    positions = [defense, forwards]
    for position in positions:
        for player in position:
            if player["giveaways"] > 0:
                output["giveaways"] = player["giveaways"] + output.get("giveaways", 0)
            if player["takeaways"] > 0:
                output["takeaways"] = player["takeaways"] + output.get("takeaways", 0)
            if player["faceoffWinningPctg"] > 0:
                faceoffs.append(player["faceoffWinningPctg"])
            if player["hits"] > 0:
                output["hits"] = player["hits"] + output.get("hits", 0)
            if player["pim"] > 0:
                output["penalty_minutes"] = player["pim"] + output.get(
                    "penalty_minutes", 0
                )
    other_forwards = response.json()["playerByGameStats"][other_team]["forwards"]
    other_defense = response.json()["playerByGameStats"][other_team]["defense"]
    other_positions = [other_defense, other_forwards]
    for position in other_positions:
        for player in position:
            if player["hits"] > 0:
                output["hits_taken"] = player["hits"] + output.get("hits_taken", 0)

    output["face_off_win_pctg"] = sum(faceoffs) / len(faceoffs)
    output["face_off_win_pctg"] = round(output["face_off_win_pctg"], 3)
    return output


#  shows power play, penalty kill, all zone minutes, and shot differential
#  details/teamId/season/game-type  (game-type =1 for preseason, 2 for regular season, 3 for playoffs,)
def get_zone_stats(team_id, season=CURRENT_SEASON, game_type=GAME_TYPE):
    url = f"https://api-web.nhle.com/v1/edge/team-zone-time-details/{team_id}/{season}/{game_type}"
    response = requests.get(url)
    stats = response.json()["zoneTimeDetails"]
    return stats


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def weigh_game(game_stats):
    score = 0
    score += normalize(game_stats["save_pctg"], 0.85, 0.96) * 0.20
    score += normalize(game_stats["shooting_pctg"], 0.05, 0.20) * 0.10
    score += normalize(game_stats["total_goals_scored"], 0, 7) * 0.20
    score += normalize(game_stats["total_goals_allowed"], 0, 7) * -0.15
    score += normalize(game_stats["face_off_win_pctg"], 0.35, 0.65) * 0.10
    score += (
        normalize(game_stats["takeaways"] - game_stats["giveaways"], -15, 15) * 0.10
    )
    score += (1 if game_stats["decision"] == "W" else 0) * 0.15
    return score


# future links:
# Retrieve NHL Edge data for the specified player, Includes skating distance and speed data, shot location and speed data, zone time details and zone starts.
# comparison/playerId/season/game-type
# (would have to call this for all the players on the team per game) would def get rate limited
# maybe would work if i started saving this in a database for each playerId. when I calc a new game, I would only calc the previous games that weren't in the database
# theres no way i don't get rate limited initally setting this up. im gonna leave this for now
# "https://api-web.nhle.com/v1/edge/skater-comparison/8482116/20242025/2"


# eventually populate with data that's being used in the main function
def get_all_info():
    game = get_next_game()
    utah, opponent = get_next_teams(game)
    utahAbbreviation = utah["abbrev"]
    opponentAbbreviation = opponent["abbrev"]
    utahInjuredPlayers = get_injured_players(utahAbbreviation)
    opponentInjuredPlayers = get_injured_players(opponentAbbreviation)


# print info as needed
# call python predictor/services/nhl_api.py
if __name__ == "__main__":
    import json

    # game = get_next_game()
    # print(json.dumps(game, indent=2))

    game = get_next_game()
    utah, opponent = get_next_teams(game)
    # print(json.dumps([utah, opponent], indent=2))

    utah_abbreviation = utah["abbrev"]
    opponent_abbreviation = opponent["abbrev"]
    utah_id = utah["id"]
    opponent_id = opponent["id"]
    # print(f"OPPONENT ID: {opponent_id}")
    # print(f"UTAH: {utah_abbreviation}")
    # print(json.dumps([utahAbbreviation, opponentAbbreviation], indent=2))

    # utah_injured_players = get_injured_players(utah_abbreviation)
    # opponent_injured_players = get_injured_players(opponent_abbreviation)
    # print(json.dumps([utah_injured_players, opponent_injured_players], indent=2))

    utah_prev_five_games = prev_five_games(utah_abbreviation)
    opponent_prev_five_games = prev_five_games(opponent_abbreviation)
    print(json.dumps([utah_prev_five_games], indent=2))

    # first_game = list(utah_prev_five_games.values())[0]
    # utah_stats = get_stats_from_game(first_game, utah_abbreviation)
    # print(json.dumps(utah_stats, indent=2))

    utah_game_output = {}
    for k, v in utah_prev_five_games.items():
        utah_game_output[k] = get_stats_from_game(v, utah_abbreviation)

    # opponent_game_output = {}
    # for k, v in opponent_prev_five_games.items():
    #     opponent_game_output[k] = get_stats_from_game(v, opponent_abbreviation)

    print("UTAH")
    print(json.dumps(utah_game_output, indent=2))
    # print(opponent_abbreviation)
    # print(json.dumps(opponent_game_output, indent=2))

    utah_zone = get_zone_stats(utah_id)
    opponent_zone = get_zone_stats(opponent_id)
    # print(json.dumps(utah_zone, indent=2))
    # print(json.dumps(opponent_zone, indent=2))

    utah_weighted_scores = []
    for k, v in utah_game_output.items():
        utah_weighted_scores.append(weigh_game(v))
    print(utah_weighted_scores)
