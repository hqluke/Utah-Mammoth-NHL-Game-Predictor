import plotly.graph_objects as go
import plotly.offline as pyo
from predictor.services import nhl_api

def gather_data():
    data = nhl_api.get_all_info()
    return data

def build_graph():

