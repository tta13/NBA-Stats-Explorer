import pandas as pd

base_url = 'https://www.basketball-reference.com/'
stat_types = ['per_game', 'totals', 'per_minute', 'advanced', 'play-by-play', 'per_poss']

def get_players_data(season: int, stat_type: str, header: int = 0, filter_games=True) -> pd.DataFrame:
    """
    Returns a dataframe representing player data from the season and stat type selected web scrapping basketball reference website
    """
    url = f'{base_url}/leagues/NBA_{str(season)}_{stat_type}.html'
    html = pd.read_html(url, header = header)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    player_stats = raw.drop(['Rk'], axis=1)

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

def get_mvp_voting(season: int, top=10) -> list:
    """
    Returns top mvp candidates from season
    """
    url = f'{base_url}awards/awards_{str(season)}.html#mvp'
    html = pd.read_html(url, header = 1)
    df = html[0]
    player_stats = df.drop(['Rank'], axis=1)

    cols=[i for i in player_stats.columns if i not in ['Player','Pos', 'Tm']]
    for col in cols:
        try:
            player_stats[col]=pd.to_numeric(player_stats[col])
        except ValueError:
            player_stats[col]=player_stats[col]
    return player_stats
