from django.shortcuts import render
from predictor.services import graph_builder
from predictor.services import nhl_api
from datetime import datetime
from zoneinfo import ZoneInfo

# Create your views here.


def index(request):
    data = nhl_api.get_all_info()
    utah_abbreviation = data["utah"]["abbrev"]
    opponent_abbreviation = data["opponent"]["abbrev"]

    graph_data = graph_builder.build_all_graphs(data)
    utah_goals_graph = graph_data["utah_goals_graph"]
    opponent_goals_graph = graph_data["opponent_goals_graph"]

    win_p = data["utah_win_probability"] * 100
    win_probability = round(win_p, 2)
    predicted_score = data["predicted_score"]

    utah_performance_graph = graph_data["utah_performance_graph"]
    opponent_performance_graph = graph_data["opponent_performance_graph"]

    utah_injured_players = list(data["utah_injured"].get("players", {}).values())
    opponent_injured_players = list(
        data["opponent_injured"].get("players", {}).values()
    )
    total_utah_injured_players = data["utah_injured"]["total"]
    total_opponent_injured_players = data["opponent_injured"]["total"]

    utah_name = (
        data["utah"]["placeName"]["default"]
        + " "
        + data["utah"]["commonName"]["default"]
    )
    opponent_name = (
        data["opponent"]["placeName"]["default"]
        + " "
        + data["opponent"]["commonName"]["default"]
    )

    utah_light_logo = data["utah"]["logo"]
    utah_dark_logo = data["utah"]["darkLogo"]
    opponent_light_logo = data["opponent"]["logo"]
    opponent_dark_logo = data["opponent"]["darkLogo"]

    venue = data["game"]["venue"]["default"]
    utc_time = data["game"]["startTimeUTC"]
    start_date, start_time = format_game_time("2026-04-25T01:30:00Z")

    utah_record = data["utah_record"]
    opponent_record = data["opponent_record"]

    return render(
        request,
        "index/index.html",
        {
            "utah_goals_graph": utah_goals_graph,
            "opponent_goals_graph": opponent_goals_graph,
            "predicted_score": predicted_score,
            "utah_performance_graph": utah_performance_graph,
            "opponent_performance_graph": opponent_performance_graph,
            "utah_injured_players": utah_injured_players,
            "opponent_injured_players": opponent_injured_players,
            "total_utah_injured_players": total_utah_injured_players,
            "total_opponent_injured_players": total_opponent_injured_players,
            "utah_abbreviation": utah_abbreviation,
            "opponent_abbreviation": opponent_abbreviation,
            "win_probability": win_probability,
            "utah_name": utah_name,
            "opponent_name": opponent_name,
            "utah_dark_logo": utah_dark_logo,
            "utah_light_logo": utah_light_logo,
            "opponent_light_logo": opponent_light_logo,
            "opponent_dark_logo": opponent_dark_logo,
            "venue": venue,
            "start_date": start_date,
            "start_time": start_time,
            "utah_record": utah_record,
            "opponent_record": opponent_record,
        },
    )


def format_game_time(utc_string):
    dt = datetime.fromisoformat(utc_string.replace("Z", "+00:00"))
    mt = dt.astimezone(ZoneInfo("America/Denver"))
    date = mt.strftime("%-m-%-d-%Y")
    time = mt.strftime("%-I:%M%p MST")
    return date, time
