import matplotlib.pyplot as plt
from pandas import DataFrame
import numpy as np
import seaborn as sns
import copy
from .basketball_reference_api import *

def add_player_labels(players: list[str], df1: DataFrame, df2: DataFrame, x_data: str, y_data: str, x_offset: float = 0., y_offset: float = 0.):
    for player in players:
        if player in df1.Player.values:
            x = df1[df1.Player==player][x_data]
            y = df2[df2.Player==player][y_data]
            plt.text(x.iloc[0] + x_offset, y.iloc[0] + y_offset, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        elif player + '*' in df1.Player.values:                
            x = df1[df1.Player==player + '*'][x_data]
            y = df2[df2.Player==player + '*'][y_data]           
            plt.text(x.iloc[0] + x_offset, y.iloc[0] + y_offset, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        else:
            continue

def gen_scoring_efficiency_plot(season: int, best_players: list[str]):
    """
    Generates points per 75 x TS% plot
    """
    per_100_stats = copy.deepcopy(get_players_data(season, 'per_poss'))
    advanced_stats = get_players_data(season, 'advanced')
    
    # Calculating points per 75 
    per_100_stats['PTS'] = per_100_stats['PTS'].apply(lambda x: x*.75)
    per_75_stats = per_100_stats

    plt.style.use('seaborn')
    plt.xlabel("Pts. per 75")
    plt.ylabel("TS%")
    plt.axhline(y=advanced_stats['TS%'].mean(), linestyle='--', color='gray', alpha=.4 ,label='League Avg.')
    plt.scatter(per_75_stats.PTS.values, advanced_stats['TS%'].values, edgecolors='k', alpha=.5)
    plt.xlim([0,40])
    plt.legend(frameon=True, edgecolor='black')

    add_player_labels(best_players, per_75_stats, advanced_stats, 'PTS', 'TS%', y_offset=.002)

def gen_on_off_plot(season: int, best_players: list[str]):
    """
    Generates On-Off, OnCourt and BPM plots
    """
    play_by_play = get_players_data(season, 'play-by-play', 1)
    advanced_stats = get_players_data(season, 'advanced')

    plt.style.use('seaborn')
    plt.ylabel('Plus/Minus')
    plt.plot(np.zeros_like(play_by_play['On-Off'].values) -.25, play_by_play['On-Off'].values, alpha=.5, marker='o', linestyle='')    
    plt.plot(np.zeros_like(play_by_play['OnCourt'].values), play_by_play['OnCourt'].values, alpha=.5, marker='o', linestyle='')
    plt.plot(np.zeros_like(advanced_stats.BPM.values) + .25, advanced_stats.BPM.values, alpha=.5, marker='o', linestyle='')
    plt.ylim(bottom=0)
    plt.xlim([-.5,.5])
    plt.xticks([-.25, 0, .25], ['On-Off', 'OnCourt', 'BPM'])
    
    for player in best_players:
        if player in play_by_play.Player.values:
            x = -.2498
            y = play_by_play[play_by_play.Player==player]['On-Off']
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))

            x = .002
            y = play_by_play[play_by_play.Player==player]['OnCourt']
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))

            x = .2502
            y = advanced_stats[advanced_stats.Player==player]['BPM']
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        elif player + '*' in play_by_play.Player.values:                
            x = -.2498
            y = play_by_play[play_by_play.Player==player + '*']['On-Off']           
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))

            x = .002
            y = play_by_play[play_by_play.Player==player + '*']['OnCourt']           
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))

            x = .2502
            y = advanced_stats[advanced_stats.Player==player + '*']['BPM']           
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        else:
            continue

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
