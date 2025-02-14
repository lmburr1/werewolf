import pandas as pd
import trueskill as ts
import pyodbc

def create_roles_query(game_num:int):
    game_str = str(game_num)
    query_string = (
    'SELECT g.town_win, r.role_id, r.role_mu, r.role_sigma\n'
    'FROM (history AS h INNER JOIN games AS g ON h.game_id = g.game_id) INNER JOIN roles AS r ON h.role_id = r.role_ID\n'
    'WHERE g.game_id = '+game_str+';'
    )
    return query_string

def create_update_query(role_id: int, new_rating):
    new_mu = new_rating.mu
    new_sigma = new_rating.sigma

    update_string = (
    'UPDATE roles\n'
    'SET role_mu = '+str(new_mu)+', role_sigma = '+str(new_sigma)+'\n'
    'WHERE role_id = '+str(role_id)
    )
    return update_string

def create_update_list(updated_team_ratings:list):
    list_of_update_strings = []

    for team in updated_team_ratings:
        for key in team:
            list_of_update_strings.append(create_update_query(key, team[key]))
    
    return list_of_update_strings


def create_town_wolf_dicts(full_role_list: list, roles_df):
# input full roles list and roles dataframe
# return list of two dictionaries of the form {role_id: Rating()}
# one each for town and wolves

    town_dict = {}
    wolf_dict = {}

    for role in full_role_list:
        obj = ts.Rating(mu = roles_df.loc[role, 'role_mu'], sigma = roles_df.loc[role, 'role_sigma'])
        if roles_df.loc[(role, 'team')] == 'Town':
            town_dict[role] = obj
        else:
            wolf_dict[role] = obj
    
    ratings_list = [town_dict, wolf_dict]
    return ratings_list

def run_game(list_of_dicts: list, score_list: list):
    updated_team_ratings = ts.rate(list_of_dicts, score_list)
    return updated_team_ratings

def df_rating_update(roles_df, updated_team_ratings: list):

    for key in updated_team_ratings[0]:
        updated_team_ratings[0][key] = updated_team_ratings[0][key]
        roles_df.loc[key, 'role_mu'] = updated_team_ratings[0][key].mu
        roles_df.loc[key, 'role_sigma'] = updated_team_ratings[0][key].sigma

    for key in updated_team_ratings[1]:
        updated_team_ratings[1][key] = updated_team_ratings[1][key]
        roles_df.loc[key, 'role_mu'] = updated_team_ratings[1][key].mu
        roles_df.loc[key, 'role_sigma'] = updated_team_ratings[1][key].sigma

    return roles_df

def main():

    connStr = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=D:\saved_data\moneywolf\moneywolf.accdb;"
    )
    cnxn = pyodbc.connect(connStr, autocommit=True)
    crsr = cnxn.cursor()

    roles_query = (
    'SELECT * FROM roles;'
    )
    roles_raw = pd.read_sql(roles_query, cnxn)
    roles = roles_raw.copy(deep=True)
    roles.set_index('role_id', inplace=True)

    games_query = (
    'SELECT * FROM games;'
    )
    games_raw = pd.read_sql(games_query, cnxn)
    games = games_raw.copy(deep=True)
    games.set_index('game_id', inplace=True)
    games_list = games.index

    for game_id in games_list:
        game_results_qry = create_roles_query(game_id)
        game = pd.read_sql(game_results_qry, cnxn)  

        role_id_list = game['role_id'].unique().tolist()

        ratings_list = create_town_wolf_dicts(role_id_list, roles)

        if game.iloc[(1,0)] == 1:
            score = [0,1]
        else:
            score = [1,0]

        updated_ratings = run_game(ratings_list, score)
        roles = df_rating_update(roles, updated_ratings)
        update_strings_list = create_update_list(updated_ratings)
        for update in update_strings_list:
            crsr.execute(update)

    cnxn.close()
    roles.to_csv('updated_roles.csv', encoding = 'utf-8', header = True)

    return None

if __name__ == '__main__':
    main()