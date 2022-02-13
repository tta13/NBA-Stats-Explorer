import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from PIL import Image

script_directory = os.getcwd()
baseUrl = 'https://www.basketball-reference.com/leagues/NBA_'
stat_types = ['per_game', 'totals', 'per_minute', 'advanced']
best_players = ['Nikola Jokić', 'Joel Embiid', 'James Harden', 'Stephen Curry', 'Kevin Durant', 'LeBron James', 'Giannis Antetokounmpo', 
    'Kareem Abdul-Jabbar', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan', 'Dirk Nowitzki', 'Wilt Chamberlain',
    'Shaquille O\'Neal', 'Carmelo Anthony', 'Moses Malone', 'Elvin Hayes', 'Hakeem Olajuwon', 'Oscar Robertson',
    'Dominique Wilkins', 'Tim Duncan', 'Paul Pierce', 'John Havlicek', 'Kevin Garnett', 'Vince Carter',
    'Alex English', 'Reggie Miller', 'Jerry West', 'Patrick Ewing', 'Ray Allen', 'Allen Iverson']

# Web scraping of NBA player stats
@st.cache
def load_data(year, stat_type, header = 0):
    url = baseUrl + str(year) + '_' + stat_type + '.html'
    html = pd.read_html(url, header = header)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)

    cols=[i for i in playerstats.columns if i not in ['Player','Pos', 'Tm']]
    for col in cols:
        try:
            playerstats[col]=pd.to_numeric(playerstats[col])
        except ValueError:
            playerstats[col]=playerstats[col]
    return playerstats

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

def translate_stat_type(stat_type):
    if stat_type == 'per_game':
        return 'Per Game'
    elif stat_type == 'totals':
        return 'Total'
    elif stat_type == 'per_minute':
        return 'Per 36 Minutes'
    elif stat_type == 'advanced':
        return 'Advanced'
    return 'None'

def gen_on_off_stats(selected_year):
    st.header('Impact metrics')
    play_by_play = load_data(selected_year, 'play-by-play', 1)
    advanced_stats = load_data(selected_year, 'advanced')

    #Filtering games
    max_games_played = play_by_play['G'].max()
    threshold = int(max_games_played / 2)
    
    play_by_play = play_by_play[play_by_play['G'] >= threshold]

    advanced_stats = advanced_stats[advanced_stats['G'] >= threshold]

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
        elif player + '*' in play_by_play.Player.values:                
            x = -.2498
            y = play_by_play[play_by_play.Player==player + '*']['On-Off']           
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        else:
            continue

    for player in best_players:
        if player in play_by_play.Player.values:
            x = .002
            y = play_by_play[play_by_play.Player==player]['OnCourt']
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        elif player + '*' in play_by_play.Player.values:                
            x = .002
            y = play_by_play[play_by_play.Player==player + '*']['OnCourt']           
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        else:
            continue

    for player in best_players:
        if player in advanced_stats.Player.values:
            x = .2502
            y = advanced_stats[advanced_stats.Player==player]['BPM']
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        elif player + '*' in advanced_stats.Player.values:                
            x = .2502
            y = advanced_stats[advanced_stats.Player==player + '*']['BPM']           
            if y.iloc[0] > 0:
                plt.text(x, y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
        else:
            continue

    st.pyplot()


def main():    
    st.set_option('deprecation.showPyplotGlobalUse', False)
    icon = Image.open(os.path.join(script_directory, 'favicon.ico'))
    st.set_page_config('NBA Stats Explorer', icon)


    st.markdown('<img src=\"https://cdn.nba.com/logos/nba/nba-logoman-75-word_white.svg\" alt=\"NBA logo\" style=\"width:150px\"> ' , 
        unsafe_allow_html=True)
    st.title('NBA Stats Explorer')

    st.markdown("""
      This app performs simple webscraping of NBA player stats data!
    * **Python libraries:** base64, pandas, streamlit
    * **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
    """)

    st.sidebar.header('User Input Features')
    selected_year = st.sidebar.selectbox('Year', list(reversed(range(1977,2023))))
    selected_stat = st.sidebar.selectbox('Player Stats', stat_types, format_func=translate_stat_type)
    playerstats = load_data(selected_year, selected_stat)

    # Sidebar - Team selection
    sorted_unique_team = sorted(playerstats.Tm.unique())
    selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

    # Sidebar - Position selection
    unique_pos = ['C','PF','SF','PG','SG']
    selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

    # Filtering data
    df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

    st.header('Displaying Players\' ' + translate_stat_type(selected_stat) + ' Stats of Selected Team(s)')
    st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
    st.dataframe(df_selected_team)

    st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)


    col1, col2, col3 = st.columns(3)

    show_plot = 0

    with col1:
        # Heatmap
        if st.button('Intercorrelation Heatmap'):
            show_plot = 1            
    with col2:
        # Scatter plot
        if st.button('Points per 75 x TS% Scattergram'):
            show_plot = 2
    if(selected_year >= 1997):
        with col3:
            # Scatter plot
            if st.button('Impact Metrics'):
                show_plot = 3   
        
    
    if show_plot == 1:
        st.header('Intercorrelation Matrix Heatmap')
        df_selected_team.to_csv('output.csv',index=False)
        df = pd.read_csv('output.csv')

        corr = df.corr()
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        with sns.axes_style("white"):
            f, ax = plt.subplots(figsize=(7, 5))
            ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
        st.pyplot()
    elif show_plot == 2:        
        st.header('Points per 75 x TS% Scatter Plot')
        per_100_stats = load_data(selected_year, 'per_poss')
        advanced_stats = load_data(selected_year, 'advanced')

        #Filtering games
        max_games_played = per_100_stats['G'].max()
        threshold = int(max_games_played / 2)
        # print(threshold)
        per_100_stats = per_100_stats[per_100_stats['G'] >= threshold]
        # Calculating points per 75 
        per_100_stats['PTS'] = per_100_stats['PTS'].apply(lambda x: x*.75)
        per_75_stats = per_100_stats

        advanced_stats = advanced_stats[advanced_stats['G'] >= threshold]

        plt.style.use('seaborn')
        plt.xlabel("Pts. per 75")
        plt.ylabel("TS%")
        plt.scatter(per_75_stats.PTS.values, advanced_stats['TS%'].values, edgecolors='k', alpha=.5)
        plt.xlim([0, 40])

        for player in best_players:
            if player in per_75_stats.Player.values:
                x = per_75_stats.PTS[per_75_stats.Player==player]
                y = advanced_stats[advanced_stats.Player==player]['TS%']
                plt.text(x.iloc[0], y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
            elif player + '*' in per_75_stats.Player.values:                
                x = per_75_stats.PTS[per_75_stats.Player==player + '*']
                y = advanced_stats[advanced_stats.Player==player + '*']['TS%']           
                plt.text(x.iloc[0], y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
            else:
                continue

        st.pyplot()
    elif show_plot == 3:
        gen_on_off_stats(selected_year)
    else:
        pass

if __name__ == '__main__':
    main()
