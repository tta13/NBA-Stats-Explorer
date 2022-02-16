import streamlit as st
import base64
import os
from nbanalyzer import *
from PIL import Image
import time

script_directory = os.getcwd()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def load_data(year: int, stat_type: str):
    if stat_type == 'play-by-play':
        return get_players_data(year, stat_type, 1)
    elif stat_type == 'advanced_box_score':
        return get_advanced_metrics(year)

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
    elif stat_type == 'advanced_box_score':
        return 'Advanced Box Score'
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
    * **Python libraries:** base64, matplotlib, pandas, plotly, streamlit
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
        best_players = get_mvp_voting(selected_year, 5)
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
                The scatter plot is used to analyze the relation between \"inflation adjusted\" scoring and efficiency from players across the league.
            """)
            with st.spinner('Loading scatter plot'):                       
                st.write(gen_scoring_efficiency_plot(selected_year, best_players))

        if selected_year >= 1980:
            with st.expander(f'Shooting - {selected_year}'):
                st.markdown("""
                    ### 3-Point Attempts x 3P% Scatter Plot
                    The scatter plot is used to analyze the relation between 3-Point Field Goal attempts per 100 possessions and 3-Point Field Goal 
                    Percentage from players across the league as well as observe the evolution of shooting along the decades.
                """)
                with st.spinner('Loading scatter plot'):                       
                    st.write(gen_shooting_efficiency_plot(selected_year))

            with st.expander(f'Playmaking - {selected_year}'):
                st.markdown("""
                    ### Box Creation x Offensive Load Scatter Plot
                    The scatter plot is used to analyze the relation between a per 100 estimate of the number of true shots created for teammates and 
                    the percentage of possessions a player is directly or indirectly involved in a true shooting attempt, or commits a turnover.
                """)
                with st.spinner('Loading scatter plot'):                       
                    st.write(gen_playmaking_plot(selected_year))
            
            with st.expander('Player Finder'):
                st.markdown("""
                    ### Player Finder
                    Player Finder is a tool to explore the database and see how specific players are performing relative to the league in 5 major categories 
                    **Scoring, Efficiency, Shooting, Creation and Load**. Try it out and see how your favorite NBA star is doing :triumph::basketball:.
                """)
                advanced_box_score = get_advanced_metrics(selected_year)
                selected_option = st.selectbox('Player Name', advanced_box_score['Player'])
                
                showed_name = False
                
                if selected_option != '':
                    with st.spinner('Loading player summary'):
                        for stat in ['Scoring','Efficiency(TS%)','Spacing','Creation','Offensive Load']:
                            result = get_player_percentile_from_advanced_stat(advanced_box_score, selected_option, stat)
                            if result.empty:
                                break
                            if not showed_name:
                                player_name = result.iloc[0]['Player']
                                st.markdown(f'#### {player_name} Summary')
                                showed_name = True
                            player_stat = int(result.iloc[0][stat] * 100)
                            st.markdown(f'{stat} - {ordinal(player_stat)} Percentile')
                            st.progress(player_stat)

        if selected_year >= 1997:
            with st.expander(f'Impact - {selected_year}'):
                st.markdown("""
                    ### Impact metrics
                    Impact metrics are used to measure a player's impact on the success of a given team. In this selection:
                    * **On-Off**: Average difference between the Plus/Minus when player is on the court vs. off the court.
                    * **OnCourt**: Plus/Minus Per 100 Possessions (On Court only).
                    * **BPM**: A box score estimate of the points per 100 possessions a player contributed above a league-average player, translated to an average team.
                """)                
                st.write(gen_on_off_plot(selected_year, best_players))

if __name__ == '__main__':
    main()
