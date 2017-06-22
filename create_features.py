import pandas as pd
import datetime
import numpy as np
import requests
import json
teams= pd.read_csv('team_boxscores_16-17.csv')
#add date column
teams['Date']=teams['Game_Id'].apply(lambda x: x.split('_')[0])
##convert to datetime
teams['Date'] = pd.to_datetime(teams['Date'])
matrix = teams.as_matrix()

##get a list of all the teams
clubs = []
for el in matrix:
    clubs.append(el[16])
clubs = list(set(clubs))

##This cell calculates how many days since the last game.

##initialize a dictionary of last dates and set all to 0
last_date = {}
for team in clubs:
    last_date[team]=0


##calculate how many days since last game
new_matrix = []
for row in matrix:
    row = list(row)
    if last_date[row[16]] == 0:
        row.append(np.nan)
    else:
        row.append((row[33]-last_date[row[16]]).days)
    new_matrix.append(row)
    last_date[row[16]] = row[33]

##add Days_Since to column names
columns = ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB', 'PF',
       'PTS', 'STL', 'TOV', 'TRB', 'is_Home', 'Team_Win', 'opponent', 'opp_TRB','opp_3P',
       'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG', 'opp_FGA', 'opp_FT',
       'opp_FTA', 'opp_PTS', 'opp_ORB', 'opp_STL', 'opp_PF', 'opp_TOV',
       'Team', 'Game_Id', 'Date','Days_Since']
##add the delta column back to new data frame
df = pd.DataFrame(new_matrix,columns = columns)
##dictionary of time zones
time_zone_dict = {}
for team in clubs:
    time_zone_dict[team]=0
for team in clubs:
    if team in ['Phoenix','Denver', 'Utah']:
        time_zone_dict[team]+= 1
    elif team in ['Chicago','Oklahoma City','Milwaukee','Houston','Dallas',
                  'San Antonio','Memphis','Minnesota','New Orleans']:
        time_zone_dict[team]+=2
    elif team in ['Atlanta','Boston','Charlotte','Brooklyn', 'Cleveland','Detroit',
                 'Indiana', 'Miami','New York', 'Orlando','Philadelphia','Washington','Toronto','New Jersey']:
        time_zone_dict[team]+=3
    else:
        pass

##grab the location from the game id
df['game_Location'] = df['Game_Id'].apply(lambda x: x.split("_")[1])

##make time zone function
def time_zone(row):
    return time_zone_dict[row['game_Location']]

##add time zone to data frame
df['Time_Zone'] =df.apply(time_zone, axis=1)

##change location column to accurate google locations. This is for the next cell to call google API
def change_Locations(row):
    if row['game_Location'] in ['LA Clippers', 'LA Lakers']:
        return 'Los Angeles'
    elif row['game_Location'] == 'Golden State':
        return 'Oakland'
    elif row['game_Location'] == 'Utah':
        return "Salt Lake City"
    elif row['game_Location'] =='Indiana':
        return 'Indianapolis'
    elif row['game_Location'] =='Minnesota':
        return 'Minneapolis'
    elif row['game_Location'] =='Washington':
        return 'Washington DC'
    elif row['game_Location'] == 'New Jersey':
        return 'Newark'
    else:
        return row['game_Location']
df['game_Location'] = df.apply(change_Locations, axis=1)

## do the same thing as game location
def team_location(row):
    if row['Team'] in ['LA Clippers', 'LA Lakers']:
        return 'Los Angeles'
    elif row['Team'] == 'Golden State':
        return 'Oakland'
    elif row['Team'] == 'Utah':
        return "Salt Lake City"
    elif row['Team'] =='Indiana':
        return 'Indianapolis'
    elif row['Team'] =='Minnesota':
        return 'Minneapolis'
    elif row['Team'] =='Washington':
        return 'Washington DC'
    elif row['Team'] == 'New Jersey':
        return 'Newark'
    else:
        return row['game_Location']

df['team_location'] = df.apply(team_location,axis=1)
##call google map API to get distances between stadiums and make them into a dictionary
dict_distances = {}
for i,loc1 in enumerate(df['game_Location'].unique()):
    for k in range(i,len(df['game_Location'].unique())):
        loc2 = df['game_Location'].unique()[k]
        if loc1!=loc2:
            string = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&key=AIzaSyAtEyirTGKvMkeAPCThQYY83-a1Dzq6SHo'.format(loc1,loc2)
            response = requests.get(string)
            try:
                dict_distances[loc1+'-'+loc2] = response.content.split('\"text" : \"')[1].split('\"')[0]
            except:
                dict_distances[loc1+'-'+loc2] = np.nan
##use the dictionary created to calculated distances between home and game
def distance_from_home(row):
    if row['game_Location'] ==row['team_location']:
        return 0
    else:
        string = row['game_Location']+'-'+row['team_location']
        if string in dict_distances:
            return dict_distances[string]
        else:
            return dict_distances[row['team_location']+'-'+row['game_Location']]
df['distance_From_Home'] = df.apply(distance_from_home,axis=1)
##turn distances into necessary form
def fix_Distance(row):

    try:
        num = row['distance_From_Home'].split(' ')[0]
        return int(num.replace(',',''))

    except:
        return row['distance_From_Home']

df['distance_From_Home'] = df.apply(fix_Distance,axis=1)
#since we will deal with team time zones we need to change the name
df['game_time_zone'] =df['Time_Zone']
df.drop('Time_Zone', axis=1, inplace=True)
##add the time zone of the team's home stadium
def team_time_zone(row):
    return time_zone_dict[row['Team']]
df['team_time_zone'] = df.apply(team_time_zone,axis=1)
history =pd.read_csv('history_lines.csv')
def game_time(row):
    return int(row['Date'].split(' ')[1].split(':')[0])
df['game_hour (et)'] = history.apply(game_time,axis=1)
##time zone differential between where the game is and the team's home location
df['time_zone_diff'] = df['game_time_zone']-df['team_time_zone']
##This cell adds the last location to the dataframe. So, if GS played Dallas in the previous game,
##That will be added as a feature.
matrix = df.as_matrix()


##initialize last_opp to check to see if a team has played a game.
last_loc = {}
for team in df.Team:
    last_loc[team]=0


##figure out who the last opponent was
new_matrix = []
for row in matrix:
    row = list(row)
    if last_loc[row[31]] == 0:
        row.append(np.nan)
    else:
        row.append(last_loc[row[31]])
    last_loc[row[31]] = row[35]
    new_matrix.append(row)


columns = ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB', 'PF',
       'PTS', 'STL', 'TOV', 'TRB', 'is_Home', 'Team_Win', 'opponent',
       'opp_TRB', 'opp_3P', 'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG',
       'opp_FGA', 'opp_FT', 'opp_FTA', 'opp_PTS', 'opp_ORB', 'opp_STL',
       'opp_PF', 'opp_TOV', 'Team', 'Game_Id', 'Date', 'Days_Since',
       'game_Location', 'team_location', 'distance_From_Home',
       'game_time_zone', 'team_time_zone', 'game_hour (et)',
       'time_zone_diff','last_loc']

##add the last loc column to new data frame
df= pd.DataFrame(new_matrix,columns = columns)
##calculate the distance from the last location
def distance_from_last_game(row):
    if row['last_loc']==row['game_Location']:
        return 0
    else:
        try:
            string = row['game_Location']+'-'+row['last_loc']
            if string in dict_distances:
                return dict_distances[string]
            else:
                return dict_distances[row['last_loc']+'-'+row['game_Location']]
        except:
            return np.nan
df['distance_From_Last_Game'] = df.apply(distance_from_last_game,axis=1)
##convert this distance to a float
def fix_Distance(row):
    try:
        return row['distance_From_Last_Game'].split(' ')[0].replace(',','')
    except:
        return row['distance_From_Last_Game']

df['distance_From_Last_Game'] = df.apply(fix_Distance,axis=1)

df['distance_From_Last_Game']=df['distance_From_Last_Game'].apply(float)
##Calculate the last time zone that the team played in.

##initialize last_time_zone at -1
matrix=df.as_matrix()
last_time = {}
for team in clubs:
    last_time[team]=-1


##calculate how many days since last game
new_matrix = []
for row in matrix:
    row = list(row)
    if last_time[row[31]] == -1:
        row.append(np.nan)
    else:
        row.append(last_time[row[31]])
    new_matrix.append(row)
    last_time[row[31]] = row[38]

columns = ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB', 'PF',
       'PTS', 'STL', 'TOV', 'TRB', 'is_Home', 'Team_Win', 'opponent',
       'opp_TRB', 'opp_3P', 'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG',
       'opp_FGA', 'opp_FT', 'opp_FTA', 'opp_PTS', 'opp_ORB', 'opp_STL',
       'opp_PF', 'opp_TOV', 'Team', 'Game_Id', 'Date', 'Days_Since',
       'game_Location', 'team_location', 'distance_From_Home',
       'game_time_zone', 'team_time_zone', 'game_hour (et)',
       'time_zone_diff','last_loc', 'distance_From_Last_Game','last_time_zone']

##add the last time_zone column to new data frame
df= pd.DataFrame(new_matrix,columns = columns)
##calculate the time zone difference from the last game
df['time_zone_change'] = df['game_time_zone']- df['last_time_zone']
##this adds an index for how many games a team has already played
##it can be used to filter out the first game or first 20 games to be used as data.
matrix = df.as_matrix()


game = {}
for team in clubs:
    game[team]=1


new_matrix = []
for row in matrix:
    row = list(row)
    if game[row[31]] == 1:
        row.append(1)
        game[row[31]]=game[row[31]] + 1
    else:
        row.append(game[row[31]])
        game[row[31]]=game[row[31]] + 1
    new_matrix.append(row)

columns = ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB', 'PF',
       'PTS', 'STL', 'TOV', 'TRB', 'is_Home', 'Team_Win', 'opponent',
       'opp_TRB', 'opp_3P', 'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG',
       'opp_FGA', 'opp_FT', 'opp_FTA', 'opp_PTS', 'opp_ORB', 'opp_STL',
       'opp_PF', 'opp_TOV', 'Team', 'Game_Id', 'Date', 'Days_Since',
       'game_Location', 'team_location', 'distance_From_Home',
       'game_time_zone', 'team_time_zone', 'game_hour (et)',
       'time_zone_diff','last_loc', 'distance_From_Last_Game','last_time_zone','time_zone_change','game_number']
df= pd.DataFrame(new_matrix,columns = columns)
##this is the result of the game, which I might try to predict
df['result'] = df['PTS']-df['opp_PTS']
df['total_PTS'] = df['PTS']+df['opp_PTS']
##Did you play a game yesterday?

##initialize last_time_zone at -1
matrix=df.as_matrix()
last_date = {}
for team in clubs:
    last_date[team]=pd.datetime(2010,5,3)


##calculate how many days since last game
new_matrix = []
for row in matrix:
    row = list(row)
    if row[46] == 1:
        row.append(False)
    else:
        row.append((row[33]-last_date[row[31]]).days==1)
    new_matrix.append(row)
    last_date[row[31]] = row[33]

columns = ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB', 'PF',
       'PTS', 'STL', 'TOV', 'TRB', 'is_Home', 'Team_Win', 'opponent',
       'opp_TRB', 'opp_3P', 'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG',
       'opp_FGA', 'opp_FT', 'opp_FTA', 'opp_PTS', 'opp_ORB', 'opp_STL',
       'opp_PF', 'opp_TOV', 'Team', 'Game_Id', 'Date', 'Days_Since',
       'game_Location', 'team_location', 'distance_From_Home',
       'game_time_zone', 'team_time_zone', 'game_hour (et)',
       'time_zone_diff','last_loc', 'distance_From_Last_Game','last_time_zone','time_zone_change','game_number','result',
          'total_PTS','played_yesterday']
##add the last time_zone column to new data frame
df= pd.DataFrame(new_matrix,columns = columns)
##did you play at a different location last night?
df['played_diff_loc_yesterday']=(df['last_loc']!=df['game_Location']) & (df['played_yesterday']==True)
##is this the second night of back to back road games?
bool1 = df['played_diff_loc_yesterday']
bool2 = df['last_loc']!=df['team_location']
bool3 = df['game_Location']!=df['team_location']
df['back_to_back_road_games'] = (bool1 & bool2 & bool3)
##don't forget DRB
df['DRB']=df['TRB']-df['ORB']
df['opp_DRB']=df['opp_TRB']-df['opp_ORB']
##create feature matrix
averages= ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB','DRB',  'PF',
       'PTS', 'STL', 'TOV', 'TRB','Team_Win','opp_TRB', 'opp_3P', 'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG',
       'opp_FGA', 'opp_FT', 'opp_FTA', 'opp_PTS', 'opp_ORB','opp_DRB', 'opp_STL',
       'opp_PF', 'opp_TOV','total_PTS']
def all_features(team):
    game_feats = {}
    subdata = df[(df['Team']==team) & (df['game_number']<82)]
    numeric_data = subdata[averages]
    features = pd.DataFrame(numeric_data.expanding().mean(),columns = averages)
    features['is_Home'] =df[df['Team']==team]['is_Home']
    features['Team_Win'] =df[df['Team']==team]['Team_Win']
    features['Team'] =df[df['Team']==team]['Team']
    features['Game_Id'] =df[df['Team']==team]['Game_Id']
    features['Date'] =df[df['Team']==team]['Date']
    features['Days_Since'] =df[df['Team']==team]['Days_Since']
    features['game_Location'] =df[df['Team']==team]['game_Location']
    features['team_location'] =df[df['Team']==team]['team_location']
    features['distance_From_Home'] =df[df['Team']==team]['distance_From_Home']
    features['game_time_zone'] =df[df['Team']==team]['game_time_zone']
    features['team_time_zone'] =df[df['Team']==team]['team_time_zone']
    features['game_hour (et)'] =df[df['Team']==team]['game_hour (et)']
    features['time_zone_diff'] =df[df['Team']==team]['time_zone_diff']
    features['last_loc'] =df[df['Team']==team]['last_loc']
    features['distance_From_Last_Game'] =df[df['Team']==team]['distance_From_Last_Game']
    features['last_time_zone'] =df[df['Team']==team]['last_time_zone']
    features['time_zone_change'] =df[df['Team']==team]['time_zone_change']
    features['game_number'] =df[df['Team']==team]['game_number']
    features['result'] =df[df['Team']==team]['result']
    features['played_yesterday'] =df[df['Team']==team]['played_yesterday']
    features['played_diff_loc_yesterday'] =df[df['Team']==team]['played_diff_loc_yesterday']
    features['back_to_back_road_games'] =df[df['Team']==team]['back_to_back_road_games']
    return features

dd = all_features(clubs[0])
for i in clubs[1:]:

    dd= pd.concat([dd,all_features(i)])
df=dd

##Did you play a game yesterday?

##initialize last_time_zone at -1
matrix=df.as_matrix()
last_date = {}



##this deals with merging things on gameID
new_matrix = []
for row in matrix:
    row = list(row)
    if row[34] in last_date:
        row.append(1)
    else:
        row.append(0)
    last_date[row[34]] = 14
    new_matrix.append(row)


columns = ['3P', '3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB', 'DRB',
       'PF', 'PTS', 'STL', 'TOV', 'TRB', 'Team_Win', 'opp_TRB', 'opp_3P',
       'opp_3PA', 'opp_AST', 'opp_BLK', 'opp_FG', 'opp_FGA', 'opp_FT',
       'opp_FTA', 'opp_PTS', 'opp_ORB', 'opp_DRB', 'opp_STL', 'opp_PF',
       'opp_TOV', 'total_PTS', 'is_Home', 'Team', 'Game_Id', 'Date',
       'Days_Since', 'game_Location', 'team_location',
       'distance_From_Home', 'game_time_zone', 'team_time_zone',
       'game_hour (et)', 'time_zone_diff', 'last_loc',
       'distance_From_Last_Game', 'last_time_zone', 'time_zone_change',
       'game_number', 'result', 'played_yesterday',
       'played_diff_loc_yesterday', 'back_to_back_road_games','first']
##add the last time_zone column to new data frame
df= pd.DataFrame(new_matrix,columns = columns)
##advanced features
data=df
data['eFG%'] = (data['FG']+data['3P']*.5)/data['FGA']
data['TOV%'] = data['TOV'] / (data['FGA'] + 0.44 * data['FTA'] + data['TOV'])
data['opp_eFG%'] = (data['opp_FG']+data['opp_3P']*.5)/data['opp_FGA']
data['opp_TOV%'] = data['opp_TOV'] / (data['opp_FGA'] + 0.44 * data['opp_FTA'] + data['opp_TOV'])
data['ORB%'] = data['ORB']/ (data['ORB']+ data['opp_DRB'])
data['opp_ORB%'] = data['opp_ORB']/ (data['opp_ORB']+ data['DRB'])
data['FT_factor'] = data['FT']/data['FGA']
data['opp_FT_factor'] = data['opp_FT']/data['opp_FGA']
data['DRB%'] = data['DRB']/(data['opp_ORB']+data['DRB'])
data['opp_DRB%'] = data['opp_DRB']/(data['ORB']+data['opp_DRB'])
df=data

#home teams are odd indices, road teams are even indices
A = df[df['first']==0]
B = df[df['first']==1]
full_game = pd.merge(A,B,on='Game_Id')
df = full_game
df.drop(['is_Home_x','game_Location_x', 'game_time_zone_x','game_hour (et)_x','result_x','total_PTS_x'],axis=1,inplace=True)
replaces = ['game_Location_y','game_time_zone_y','game_hour (et)_y','total_PTS_y','result_y',]
repl = {}
for i in replaces:
    repl[i] = i.replace('_y','')
df.rename(columns = repl,inplace=True)

history = pd.read_csv('history_lines.csv')

history['date'] = history['Date'].apply(lambda x: x.split(' ')[0])
def make_team(name):
    splits = name.split(' ')
    try:
        if len(splits)==2:
            return splits[0]
        else:
            return splits[0]+' '+splits[1]
    except:
        return np.nan
def edit_team(name):
    try:
        if 'Portland' in name:
            return name.split(' ')[0]
        else:
            return name
    except:
        return np.nan
history['home'] = history['Home Team'].apply(make_team)
history['home']=history['home'].apply(edit_team)
history['home'] = history['Home Team'].apply(make_team)
history['home']=history['home'].apply(edit_team)

history['away'] = history['Visitor Team'].apply(make_team)
history['away']=history['away'].apply(edit_team)
def make_id(row):
    try:
        return row['date']+ '_' + row['home']+ '_'+ row['away']
    except:
        return np.nan
def fix_date(date):
    els = date.split('/')
    return els[0]+'/'+els[1]+'/'+'20'+els[2]
history['date']=history['date'].apply(fix_date)
history['Game_Id'] = history.apply(make_id,axis=1)
data = pd.merge(df,history[['Home Opener', 'Home Closing Line','Visitor Juice', 'Home Juice', 'Opening Total',
       'Closing Total', 'Over Juice', 'Under Juice', 'Visitor ML Open',
       'Visitor ML', 'Home ML Open', 'Home ML','Game_Id']],on = 'Game_Id')
data.to_csv('game_boxscores_16-17.csv')
