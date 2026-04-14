from django.contrib import admin
from .models import Team, Game, GamePrediction

admin.site.register(Team)
admin.site.register(Game)
admin.site.register(GamePrediction)
