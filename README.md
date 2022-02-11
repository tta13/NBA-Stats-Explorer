
# NBA Stats Explorer

This app performs simple webscraping of NBA players' per game, advanced, per 36 and total stats data and applies simple exploratory data analysis knowledge to the dataset!
* **Python libraries:** base64, pandas, streamlit and more
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).

**Try it out below!!!**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/tta13/nba-stats-explorer/main/nba_app.py)

## Running the project
Requirements:
- [Python 3.9](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Anaconda](https://www.anaconda.com/products/individual)

In the command line, start a new conda environment from the repository location:
```
$ conda create -n myenv python=3.9
$ conda activate myenv
```
Install the requirements:
```
$ pip install -r requirements.txt
```
Install streamlit and run the app
```
$ pip install streamlit
$ streamlit run nba_app.py
```
Now go to <http://localhost:8501> to see the application running and enjoy :basketball::rocket::smiley:
