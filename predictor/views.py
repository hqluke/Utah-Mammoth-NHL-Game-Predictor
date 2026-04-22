from django.shortcuts import render
from predictor.services import graph_builder
from predictor.services import nhl_api

# Create your views here.


def index(request):
    data = nhl_api.get_all_info()
    goals_graph = graph_builder.build_all_graphs(data)
    utah_goals_graph = goals_graph["utah_goals_graph"]
    opponent_goals_graph = goals_graph["opponent_goals_graph"]
    predicted_score = data["predicted_score"]
    return render(
        request,
        "index/index.html",
        {
            "utah_goals_graph": utah_goals_graph,
            "opponent_goals_graph": opponent_goals_graph,
            "predicted_score": predicted_score,
        },
    )
