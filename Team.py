from Player import *

class Team():
    def __init__(self, name: str):
        self.player_list = []
        self.num_players = -1
        self.rating_sum = -1
        self.name = name

    def show(self):
        for player in self.player_list:
            player.show()
        print(f'current total rating: {self.rating_sum}')
        return None

    def add_player(self, new_team_member):
        self.player_list.append(new_team_member)
        return None

    def update_rating_sum(self):
        total_rating = 0
        for player in self.player_list:
            total_rating += player.rating
        self.rating_sum = total_rating
        return None
    
    def update_num_players(self):
        self.num_players = len(self.player_list)
        return None

    def return_expected_score(self, team_b):
        expected_win = 1 / (1 + 10**((team_b.rating_sum - self.rating_sum)/400))
        return expected_win

    def match_win(self, team_b):
        expected_a_win = self.return_expected_score(team_b)
        expected_b_win = team_b.return_expected_score(self)

        self.update_num_players()
        team_b.update_num_players()
        all_players = self.num_players + team_b.num_players

        score_a = float((1 - expected_a_win) * ((all_players - 6)**2))
        score_b = float((0 - expected_b_win) * ((all_players - 6)**2))

        for player in self.player_list:
            player.rating = player.rating + (float((abs(player.rating) / self.rating_sum) * score_a))

        for player in team_b.player_list:
            player.rating = player.rating + (float((abs(player.rating) / team_b.rating_sum) * score_b))

        return None