from django.db import models


class Team(models.Model):
    team_id = models.IntegerField(primary_key=True)  # use NHL API's ID
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5)
    logo_url = models.URLField()


class Game(models.Model):
    game_id = models.IntegerField(primary_key=True)  # NHL API game ID
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_games"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_games"
    )
    game_date = models.DateTimeField()
    completed = models.BooleanField(default=False)


class GamePrediction(models.Model):
    game = models.OneToOneField(
        Game, on_delete=models.CASCADE, related_name="prediction"
    )
    utah_win_pct = models.FloatField()
    predicted_home_score = models.FloatField(null=True, blank=True)
    predicted_away_score = models.FloatField(null=True, blank=True)
    utah_won = models.BooleanField(null=True)  # null until game finishes
    prediction_correct = models.BooleanField(null=True)
    # stores the entire data object from the NHL API
    cached_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
