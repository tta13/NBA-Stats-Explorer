import streamlit as st
import base64
import os
from nbanalyzer import *
from PIL import Image

script_directory = os.getcwd()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def load_data(year: int, stat_type: str):
    if stat_type == 'play-by-play':
        return get_players_data(year, stat_type, 1)

    return get_players_data(year, stat_type, 0)

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
    elif stat_type == 'per_poss':
        return 'Per 100 Possessions'    
    elif stat_type == 'play-by-play':
        return 'Play-by-Play'
    return 'None'

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

    if selected_year < 2022:
        best_players = get_mvp_voting(selected_year)
    else:
        best_players = ['Nikola Jokić', 'Joel Embiid', 'Chris Paul', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo',
            'Ja Morant', 'Luka Dončić', 'Devin Booker', 'DeMar DeRozan', 'Jimmy Butler']
    
    with st.spinner('Loading season summary...'):
        st.header(f'{selected_year} Season Summary')
        st.write(f"""
            The {selected_year} season was the {ordinal(selected_year - 1946)} of the [National Basketball Association](https://en.wikipedia.org/wiki/National_Basketball_Association). 
            As usual, we have to analyze its vast data and explore player performances to decide which players performed the best!
        """)

        if selected_year < 2022:
            with st.expander(f'{selected_year} NBA MVP'):
                st.write(f"""
                    ### MVP
                    This season's MVP was **{best_players[0]}** who won the prize against the likes of {best_players[1]}, {best_players[2]}
                    and {best_players[3]}.
                """)

        with st.expander(f'Intercorrelation Matrix Heatmap - {selected_year}'):
            st.markdown("""
                ### Intercorrelation Matrix Heatmap
                The matrix is calculated from a cross-tabulation and shows how statistically similar all pairs of variables are in their 
                distributions across the various samples. The table below shows the intercorrelations between per game player stats.
            """)
            with st.spinner('Loading heatmap...'):
                draw_intercorrelation_heatmap(selected_year)
                st.pyplot()

        with st.expander(f'Scoring - {selected_year}'):
            st.markdown("""
                ### Points per 75 possessions x TS% Scatter Plot
                The scatter plot is used to analyze the relation between \"inflation adjusted\" scoring and efficiency from players across the league, 
                highlighting the top 10 MVP candidates.
            """)
            with st.spinner('Loading scatter plot'):
                gen_scoring_efficiency_plot(selected_year, best_players)        
                st.pyplot()

        if(selected_year >= 1997):
            with st.expander(f'Impact - {selected_year}'):
                st.markdown("""
                    ### Impact metrics
                    Impact metrics are used to measure a player's impact on the success of a given team. In this selection:
                    * **On-Off**: Average difference between the Plus/Minus when player is on the court vs. off the court.
                    * **OnCourt**: Plus/Minus Per 100 Possessions (On Court only).
                    * **BPM**: A box score estimate of the points per 100 possessions a player contributed above a league-average player, translated to an average team.
                    PS: highlighting top MVP cadidates.
                """)
                gen_on_off_plot(selected_year, best_players)
                st.pyplot()

if __name__ == '__main__':
    main()
