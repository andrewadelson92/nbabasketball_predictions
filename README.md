# nbabasketball_predictions

This is a repository I created to share my methodology for building a machine learning model to classify NBA point spreads. For example, if the Golden State Warriors are favored by 6, with what accuracy can I predict the correct side of the line? I sort of randomly picked one of the most difficult things to beat in Vegas. I haven't found a profitable strategy, and I don't plan to spend much more energy on this type of bet. Because there is so much data available, and so many people analyzing it already, it is very hard to beat Vegas' predictions, which are bagged classifers. Many experts model this problem already, and their models are weighted appropriately to come up with a better approximation in Vegas. Over the last 15 years, the difference between their approximation and the actual result is normally distributed with a mean at almost EXACTLY 0 and a standard deviation of 12 points. 

The main purpose of this repository is to show the steps I followed in setting up the model to classify these Vegas point spreads. I used the Python library, Beautiful Soup, for web scraping on basketball reference. I then did some Pandas DataFrame manipulation to create a feature matrix for each game, where a game only considers boxscore statistics up to that point in a particular season. I also used Google map's API to add additional features for distance traveled, distance from home, time zone changes, etc. Finally, I created a few booleans that experts usually consider, such as did the team play back to back road games, did they play last night, is the game at a high elevation, etc. Note: I didn't use the first 20 games of the season to train my model, because I considered these games to not have enough data to have valid means. 

The file nba_season_data_function is an iPython notebook that allows one to execute the scraping of the player boxscores, the creation of the team boxscores, and finally the creation of the boxscore features all at once. I also divided the API I followed into four files, which can be executed in the following order to reach the resulting feature matrix: create_player_df.py, create_team_df.py, create_features.py, feature_matrix.py.


