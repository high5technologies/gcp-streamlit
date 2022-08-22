import pandas as pd
import requests
#import streamlit as st
import json

#url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset/nba/game_team_odds_ml?key=AIzaSyAqDjawEivZhJtRdMktAUJwkjvfrvKjVG4'
url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset-test?key=AIzaSyDod7ymTrgAJr9bRvbFhDZWSNcma9jkwpM'

r = requests.get(url)

j = r.json()

#print(json.dumps(j))
df = pd.DataFrame(j['data'])
seasons = df['season'].unique().tolist()
print(seasons)
seasons2 = seasons.sort(reverse=True,key = int)
print(seasons2)
#df['ml_result'] = pd.to_numeric(df['ml_result'])
##st.table(data=df)
#Total = df['ml_result'].sum()
#print(Total)

