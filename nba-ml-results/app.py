import pandas as pd
import requests
import streamlit as st
import json
import numpy as np
from datetime import datetime

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def caching_data_to_analyze():
    #url = 'https://sports-analytics-dc7nfvdr.uc.gateway.dev/dataset-test?key=AIzaSyB_7ITiFjgqEB_Jufa98rA_Xr5_E4FPMC4' # dev
    url = 'https://sports-analytics-363bag9z.uc.gateway.dev/dataset-test?key=AIzaSyCTR0TV_tdDldMRfS64R4Gwn7k05R_Dvz8'  # prod
    r = requests.get(url)
    j = r.json()
    return pd.DataFrame(j['data'])

def config_set_up():
    st.set_page_config(layout="wide")

    styl = f"""
        <style>
            .appview-container .main .block-container{{
                padding-top: 10px;    }}
            header {{ background: rgba(255,255,255,0) !important }}
        </style>
        """
    st.markdown(styl, unsafe_allow_html=True)

def create_filter_columns(label,filter_checkbox_key,middle_col_count=0):
    if not middle_col_count:
        middle_col_count = 0
    if middle_col_count >= 10:
        st.error('max values for filter columns is 10')
    col_array = []
    col_array.append(3)
    remaining = 10
    for x in range(middle_col_count):
        col_array.append(1)
        remaining = remaining - 1
    col_array.append(remaining)
    #col_array.append(10)
    col_array.append(1)
    cols = st.columns(col_array)
    cols[0].text(label)
    max_index = len(cols)-1
    cols[max_index].button('X',on_click=remove_filter, args=(filter_checkbox_key,),key=label)
    return cols

def remove_filter(filter_name):
    st.session_state[filter_name] = False

def string_to_bool(string_bool):
    if string_bool == "True": 
        return True 
    elif string_bool=="False": 
        return False
    else: 
        return None


#def filter_container(label , filter_checkbox_key):
#    filter_container_col1, filter_container_col2, filter_container_col3 = st.columns([2, 10, 1])
#    with filter_container_col1:
#       st.write(label)
#    with filter_container_col2:
#        seasons.sort(reverse=True)
#        seasons_selected = st.multiselect('Season',seasons,default=seasons, label_visibility="collapsed")
#    with filter_container_col3:
#        st.button('X',on_click=remove_filter, args=(filter_checkbox_key,))

#filter_container('Season','season_filter')
config_set_up()
df = caching_data_to_analyze()

#############################################################
# Data Type Conversions
#############################################################
df['ml_result'] = pd.to_numeric(df['ml_result'])
df['game_date'] = pd.to_datetime(df['game_date']).dt.date
df['game_week'] = pd.to_datetime(df['game_week']).dt.date
df['ml'] = pd.to_numeric(df['ml'])


#############################################################
# Transformations from API (these should be temp)
#############################################################
df['raptor_ml_pick'] = df['raptor_ml_pick'].replace(np.nan, "None")

st.title("NBA - 538 - Analysis")


#############################################################
# Side Filters
#############################################################

st.sidebar.title("Choose Filters")
with st.sidebar.expander("Timeframe"):
    season_filter = st.checkbox('Season',value=True,key="season_filter")
    season_type_filter = st.checkbox('Season Type',value=True,key='season_type_filter')
    game_week_filter = st.checkbox('Game Week',value=False,key='game_week_filter')
    game_date_filter = st.checkbox('Game Date',value=False,key='game_date_filter')

with st.sidebar.expander("Game Attributes"):
    home_away_type_filter = st.checkbox('Home or Away',value=False,key='home_away_type_filter')
    fav_dog_type_filter = st.checkbox('Fav or Dog',value=False,key='fav_dog_type_filter')
    inter_conference_type_filter = st.checkbox('Inter Conference',value=False,key='inter_conference_type_filter')
    inter_division_type_filter = st.checkbox('Inter Division',value=False,key='inter_division_type_filter')
    team_filter = st.checkbox('Team',value=False,key='team_filter')

with st.sidebar.expander("Predictions"):
    elo_pick_type_filter = st.checkbox('Elo Pick Type',value=False,key='elo_pick_type_filter')
    raptor_pick_type_filter = st.checkbox('Raptor Pick Type',value=False,key='raptor_pick_type_filter')

#############################################################
# KPI Container
#############################################################

with st.container():
    col1, col2, col3 = st.columns(3)


#############################################################
# Main Filters When Selected on Side
#############################################################

df_filtered = df

with st.expander("Filters",expanded=True):

    #seasons
    seasons = df_filtered['season'].unique().tolist()
    seasons.sort(reverse=True)
    #seasons_selected = seasons
    if season_filter:
        with st.container():
            season_cols = create_filter_columns('Season','season_filter')
            if seasons:
                seasons_selected = season_cols[1].multiselect('Season',seasons,default=seasons, label_visibility="collapsed")
                df_filtered = df_filtered[ df_filtered["season"].isin(seasons_selected) ]



    #season types
    season_types = df_filtered['season_type'].unique().tolist()
    #season_types_selected = season_types
    if season_type_filter:
        with st.container():
            season_types_cols = create_filter_columns('Season Types','season_type_filter')
            if season_types:
                season_types_selected = season_types_cols[1].multiselect('Season Types',season_types, default=["Regular Season"], label_visibility="collapsed")
                df_filtered = df_filtered[ df_filtered["season_type"].isin(season_types_selected)  ]
    
    # Game Date Range
    if game_date_filter:
        date_aggs = df_filtered['game_date'].agg(['min', 'max'])
        #min_slider_game_date = datetime.strptime(date_aggs['min'], '%Y-%m-%d')
        #max_slider_game_date = datetime.strptime(date_aggs['max'], '%Y-%m-%d')
        min_slider_game_date = date_aggs['min']
        max_slider_game_date = date_aggs['max']
        with st.container():
            game_date_cols = create_filter_columns('Game Dates','game_date_filter')
            game_date_range_selected = game_date_cols[1].slider('Game Dates',min_value = min_slider_game_date, max_value = max_slider_game_date, value=(min_slider_game_date,max_slider_game_date), format = 'MM/DD/YYYY', label_visibility="collapsed")
        #st.write('Values:', game_date_range_selected)
        #st.write(game_date_range_selected[0])        
        beg_game_date_filter = game_date_range_selected[0]
        end_game_date_filter = game_date_range_selected[1]
        df_filtered = df_filtered[ (df_filtered['game_date'] >= beg_game_date_filter) & (df_filtered['game_date'] <= end_game_date_filter)  ]

        #df[(df['date'] > '2013-01-01') & (df['date'] < '2013-02-01')]

    # Game Week Range
    if game_week_filter:
        date_week_aggs = df_filtered['game_week'].agg(['min', 'max'])
        min_slider_game_week = date_week_aggs['min']
        max_slider_game_week = date_week_aggs['max']
        with st.container():
            game_week_cols = create_filter_columns('Game Weeks','game_week_filter')
            game_week_range_selected = game_week_cols[1].slider('Game Weeks',min_value = min_slider_game_week, max_value = max_slider_game_week, value=(min_slider_game_week,max_slider_game_week), format = 'MM/DD/YYYY', label_visibility="collapsed")
        #st.write('Values:', game_date_range_selected)
        #st.write(game_date_range_selected[0])        
        beg_game_week_filter = game_week_range_selected[0]
        end_game_week_filter = game_week_range_selected[1]
        df_filtered = df_filtered[ (df_filtered['game_week'] >= beg_game_week_filter) & (df_filtered['game_week'] <= end_game_week_filter)  ]

    


    #home away types
    home_away_types = df_filtered['h_a'].unique().tolist()
    #home_away_types_selected = home_away_types
    if home_away_type_filter:
        with st.container():
            ncols = len(home_away_types)
            home_away_type_cols = create_filter_columns('Home or Away','home_away_type_filter',ncols)
            #h_a_cols = season_types_cols[1].columns(ncols)

            #dct = {}
            #for i, x in enumerate(h_a_cols):
            #    val = home_away_types[i]
            #    dct[val] = x.checkbox(val, value=True)
            #home_away_types_selected = []
            #for key in dct:
            #    if dct[key]:  
            #        home_away_types_selected.append(key)

            
            #for i, val in enumerate(home_away_types):
                #val = home_away_types[i]
                #home_away_type in home_away_types:
            dct = {}
            col_i = 1
            for home_away_type in home_away_types:
                dct[home_away_type] = home_away_type_cols[col_i].checkbox(home_away_type,value=True)
                col_i += 1
            home_away_types_selected = []
            for key in dct:
                if dct[key]:  
                    home_away_types_selected.append(key)
        df_filtered = df_filtered[ df_filtered["h_a"].isin(home_away_types_selected)   ]

    # Fav or Dogs
    fav_dog_types = df_filtered['ml_breakeven_f_d'].unique().tolist()
    #fav_dog_types_selected = fav_dog_types
    if fav_dog_type_filter:
        with st.container():
            ncols = len(fav_dog_types)
            fav_dog_type_cols = create_filter_columns('Fav Or Dog','fav_dog_type_filter',ncols)
            
            dct = {}
            col_i = 1
            for fav_dog_type in fav_dog_types:
                dct[fav_dog_type] = fav_dog_type_cols[col_i].checkbox(fav_dog_type,value=True)
                col_i += 1
            fav_dog_types_selected = []
            for key in dct:
                if dct[key]:  
                    fav_dog_types_selected.append(key)
        df_filtered = df_filtered[ df_filtered["ml_breakeven_f_d"].isin(fav_dog_types_selected)   ]

    # Inter Conference
    inter_conference_types = df_filtered['inter_conference'].unique().tolist()
    inter_conference_types.sort(reverse=True)
    #inter_conference_types_selected = inter_conference_types
    if inter_conference_type_filter:
        with st.container():
            ncols = len(inter_conference_types)
            inter_conference_type_cols = create_filter_columns('Inter Conference','inter_conference_type_filter',ncols)
            
            dct = {}
            col_i = 1
            for inter_conference_type in inter_conference_types:
                dct[str(inter_conference_type)] = inter_conference_type_cols[col_i].checkbox(str(inter_conference_type),value=True,key='Inter Conference' + str(col_i))
                col_i += 1
            inter_conference_types_selected = []
            for key in dct:
                if dct[key]:  
                    key_bool = string_to_bool(key)
                    inter_conference_types_selected.append(key_bool)
        df_filtered = df_filtered[  df_filtered["inter_conference"].isin(inter_conference_types_selected)  ]

    # Inter Division
    inter_division_types = df_filtered['inter_division'].unique().tolist()
    inter_division_types.sort(reverse=True)
    #inter_division_types_selected = inter_division_types
    if inter_division_type_filter:
        with st.container():
            ncols = len(inter_division_types)
            inter_division_type_cols = create_filter_columns('Inter Division','inter_division_type_filter',ncols)
            
            dct = {}
            col_i = 1
            for inter_division_type in inter_division_types:
                dct[str(inter_division_type)] = inter_division_type_cols[col_i].checkbox(str(inter_division_type),value=True,key='Inter Division' + str(col_i))
                col_i += 1
            inter_division_types_selected = []
            for key in dct:
                if dct[key]:  
                    key_bool = string_to_bool(key)
                    inter_division_types_selected.append(key_bool)
        df_filtered = df_filtered[  df_filtered["inter_division"].isin(inter_division_types_selected)  ]

    # Team Filter
    teams = df_filtered['team_abbr'].unique().tolist()
    teams.sort()
    #teams_selected = teams
    if team_filter:
        with st.container():
            team_cols = create_filter_columns('Teams','team_filter')
            teams_selected = team_cols[1].multiselect('Teams',teams, label_visibility="collapsed")
            #teams_selected = team_cols[1].multiselect('Teams',teams)
        teams_filter = teams if not teams_selected else teams_selected # assume all if not selected
        df_filtered = df_filtered[  df_filtered["team_abbr"].isin(teams_filter)  ]
    

    # Elo Pick Type
    elo_pick_types = df_filtered['elo_ml_pick'].unique().tolist()
    elo_pick_types_selected = elo_pick_types
    if elo_pick_type_filter:
        with st.container():
            ncols = len(elo_pick_types)
            elo_pick_type_cols = create_filter_columns('Elo Pick Types','elo_pick_type_filter',ncols)
            
            dct = {}
            col_i = 1
            for elo_pick_type in elo_pick_types:
                dct[elo_pick_type] = elo_pick_type_cols[col_i].checkbox(elo_pick_type,value=True)
                col_i += 1
            elo_pick_types_selected = []
            for key in dct:
                if dct[key]:  
                    elo_pick_types_selected.append(key)
        df_filtered = df_filtered[  df_filtered["elo_ml_pick"].isin(elo_pick_types_selected)  ]

    # Raptor Pick Type
    raptor_pick_types = raptor_pick_types = df_filtered['raptor_ml_pick'].unique().tolist()
    raptor_pick_types_selected = raptor_pick_types
    if raptor_pick_type_filter:
        with st.container():
            #ncols = len(raptor_pick_types)
            #raptor_pick_type_cols = create_filter_columns('Raptor Pick Types','raptor_pick_type_filter',ncols)
            
            #dct = {}
            #col_i = 1
            #for raptor_pick_type in raptor_pick_types:
            #    dct[raptor_pick_type] = raptor_pick_type_cols[col_i].checkbox(raptor_pick_type,value=True)
            #    col_i += 1
            #raptor_pick_types_selected = []
            #for key in dct:
            #    if dct[key]:  
            #        raptor_pick_types_selected.append(key)

            raptor_pick_type_cols = create_filter_columns('raptor_ml_pick','raptor_pick_type_filter')
            raptor_pick_types_selected = raptor_pick_type_cols[1].multiselect('Season',raptor_pick_types,default=raptor_pick_types, label_visibility="collapsed")
        df_filtered = df_filtered[  df_filtered["raptor_ml_pick"].isin(raptor_pick_types_selected)  ]


#df_filtered = df_filtered[  df_filtered["team_abbr"].isin(teams_filter)  ]

#fav_dog_types = df['ml_breakeven_f_d'].unique().tolist()
#fav_dog_types_selected = st.sidebar.multiselect('Fav or Dog',fav_dog_types, default=fav_dog_types)

#elo_pick_types = df['elo_ml_pick'].unique().tolist()
#elo_pick_types_selected = st.sidebar.multiselect('Elo Pick',elo_pick_types, default=elo_pick_types)

#raptor_pick_types = df['raptor_ml_pick'].unique().tolist()
#raptor_pick_types_selected = st.sidebar.multiselect('Raptor Pick',raptor_pick_types, default=raptor_pick_types)

#inter_conference_types = df['inter_conference'].unique().tolist()
#inter_conference_types_selected = st.sidebar.multiselect('Inter Conference',inter_conference_types, default=inter_conference_types)

#inter_division_types = df['inter_division'].unique().tolist()
#inter_division_types_selected = st.sidebar.multiselect('Inter Division',inter_division_types, default=inter_division_types)

#teams = df['team_abbr'].unique().tolist()
#teams_selected = st.sidebar.multiselect('Teams',teams)
#teams_filter = teams if not teams_selected else teams_selected # assume all if not selected

#############################################################
# Filter DF by Side Filters
#############################################################
#df_filtered_season = df[ df["season"].isin(seasons_selected) 
#                    & df["season_type"].isin(season_types_selected) 
#                    ]




#df = df.astype({"A": int, "B": str})

if df_filtered.empty:
    st.write('No data matches filter criteria')
else:
    #############################################################
    # KPI's
    #############################################################
    Bet_Count = df_filtered['game_date'].count()
    Total_Result = df_filtered['ml_result'].sum().round(1)
    ROI = (Total_Result / Bet_Count * 100).round(1)


    #Possible_Games = df_filtered_season['game_date'].count()
    Possible_Games = df_filtered['game_date'].count()
    Percent_of_possible_games = (Bet_Count / Possible_Games * 100).round(1)

    avg_ml = df_filtered['ml'].mean().round()

    col1.metric("Total Result",Total_Result, str(ROI) + "% ROI")
    col2.metric("Bets", Bet_Count, str(Percent_of_possible_games) + "% Possible")
    col3.metric("Average ML", avg_ml, "")

    # count, ROI, 
    #############################################################
    # Chart
    #############################################################
    tab1, tab2 = st.tabs(["Chart", "Sample Data"])

    df_chart = df_filtered.groupby('game_date').agg(daily_result=('ml_result', 'sum'))
    tab1.line_chart(df_chart['daily_result'].cumsum())
    tab2.write("First 100 record sample")
    tab2.table(df_filtered[0:100])






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