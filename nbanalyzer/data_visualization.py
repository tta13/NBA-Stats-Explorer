import copy
from pandas import DataFrame
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from .basketball_reference_api import *


def gen_scoring_efficiency_plot(season: int, best_players: list[str]) -> go.Figure:
    """
    Generates points per 75 x TS% plot
    """
    per_100_stats = copy.deepcopy(get_players_data(season, 'per_poss'))
    advanced_stats = get_players_data(season, 'advanced')
    
    # Calculating points per 75 
    per_100_stats['PTS'] = per_100_stats['PTS'].apply(lambda x: x*.75)
    per_75_stats = per_100_stats

    
    # Plottings data
    fig = px.scatter(x=per_75_stats.PTS.values, y=advanced_stats['TS%'].values,
                     range_x=[0, 40],
                     opacity=.65,
                     template="plotly_dark",
                     hover_name=per_75_stats.Player.values)
    
    fig.update_traces(marker=dict(color="#2a87df"))

    
    fig.add_hline(y=advanced_stats['TS%'].mean(), 
                  line_width=2, 
                  line_dash="dash", 
                  line_color="gray",
                  opacity=.5,
                  annotation_text="League Avg.",
                  annotation_position="bottom right")

    fig.update_xaxes(
        title_text = "Pts. per 75",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showline = True,
        showticklabels = True,
        zeroline = True
    )

    fig.update_yaxes(
        title_text = "TS%",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showline = True,
        showticklabels = True,
        zeroline = True
    )

    return fig

def gen_on_off_plot(season: int, best_players: list[str]) -> go.Figure:
    """
    Generates On-Off, OnCourt and BPM plots
    """
    play_by_play = get_players_data(season, 'play-by-play', 1)
    advanced_stats = get_players_data(season, 'advanced')

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=np.full_like(play_by_play['On-Off'].values, -.25), 
                             y=play_by_play['On-Off'].values,
                             mode='markers', name='On-Off',
                             opacity=.75,
                             hovertext=play_by_play.Player.values))
    
    fig.add_trace(go.Scatter(x=np.zeros_like(play_by_play['OnCourt'].values), 
                             y=play_by_play['OnCourt'].values,
                             mode='markers', name='OnCourt',
                             opacity=.75,
                             hovertext=play_by_play.Player.values))

    
    fig.add_trace(go.Scatter(x=np.full_like(advanced_stats.BPM.values, .25), 
                             y=advanced_stats.BPM.values,
                             mode='markers', name='BPM',
                             opacity=.75,
                             hovertext=play_by_play.Player.values))
    fig.update_xaxes(
        showgrid = False,
        showline = False,
        showticklabels = False,
        zeroline = False
    )

    fig.update_yaxes(
        title_text = "Plus/Minus",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showticklabels = True,
        zeroline = False
    )

    fig.update_layout(xaxis_range=[-.5,.5], yaxis_range=[0.,25.], height=680)
    
    return fig

def draw_intercorrelation_heatmap(season: int):
    """
    Generates intercorrelation heatmap from stats
    """
    df_selected_team = get_players_data(season, 'per_game')

    corr = df_selected_team.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
