import pandas as pd
import requests
import streamlit as st
import json

@st.cache(suppress_st_warning=True)
def go_get_some_data():
    #url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset/nba/game_team_odds_ml?key=AIzaSyAqDjawEivZhJtRdMktAUJwkjvfrvKjVG4'
    #url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset-test?key=AIzaSyDod7ymTrgAJr9bRvbFhDZWSNcma9jkwpM'
    url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset-test?key=AIzaSyB_7ITiFjgqEB_Jufa98rA_Xr5_E4FPMC4' # dev
    #url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset-test?key=AIzaSyCTR0TV_tdDldMRfS64R4Gwn7k05R_Dvz8'
    #url = 'https://sports-analytics-363bag9z.uc.gateway.dev/dataset-test?key=AIzaSyCTR0TV_tdDldMRfS64R4Gwn7k05R_Dvz8'  # prod
    r = requests.get(url)

    j = r.json()

    #print(json.dumps(j))
    return pd.DataFrame(j['data'])


df = go_get_some_data()

#############################################################
# Side Filters
#############################################################
seasons = df['season'].unique().tolist()
seasons.sort(reverse=True)
seasons_selected = st.sidebar.multiselect('Season',seasons,default=[max(seasons)])

season_types = df['season_type'].unique().tolist()
season_types_selected = st.sidebar.multiselect('Season Types',season_types, default=["Regular Season"])

home_away_types = df['h_a'].unique().tolist()
#home_away_types_selected = st.sidebar.multiselect('Home or Away',home_away_types, default=home_away_types)

#st.sidebar.write('Home or Away 2')
#option_1_a = st.sidebar.checkbox('H')
#option_2_a = st.sidebar.checkbox('A')
#option_3_a = st.sidebar.checkbox('P')

#st.sidebar.write('Home or Away 3')
#cb1, cb2, cb3 = st.sidebar.columns(3)
#option_1 = cb1.checkbox('H')
#option_2 = cb2.checkbox('A')
#option_3 = cb3.checkbox('P')

#ncol = st.sidebar.number_input("Number of dynamic columns", 0, 20, 1)
ncols = len(home_away_types)
cols = st.sidebar.columns(ncols)

dct = {}
for i, x in enumerate(cols):
    val = home_away_types[i]
    dct[val] = x.checkbox(val, value=True)

home_away_types_selected = []
for key in dct:
    if dct[key]:  
        home_away_types_selected.append(key)

fav_dog_types = df['ml_breakeven_f_d'].unique().tolist()
fav_dog_types_selected = st.sidebar.multiselect('Fav or Dog',fav_dog_types, default=fav_dog_types)

elo_pick_types = df['elo_ml_pick'].unique().tolist()
elo_pick_types_selected = st.sidebar.multiselect('Elo Pick',elo_pick_types, default=elo_pick_types)

raptor_pick_types = df['raptor_ml_pick'].unique().tolist()
raptor_pick_types_selected = st.sidebar.multiselect('Raptor Pick',raptor_pick_types, default=raptor_pick_types)

inter_conference_types = df['inter_conference'].unique().tolist()
inter_conference_types_selected = st.sidebar.multiselect('Inter Conference',inter_conference_types, default=inter_conference_types)

inter_division_types = df['inter_division'].unique().tolist()
inter_division_types_selected = st.sidebar.multiselect('Inter Division',inter_division_types, default=inter_division_types)

teams = df['team_abbr'].unique().tolist()
teams_selected = st.sidebar.multiselect('Teams',teams)
teams_filter = teams if not teams_selected else teams_selected # assume all if not selected

#############################################################
# Filter DF by Side Filters
#############################################################
df_filtered_season = df[ df["season"].isin(seasons_selected) 
                    & df["season_type"].isin(season_types_selected) 
                    ]

df_filtered = df_filtered_season[   df_filtered_season["h_a"].isin(home_away_types_selected) 
                    & df_filtered_season["ml_breakeven_f_d"].isin(fav_dog_types_selected)
                    & df_filtered_season["elo_ml_pick"].isin(elo_pick_types_selected)
                    & df_filtered_season["raptor_ml_pick"].isin(raptor_pick_types_selected)
                    & df_filtered_season["inter_conference"].isin(inter_conference_types_selected)
                    & df_filtered_season["inter_division"].isin(inter_division_types_selected)
                    & df_filtered_season["team_abbr"].isin(teams_filter)
                    ]

#############################################################
# Data Type Conversions
#############################################################
df_filtered['ml_result'] = pd.to_numeric(df_filtered['ml_result'])
df_filtered['game_date'] = pd.to_datetime(df_filtered['game_date'])
df_filtered['ml'] = pd.to_numeric(df_filtered['ml'])
#df = df.astype({"A": int, "B": str})

#############################################################
# KPI's
#############################################################
Bet_Count = df_filtered['game_date'].count()
Total_Result = df_filtered['ml_result'].sum().round(1)
ROI = (Total_Result / Bet_Count * 100).round(1)

Possible_Games = df_filtered_season['game_date'].count()
Percent_of_possible_games = (Bet_Count / Possible_Games * 100).round(1)

avg_ml = df_filtered['ml'].mean().round()
col1, col2, col3 = st.columns(3)
col1.metric("Total Result",Total_Result, str(ROI) + "% ROI")
col2.metric("Bets", Bet_Count, str(Percent_of_possible_games) + "% Possible")
col3.metric("Average ML", avg_ml, "")

# count, ROI, 
#############################################################
# Chart
#############################################################
df_chart = df_filtered.groupby('game_date').agg(daily_result=('ml_result', 'sum'))
st.line_chart(df_chart['daily_result'].cumsum())

####
#makes = df['make'].drop_duplicates()
#make_choice = st.sidebar.selectbox('Select your vehicle:', makes)
#years = df["year"].loc[df["make"] = make_choice]
#year_choice = st.sidebar.selectbox('', years) 

#options = df['app'].unique().tolist()
#selected_options = st.sidebar.multiselect('Which app do you want?',options)

#st.table(data=df)
#df['ml_result'] = pd.to_numeric(df['ml_result'])
#Total = df['ml_result'].sum()
#df2 = df.query('season == "2022" & season_type == "Regular Season"')

###

#foo = df.dtypes.astype(str)

#https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset/nba/game_team_odds_ml?key=AIzaSyAqDjawEivZhJtRdMktAUJwkjvfrvKjVG4&