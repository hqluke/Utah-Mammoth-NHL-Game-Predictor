import requests
from datetime import datetime

# get current date formatted as YYYY-MM-DD
today = datetime.now().strftime("%Y-%m-%d")


def get_next_game():
    url = "https://api-web.nhle.com/v1/club-schedule/UTA/week/now"
    response = requests.get(url)
    games = response.json()["games"]
    for game in games:
        if game["gameDate"] >= today:
            return game


def get_next_teams():
    game = get_next_game()
    away_team = game["awayTeam"]
    home_team = game["homeTeam"]
    if away_team["id"] == 68:
        utah = away_team
        opponent = home_team
    else:
        utah = home_team
        opponent = away_team
    utahID = utah["id"]
    opponentID = opponent["id"]
    # print(utah["logo"])
    return utahID, opponentID


# print info as needed
# call python predictor/services/nhl_api.py
if __name__ == "__main__":
    import json

    # game = get_next_game()
    # print(json.dumps(game, indent=2))

    utahId, opponentId = get_next_teams()
    print(json.dumps([utahId, opponentId], indent=2))
