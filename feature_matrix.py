import pandas as pd
data = pd.read_csv('game_boxscores_16-17.csv')
final_data = data[(data['game_number_x']>20) &(data['game_number_y']>20)]
##this returns a matrix of all the average values up to a given data, with some features that I extracted.
final_data.to_csv('Feature_Matrix_16-17.csv')
