import pandas as pd
import datetime
import numpy as np
df = pd.read_csv('NBA_player_data_16-17.csv')
df['result'] = df['team_score']-df['opp_score']
groups= df.groupby(['Game_Id','Team'],sort=False).sum()

matrix = groups.as_matrix()

ids = []
for game in df['Game_Id'].unique():
    ids.append(game+ '%aa'+game.split('_')[1])
    ids.append(game+ '%aa'+game.split('_')[2])

new_frame = pd.DataFrame(matrix, columns = groups.columns, index = ids)

team_data = new_frame[['3P','3PA', 'AST', 'BLK', 'FG', 'FGA', 'FT', 'FTA', 'ORB',
       'PF', 'PTS', 'STL', 'TOV', 'TRB','is_Home','Team_Win']]

team_data = team_data.reset_index()

team_data['opponent'] = team_data['index'].apply(lambda x: x.split('%aa')[1])

team_data['index'] = team_data['index'].apply(lambda x: x.split('%aa')[0])

team_data['is_Home'] = team_data['is_Home'].apply(lambda x: x>0).astype(int)
team_data['Team_Win'] = team_data['Team_Win'].apply(lambda x: x>0).astype(int)

both_teams_total = team_data.groupby('index',sort=False).sum().reset_index()
##this gets all the opponents data on the same line
weird = pd.merge(both_teams_total,team_data,on='index')

#fill in opponent data in an insufficient way
team_data['opp_TRB'] = weird['TRB_x']-team_data['TRB']
team_data['opp_3P'] = weird['3P_x']-team_data['3P']
team_data['opp_3PA'] = weird['3PA_x']-team_data['3PA']
team_data['opp_AST'] = weird['AST_x']-team_data['AST']
team_data['opp_BLK'] = weird['BLK_x']-team_data['BLK']
team_data['opp_FG'] = weird['FG_x']-team_data['FG']
team_data['opp_FGA'] = weird['FGA_x']-team_data['FGA']
team_data['opp_FT'] = weird['FT_x']-team_data['FT']
team_data['opp_FTA'] = weird['FTA_x']-team_data['FTA']
team_data['opp_PTS'] = weird['PTS_x']-team_data['PTS']
team_data['opp_ORB'] = weird['ORB_x']-team_data['ORB']
team_data['opp_STL'] = weird['STL_x']-team_data['STL']
team_data['opp_PF'] = weird['PF_x']-team_data['PF']
team_data['opp_TOV'] = weird['TOV_x']-team_data['TOV']

def opponent(row):
    if row['opponent'] == row['index'].split('_')[1]:
        return row['index'].split('_')[2]
    else:
        return row['index'].split('_')[1]

team_data['Team'] =team_data.apply(opponent, axis=1)

team_data['Game_Id'] = team_data['index']
team_data.drop('index',axis=1, inplace=True)
team_data.to_csv('team_boxscores_16-17.csv',index=False)
