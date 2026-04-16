import requests
from datetime import datetime
from bs4 import BeautifulSoup

# get current date formatted as YYYY-MM-DD
TODAY = datetime.now().strftime("%Y-%m-%d")
CURRENT_YEAR = datetime.now().year


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
    # print(f"UTAH: {utah_abbreviation}")
    # print(json.dumps([utahAbbreviation, opponentAbbreviation], indent=2))

    utah_injured_players = get_injured_players(utah_abbreviation)
    opponent_injured_players = get_injured_players(opponent_abbreviation)
    print(json.dumps([utah_injured_players, opponent_injured_players], indent=2))
