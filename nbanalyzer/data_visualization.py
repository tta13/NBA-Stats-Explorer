import copy
from pandas import DataFrame
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from .basketball_reference_api import *

SCORING_PLOT_COLOR = '#2a87df'
SHOOTING_PLOT_COLOR = '#6cc644'
PLAYMAKING_PLOT_COLOR = '#f5982c'

def gen_scoring_efficiency_plot(season: int, best_players: list[str]) -> go.Figure:
    """
    Generates points per 75 x TS% plot
    """
    per_100_stats = copy.deepcopy(get_players_data(season, 'per_poss'))
    advanced_stats = get_players_data(season, 'advanced')
    
    # Calculating points per 75 
    per_100_stats['PTS'] = per_100_stats['PTS'].apply(lambda x: x*.75)
    per_75_stats = per_100_stats    
    avg_ts_percentage = round(advanced_stats['TS%'].mean(), 3)
    
    # Plottings data
    fig = px.scatter(x=per_75_stats.PTS.values, y=advanced_stats['TS%'].values,
                     range_x=[0, 40],
                     opacity=.65,
                     template="plotly_dark",
                     hover_name=per_75_stats.Player.values)
    
    fig.update_traces(marker=dict(color=SCORING_PLOT_COLOR))

    
    fig.add_hline(y=avg_ts_percentage, 
                  line_width=2, 
                  line_dash="dash", 
                  line_color="gray",
                  opacity=.5,
                  annotation_text=f"League Avg.={avg_ts_percentage}",
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

def gen_shooting_efficiency_plot(season: int, minimum_attempts=2) -> go.Figure:
    """
    Generates 3PA per 100 possessions x 3P% plot
    """
    per_100_stats = copy.deepcopy(get_players_data(season, 'per_poss'))
    per_100_stats = per_100_stats[per_100_stats['3PA'] >= minimum_attempts]
    avg_3p_percentage = round(per_100_stats['3P%'].mean(), 3)
    
    # Plottings data
    fig = px.scatter(data_frame=per_100_stats,
                     x='3PA',
                     y='3P%',
                     opacity=.65,
                     template="plotly_dark",
                     hover_name='Player')
    
    fig.update_traces(marker=dict(color=SHOOTING_PLOT_COLOR))

    fig.add_hline(y=avg_3p_percentage, 
                  line_width=2,
                  line_dash="dash", 
                  line_color="gray",
                  opacity=.5,
                  annotation_text=f"League Avg.={avg_3p_percentage}",
                  annotation_position="bottom right")

    fig.update_xaxes(
        title_text = "3-Point Attempts per 100",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showline = True,
        showticklabels = True,
        zeroline = True
    )

    fig.update_yaxes(
        title_text = "3P%",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showline = True,
        showticklabels = True,
        zeroline = True
    )

    return fig

def gen_playmaking_plot(season: int) -> go.Figure:
    """
    Generates Box Creation x Offensive Load% plot
    """
    advanced_box_score = get_advanced_metrics(season)
    
    # Plottings data
    fig = px.scatter(data_frame=advanced_box_score,
                     x='Offensive Load',
                     y='Creation',
                     opacity=.65,
                     template="plotly_dark",
                     hover_name='Player')
    
    fig.update_traces(marker=dict(color=PLAYMAKING_PLOT_COLOR))

    fig.update_xaxes(
        title_text = "Offensive Load",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showline = True,
        showticklabels = True,
        zeroline = True
    )

    fig.update_yaxes(
        title_text = "Box Creation",
        title_font = {"size": 15},
        title_standoff = 20,
        showgrid = True,
        showline = True,
        showticklabels = True,
        zeroline = True
    )

    return fig

def get_player_percentile_from_advanced_stat(df: DataFrame, player: str, stat: str) -> float:
    advanced_box_score = df
    temp = advanced_box_score[f'{stat}'].rank(method='max', pct=True)
    temp = temp.to_frame()
    temp['Player'] = advanced_box_score['Player']
    temp = temp.loc[temp['Player'].str.match(player)]
    return temp
