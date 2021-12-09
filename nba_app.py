import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image


baseUrl = 'https://www.basketball-reference.com/leagues/NBA_'
stat_types = ['per_game', 'totals', 'per_minute', 'advanced']
best_players = ['James Harden', 'Stephen Curry', 'Kevin Durant', 'LeBron James', 'Giannis Antetokounmpo', 
    'Kareem Abdul-Jabbar', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan', 'Dirk Nowitzki', 'Wilt Chamberlain',
    'Shaquille O\'Neal', 'Carmelo Anthony', 'Moses Malone', 'Elvin Hayes', 'Hakeem Olajuwon', 'Oscar Robertson',
    'Dominique Wilkins', 'Tim Duncan', 'Paul Pierce', 'John Havlicek', 'Kevin Garnett', 'Vince Carter',
    'Alex English', 'Reggie Miller', 'Jerry West', 'Patrick Ewing', 'Ray Allen', 'Allen Iverson']

# Web scraping of NBA player stats
@st.cache
def load_data(year, stat_type):
    url = baseUrl + str(year) + '_' + stat_type + '.html'
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)

    cols=[i for i in playerstats.columns if i not in ['Player','Pos', 'Tm']]
    for col in cols:
        playerstats[col]=pd.to_numeric(playerstats[col])
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

def main():    
    st.set_option('deprecation.showPyplotGlobalUse', False)
    icon = Image.open(r"D:\Documentos\Git\Github\NBA-stats-explorer\favicon.ico")
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
    selected_year = st.sidebar.selectbox('Year', list(reversed(range(1970,2023))))
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


    col1, col2 = st.columns(2)

    show_plot = 0

    with col1:
        # Heatmap
        if st.button('Intercorrelation Heatmap'):
            show_plot = 1            
    with col2:
        # Scatter plot
        if st.button('Points per 36 x TS% Scattergram'):
            show_plot = 2
    
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
        st.header('Points per 36 x TS% Scatter Plot')
        per_36_stats = load_data(selected_year, 'per_minute')
        advanced_stats = load_data(selected_year, 'advanced')

        #Filtering games
        max_games_played = per_36_stats['G'].max()
        threshold = int(max_games_played / 2)
        print(threshold)
        per_36_stats = per_36_stats[per_36_stats['G'] >= threshold]
        advanced_stats = advanced_stats[advanced_stats['G'] >= threshold]

        plt.style.use('seaborn')
        plt.xlabel("Pts. per 36")
        plt.ylabel("TS%")
        plt.scatter(per_36_stats.PTS.values, advanced_stats['TS%'].values, edgecolors='k', alpha=.5)
        plt.xlim([0, 40])

        for player in best_players:
            if player in per_36_stats.Player.values:
                x = per_36_stats.PTS[per_36_stats.Player==player]
                y = advanced_stats[advanced_stats.Player==player]['TS%']
                plt.text(x.iloc[0], y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
            elif player + '*' in per_36_stats.Player.values:                
                x = per_36_stats.PTS[per_36_stats.Player==player + '*']
                y = advanced_stats[advanced_stats.Player==player + '*']['TS%']           
                plt.text(x.iloc[0], y.iloc[0] + .002, player.split()[1], fontdict=dict(color='black', alpha=0.5))
            else:
                continue

        st.pyplot()
    else:
        pass

if __name__ == '__main__':
    main()
