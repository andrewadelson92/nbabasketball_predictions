import requests
from bs4 import BeautifulSoup
import pandas as pd
pd.set_option('max_columns',999)
pd.set_option('max_rows',999)
pd.set_option('max_colwidth',999)
import datetime
import numpy as np
import requests
import json


def boxes(first, second):
    ##return all the boxscores (per side) from one season, for the 2016-2017 season we would call boxes('2016','2017')
    ##one fault is that every season will include a few playoff games in april.
    ##This isn't a big deal though as it can be viewed as a continuation of the regular season
    box = []
    months = ['10','11','12','1','2','3','4']
    days = [str(i) for i in range(1,32)]
    for month in months:
        print month
        if int(month)>7:
            year = first
        else:
            year=second
        for day in days:
            response = requests.get('http://www.basketball-reference.com/boxscores/?month={0}&day={1}&year={2}'.format(month,day,year))
            soup = BeautifulSoup(response.content, 'lxml')
            tables = soup.find_all('div',{'class':'game_summary expanded nohover'})
            for table in tables:
                teams = {}
                teams['away'] = table.find_all('table')[1].find('tbody').find_all('tr')[0].find('td').text
                teams['away_score'] = table.find('table').find_all('tr')[0].find_all('td')[1].text
                teams['home'] = table.find_all('table')[1].find('tbody').find_all('tr')[1].find('td').text
                teams['home_score'] = table.find('table').find_all('tr')[1].find_all('td')[1].text
                teams['away_r'] = table.find('table').find('tr')['class'][0]
                teams['home_r'] = table.find('table').find_all('tr')[1]['class'][0]
                response = requests.get('http://www.basketball-reference.com{0}'.format(table.find('p').find('a')['href']))
                soup = BeautifulSoup(response.content, 'lxml')
                for i, athlete in enumerate(soup.find_all('table')[0].find('tbody').find_all('tr')):
                    if athlete.find('th').text.strip() not in ["Reserves","Team Totals"]:
                        player = {}
                        player['name'] = athlete.find('th').text
                        cells = athlete.find_all('td')
                        player['minutes'] = 'DNP'
                        player['team_score']=teams['away_score']
                        player['opp_score']=teams['home_score']
                        player['Team'] = teams['away']
                        player['Date'] = month + '/'+day+'/'+year
                        player['Opponent'] = teams['home']
                        player['Game_Id'] = player['Date'] + '_'+player['Opponent']+'_'+player['Team']
                        player['result'] = teams['away_r']
                        player['started']=False
                        if len(cells)>1:
                            player['minutes'] = cells[0].text
                            player['FG'] = cells[1].text
                            player['FGA'] = cells[2].text
                            player['3P'] = cells[4].text
                            player['3PA'] = cells[5].text
                            player['FT'] = cells[7].text
                            player['FTA'] = cells[8].text
                            player['ORB'] = cells[10].text
                            player['TRB'] = cells[12].text
                            player['AST'] = cells[13].text
                            player['STL'] = cells[14].text
                            player['BLK'] = cells[15].text
                            player['TOV'] = cells[16].text
                            player['PF'] = cells[17].text
                            player['PTS'] = cells[18].text
                            player['+/1'] = cells[19].text
                            if i<5:
                                player['started']=True
                        box.append(player)
                for i, athlete in enumerate(soup.find_all('table')[2].find('tbody').find_all('tr')):
                    if athlete.find('th').text.strip() not in ["Reserves","Team Totals"]:
                        player = {}
                        player['name'] = athlete.find('th').text
                        cells = athlete.find_all('td')
                        player['team_score']=teams['home_score']
                        player['opp_score']=teams['away_score']
                        player['minutes'] = 'DNP'
                        player['Team'] = teams['home']
                        player['Date'] = month + '/'+day+'/'+year
                        player['Opponent'] = teams['away']
                        player['Game_Id'] = player['Date'] + '_'+player['Opponent']+'_'+player['Team']
                        player['result'] = teams['home_r']
                        player['started']=False
                        if len(cells)>1:
                            player['minutes'] = cells[0].text
                            player['FG'] = cells[1].text
                            player['FGA'] = cells[2].text
                            player['3P'] = cells[4].text
                            player['3PA'] = cells[5].text
                            player['FT'] = cells[7].text
                            player['FTA'] = cells[8].text
                            player['ORB'] = cells[10].text
                            player['TRB'] = cells[12].text
                            player['AST'] = cells[13].text
                            player['STL'] = cells[14].text
                            player['BLK'] = cells[15].text
                            player['TOV'] = cells[16].text
                            player['PF'] = cells[17].text
                            player['PTS'] = cells[18].text
                            player['+/1'] = cells[19].text
                            if i<5:
                                player['started']=True
                        box.append(player)
    return pd.DataFrame(box)
df = boxes('2016','2017')

# fix gameIds so they don't only have one format, regardless of which team a player played on

##convert to numpy array to create features I need
array = df.as_matrix()


##this corrected my game ids. I scraped incorrectly.
##I had both '10/25/2016_Cleveland_New York' and '10/25/2016_New York_Cleveland'
ids = df.iloc[0]['Game_Id']
sets = ids.split('_')
for i in range(len(array)):
    set_row = array[i][10].split('_')
    if set(set_row)==set(sets):
        array[i][10] = ids
    else:
        sets = set(set_row)
        ids = array[i][10]
##convert back into a pandas dataframe
df = pd.DataFrame(array,columns=df.columns)


#convert boxscore columns to appropriate type
numeric_cols = [i for i in df.columns if i not in ['Date','Game_Id','Opponent','Team','minutes','name','result','started','+/-']]

for i in df.columns:
    if i in numeric_cols:
        def make_float(row):
            if pd.notnull(row[i]):
                try:
                    return float(row[i])
                except:
                    return np.nan
            else:
                return np.nan
        df[i]=df.apply(make_float,axis=1)



df['Date']=pd.to_datetime(df['Date'])
##create a feature that says whether or not the team is at home
def home(row):
    return row['Game_Id'].split('_')[1]
df['Home_team'] = df.apply(home,axis=1)
df['is_Home']=df['Home_team'] ==df['Team']
df.drop('Home_team',axis=1,inplace=True)
##convert result column to a boolean Team_Win
df['Team_Win'] = df['result'].map({'loser':0,'winner':1})
df.drop('result',axis=1, inplace=True)

##convert other booleans to ints
df['started']= df['started'].apply(int)
df['is_Home']= df['is_Home'].apply(int)
#convert minutes to seconds
def time_played(row):
    if row['minutes']=='DNP':
        return 0
    else:
        time = row['minutes'].split(':')
        return int(time[0])*60+int(time[1])
df['time_played_(s)'] = df.apply(time_played,axis=1)
df.drop('minutes',axis=1,inplace=True)
df.to_csv('NBA_player_data_16-17.csv',index=False)
