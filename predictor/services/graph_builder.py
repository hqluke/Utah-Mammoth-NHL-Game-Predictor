import plotly.graph_objects as go
import plotly.offline as pyo


def gather_data():
    data = nhl_api.get_all_info()
    return data


def build_goals_graph(
    data, abbrev, goal_scored_color="#7ab3e2", goal_allowed_color="#ffffff"
):
    dates = list(data.keys())
    goals_scored = [v["total_goals_scored"] for v in data.values()]
    goals_allowed = [v["total_goals_allowed"] for v in data.values()]
    opponents = [v["opponent_abbrev"] for v in data.values()]
    opponents.reverse()
    goals_scored.reverse()
    goals_allowed.reverse()
    dates.reverse()
    game_numbers = list(range(1, len(dates) + 1))

    def fmt(d):
        from datetime import datetime

        return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d")

    tick_labels = [fmt(d) for d in dates]
    tick_labels[-1] = f"{tick_labels[-1]} ◀ Latest"

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=game_numbers,
            y=goals_scored,
            name="Scored",
            marker_color=goal_scored_color,
            customdata=list(zip(dates, opponents)),
            hovertemplate="Date: %{customdata[0]}<br>vs: %{customdata[1]}<br>Goals Scored: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=game_numbers,
            y=goals_allowed,
            name="Allowed",
            marker_color=goal_allowed_color,
            customdata=list(zip(dates, opponents)),
            hovertemplate="Date: %{customdata[0]}<br>vs: %{customdata[1]}<br>Goals Allowed: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text=f"{abbrev} Goals Scored vs. Goals Allowed in past games", x=0.5
        ),
        barmode="group",
        template="plotly_dark",
        xaxis=dict(
            tickmode="array",
            tickvals=game_numbers,
            ticktext=tick_labels,
        ),
    )
    return fig.to_json()


def build_performance_graph(data, game_ratings, abbrev, bar_color="#7ab3e2"):
    dates = list(data.keys())
    dates.reverse()
    scores = [r["score"] for r in game_ratings]
    vs_avg = [r["vs_average"] for r in game_ratings]
    ratings = [r["rating"] for r in game_ratings]
    opponents = [v["opponent_abbrev"] for v in data.values()]
    opponents.reverse()
    scores.reverse()
    vs_avg.reverse()
    ratings.reverse()

    game_numbers = list(range(1, len(dates) + 1))

    # Short date labels e.g. "Apr 7" with "Apr 21 (Latest)" on the last
    def fmt(d):
        from datetime import datetime

        dt = datetime.strptime(d, "%Y-%m-%d")
        return dt.strftime("%b %-d")

    tick_labels = [fmt(d) for d in dates]
    tick_labels[-1] = f"{tick_labels[-1]} ◀ Latest"  # mark most recent

    colors = []
    for r in ratings:
        if r == "good":
            colors.append("#4caf50")
        elif r == "average":
            colors.append("#ff9800")
        else:
            colors.append("#f44336")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=game_numbers,
            y=scores,
            name="Performance Score",
            marker_color=colors,
            customdata=list(zip(dates, vs_avg, ratings, opponents)),
            hovertemplate=(
                "Date: %{customdata[0]}<br>"
                "vs: %{customdata[3]}<br>"
                "Score: %{y}<br>"
                "vs Average: %{customdata[1]}%<br>"
                "Rating: %{customdata[2]}<extra></extra>"
            ),
        )
    )
    # 0.5 average line
    fig.add_hline(
        y=0.5,
        line_dash="dash",
        line_color="white",
        annotation_text="Average",
        annotation_position="right",
    )
    fig.update_layout(
        title=dict(text=f"{abbrev} Game Performance Rating", x=0.5),
        template="plotly_dark",
        xaxis=dict(
            tickmode="array",
            tickvals=game_numbers,
            ticktext=tick_labels,
        ),
        yaxis=dict(range=[0, 1]),
    )
    return fig.to_json()


def build_all_graphs(data):
    output = {}
    output["utah_goals_graph"] = build_goals_graph(
        data["utah_game_output"], data["utah"]["abbrev"]
    )
    output["opponent_goals_graph"] = build_goals_graph(
        data["opponent_game_output"], data["opponent"]["abbrev"], "#de1a24"
    )
    output["utah_performance_graph"] = build_performance_graph(
        data["utah_game_output"], data["utah_game_ratings"], data["utah"]["abbrev"]
    )
    output["opponent_performance_graph"] = build_performance_graph(
        data["opponent_game_output"],
        data["opponent_game_ratings"],
        data["opponent"]["abbrev"],
        "#de1a24",
    )
    return output
