import plotly.graph_objects as go
import plotly.offline as pyo


def gather_data():
    data = nhl_api.get_all_info()
    return data


def build_goals_graph(data):
    dates = list(data.keys())
    goals_scored = [v["total_goals_scored"] for v in data.values()]
    goals_allowed = [v["total_goals_allowed"] for v in data.values()]
    goals_scored.reverse()
    goals_allowed.reverse()
    dates.reverse()
    game_numbers = list(range(1, len(dates) + 1))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=game_numbers,
            y=goals_scored,
            name="Scored",
            marker_color="#12e383",  # green
            customdata=dates,
            hovertemplate="Date: %{customdata}<br>Goals Scored: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=game_numbers,
            y=goals_allowed,
            name="Allowed",
            marker_color="#f00d0d",  # red
            customdata=dates,
            hovertemplate="Date: %{customdata}<br>Goals Allowed: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Goals Scored vs. Goals Allowed",
        barmode="group",
        template="plotly_dark",
        xaxis=dict(
            tickmode="array",
            tickvals=game_numbers,
            ticktext=[f"G{n}" for n in game_numbers],
        ),
    )
    return fig.to_json()


def build_all_graphs(data):
    output = {}
    utah_goals_graph = build_goals_graph(data["utah_game_output"])
    opponent_goals_graph = build_goals_graph(data["opponent_game_output"])
    output["utah_goals_graph"] = utah_goals_graph
    output["opponent_goals_graph"] = opponent_goals_graph
    return output


if __name__ == "__main__":
    build_all_graphs()
