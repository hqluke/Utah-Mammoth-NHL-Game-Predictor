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


# print info as needed
# call python predictor/services/nhl_api.py
if __name__ == "__main__":
    import json

    game = get_next_game()
    print(json.dumps(game, indent=2))
