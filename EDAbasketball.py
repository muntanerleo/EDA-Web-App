import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Data Science Web App

# in this project i will dynamically retrieve data form the internet doing web scraping-
# from the basketball refrence website. 

# after the data has been scraped i will be doing some data filtering.
# this will be a simple Exploritory Data Analysis by creating a simple  Heatmap

# the use of pandas in this project help with the webscraping
# the base64 library is used to handle the data download for the csv file. ASCCI to byte conversion
# matplotlib,seaborn,numpy for the heatmap

# PART 1: SET UP
st.title('NBA Player Stats')

st.markdown("""
This Data Science Web App performs simple webscraping of NBA player stats!
* **Python libraries:** streamlit, pandas, base64, matplotlib, seaborn, numpy.
* **Data source acquired from:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

# code below: this makes the side bar on the webpage where the user can choose the year for the stats
st.sidebar.header('User Input Features')

# the .selectbox function makes the dropdown menu. i specify that i want my list showing the year 2020 at the top-
# by using reversed. if not then 1950 will be first.
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950,2022))))

# PART 2: WEB SCRAPING OF NBA PLAYER STATS
# this part will also do data pre-processing.
# the web scraping is simple, nothing fancy

# the st.cache allows me to save the data for future use. instaead of it always having to retrieve the data.
# therefore whenever a user selects a new year, it will run for the first time and make a cache for that data.
# so the second time the user picks the same year, it will load much faster.
@st.cache
def load_data(year):
  # get the website i want to scrape
  url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
  
  # specify the line to be scraped. which in this case is only 1 line.
  # the .read_html reads the data from the html. the data in this case is in table form.
  # pandas are great for reading the data in table form
  html = pd.read_html(url, header = 0)
  dataframe = html[0]

  # drop redundant header which is present throughout the table
  # code below: deletes repeating headers
  raw = dataframe.drop(dataframe[dataframe.Age == 'Age'].index)
  raw = raw.fillna(0)

  # code below: performs simple deletion of some index column called 'Rk'
  # it is redundant because of the index already provided by pandas
  playerstats = raw.drop(['Rk'], axis=1)
  return playerstats

# display the pre-processed data: costum function load_data()takes in the input argument selected_year. 
# then it takes NBA player stats data from the selected_year.
# for ex: if i choose the year 2019 on the drop down menu, the selected_year becomes 2019. this then gives me the stats of 2019
playerstats = load_data(selected_year)

# PART 3: USER SELECTS THE TEAMS
# sidebar - Team selection

# code below: variable that uses the playerstats dataframe, in particular the team column then i will display the unique values.
# then the teams will be sorted alphabetically
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# QUICK Note: the reason i put sorted_unique_team and unique_pos twice is because if i didnt then-
# the teams and positions would not show up in the sidebar. it would only show 1 team and 1 position

# sidebar - position selection
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
# the multiselect functions allows me to display all the possible values inside the team/position variable.
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# PART 4: FILTERING DATA
# code below: filters data based on the input section on the sidebar.
# for ex: if the user takes out a few teams, the display will show only the selected teams data.
# whenever the data selection is updated, so will the dataframe
dataframe_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimensions: ' + str(dataframe_selected_team.shape[0]) + ' rows and ' + str(dataframe_selected_team.shape[1]) + ' columns.')

# QUICK Note: streamlit 0.85.0. came with a bug. pyarrow has an issue with numpy.dtype values (which df.dtypes returns).
# A possible workaround is to convert DataFrame cells to strings with df.astype(str)
# thats what i did below and it worked fine.
test = dataframe_selected_team.astype(str)
st.dataframe(test)
# st.dataframe(dataframe_selected_team)

# PART 5: DOWNLOAD NBA PLAYER STATS DATA (code made possiable by the link below)
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(dataframe):
  csv = dataframe.to_csv(index=False)
  # strings <-> bytes conversion
  b64 = base64.b64encode(csv.encode()).decode()
  href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'

st.markdown(filedownload(dataframe_selected_team), unsafe_allow_html=True)

# PART 6: HEATMAP
if st.button('Intercorrelation Heatmap'):
  st.header('Intercorrelation Matrix Heatmap')
  # code below: saves data into a csv file
  dataframe_selected_team.to_csv('output.csv',index=False)
  # code below: reads the csv file back in. (these two steps help make the heatmap)
  dataframe = pd.read_csv('output.csv')

  # code below: performs the Intercorrelation Matrix calculation
  corr = dataframe.corr()
  
  # create the heatmap where half are not shown because they're masked
  mask = np.zeros_like(corr)
  mask[np.triu_indices_from(mask)] = True
  with sns.axes_style("white"):
    f, ax = plt.subplots(figsize=(7, 5))
    ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
  st.pyplot()