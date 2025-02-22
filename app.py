from Team import *
import pandas as pd
import pyodbc

def game_history_query(game_num:int):
    game_str = str(game_num)
    query_string = (
    'SELECT p.player_id, p.town_rating, p.wolf_rating, r.role_id, r.team, r.role_rating\n'
    'FROM (history AS h INNER JOIN roles AS r ON h.role_id = r.role_ID) INNER JOIN players AS p ON h.player_id = p.player_id\n'
    'WHERE h.game_id = '+game_str+';'
    )
    return query_string

def create_roles_update(role_id: int, new_rating):

    update_string = (
    'UPDATE roles\n'
    'SET role_rating ='+str(new_rating)+'\n'
    'WHERE role_id = '+str(role_id)
    )
    return update_string

def create_player_update(player_id, new_rating, team:str):
    team_string = team+'_rating'

    update_string = (
    'UPDATE players\n'
    'SET '+team_string+' = '+str(new_rating)+'\n'
    'WHERE player_id = '+str(player_id)
    )
    return update_string

def sort_team_roles(game_df):
    town = Team(name='town')
    wolves = Team(name='wolf')

    for index, row in game_df.iterrows():
        player = Player(int(row['role_id']), float(row['role_rating']))
        if row['team'] == 'Town':
            town.add_player(player)
        else:
            wolves.add_player(player)

    town.update_rating_sum()
    wolves.update_rating_sum()

    return (town, wolves)

def sort_team_players(game_df):
    town = Team(name='town')
    wolves = Team(name='wolf')

    for index, row in game_df.iterrows():
        if row['team'] == 'Town':
            player = Player(int(row['player_id']), float(row['town_rating']))
            town.add_player(player)
        else:
            player = Player(int(row['player_id']), float(row['wolf_rating']))
            wolves.add_player(player)

    town.update_rating_sum()
    wolves.update_rating_sum()

    return (town, wolves)

def main():

    connStr = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=D:\saved_data\moneywolf\moneywolf.accdb;"
    )
    cnxn = pyodbc.connect(connStr, autocommit=True)
    crsr = cnxn.cursor()

    games_query = (
    'SELECT * FROM games;'
    )
    games_raw = pd.read_sql(games_query, cnxn)
    games = games_raw.copy(deep=True)
    games.set_index('game_id', inplace=True)
    games_list = games.index

    for game_no in games_list:
        game_results_qry = game_history_query(game_no)
        game = pd.read_sql(game_results_qry, cnxn)

        town_roles, wolf_roles = sort_team_roles(game)
        town_players, wolf_players = sort_team_players(game)

        if games.loc[game_no, 'town_win'] == True:
            town_roles.match_win(wolf_roles)
            town_players.match_win(wolf_players)
        else:
            wolf_roles.match_win(town_roles)
            wolf_players.match_win(town_players)

        update_strings_list = []

        for team in [town_roles, wolf_roles]:
            for player in team.player_list:
                update_string = create_roles_update(player.id, player.rating)
                update_strings_list.append(update_string)
        
        for team in [town_players, wolf_players]:
            for player in team.player_list:
                update_string = create_player_update(player.id, player.rating, team.name)
                update_strings_list.append(update_string)
        
        for update in update_strings_list:
            crsr.execute(update)

    cnxn.close()

    return None

if __name__ == '__main__':
    main()