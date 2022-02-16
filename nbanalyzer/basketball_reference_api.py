from math import exp
import pandas as pd
from streamlit import cache

base_url = 'https://www.basketball-reference.com/'
stat_types = ['per_game', 'totals', 'per_minute', 'advanced', 'per_poss', 'play-by-play', 'advanced_box_score']

@cache
def get_players_data(season: int, stat_type: str, header: int = 0, filter_games=True) -> pd.DataFrame:
    """
    Returns a dataframe representing player data from the season and stat type selected web scrapping basketball reference website
    """
    url = f'{base_url}leagues/NBA_{str(season)}_{stat_type}.html'
    print(f'GET {url}')
    html = pd.read_html(url, header = header)
    df = html[0]

    raw = None
    if 'Age' in df:
        raw = df.drop(df[df.Age == 'Age'].index)
        raw = raw.fillna(0)
    
    player_stats = raw.drop(['Rk'], axis=1) if raw is not None else df.drop(['Rk'])

    cols=[i for i in player_stats.columns if i not in ['Player','Pos', 'Tm']]
    for col in cols:
        try:
            player_stats[col]=pd.to_numeric(player_stats[col])
        except ValueError:
            player_stats[col]=player_stats[col]
    
    if filter_games:
        max_games_played = player_stats['G'].max()
        threshold = max_games_played // 2   
        player_stats = player_stats[player_stats['G'] >= threshold]

    return player_stats

@cache
def get_mvp_voting(season: int, top=10) -> list:
    """
    Returns top mvp candidates from season
    """
    url = f'{base_url}awards/awards_{str(season)}.html#mvp'
    html = pd.read_html(url, header = 1)
    df = html[0]
    player_stats = df.drop(['Rank'], axis=1)

    if top > 0:
        return player_stats[:top]['Player']
    return list(player_stats.Player.values)

@cache
def get_advanced_metrics(season: int) -> pd.DataFrame:
    per_100 = get_players_data(season, 'per_poss')
    advanced = get_players_data(season, 'advanced')
    per_game = get_players_data(season, 'per_game')
    league_avg_efg = per_game['eFG%'].mean()

    cols = ['Player','Pos','Tm','Scoring','Efficiency(TS%)','Spacing','Creation','Off. Load']
    table = [[p,pos,tm,pts,ts,spacing(attmpts,pctg,league_avg_efg),box_creation(ast,pts,attmpts,pctg,tov),offensive_load(ast,fga,fta,tov,box_creation(ast,pts,attmpts,pctg,tov))] 
        for p,pos,tm,pts,ts,attmpts,pctg,ast,tov,fga,fta 
        in zip(per_100['Player'],per_100['Pos'],per_100['Tm'],per_100['PTS'],advanced['TS%'],per_100['3PA'],per_100['3P%'],per_100['AST'],per_100['TOV'],per_100['FGA'],per_100['FTA'])]
    return pd.DataFrame(table, columns=cols)    

def spacing(attemps: float, percentage: float, league_avg_efg: float) -> float:
    """
    (3PA * (3P% * 1.5)) - EFG% =
    A measure of shooting quality that takes into account both attempts as well as accuracy, with a slight adjustment towards attempts.
    """
    return (attemps * (percentage * 1.5)) - league_avg_efg

def shooting_proficiency(attempts: float, percentage: float) -> float:
    """
    A measure of shooting quality that takes into account both attempts as well as accuracy.
    """
    return (2/(1+exp(-attempts))-1)*percentage

def box_creation(ass_per_100: float, pts_per_100: float, attempts: float, percentage: float, turnovers_per_100: float) -> float:
    """
    A per 100 estimate of the number of \'true\' shots created for teammates
    """
    proficiency = shooting_proficiency(attempts, percentage)
    return ass_per_100*0.1843+(pts_per_100+turnovers_per_100)*0.0969-2.3021*(proficiency)+0.0582*(ass_per_100*(pts_per_100+turnovers_per_100)*proficiency)-1.1942

def offensive_load(ass: float, field_goals: float, free_throws: float, turnovers: float, box_creation: float) -> float:
    """
    The percentage of possessions a player is directly or indirectly involved in a true shooting attempt, or commits a turnover.
    """
    return ((ass-(0.38*box_creation))*0.75) + field_goals + free_throws*0.44 + box_creation + turnovers
