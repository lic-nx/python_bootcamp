from collections import Counter
import random
from itertools import combinations

class Game(object):

    def __init__(self, matches=10):
        self.matches = matches
        self.registry = Counter()

    def game_result(self, first_action, second_action):
        if first_action and second_action:
            return (2, 2)
        if not first_action and second_action:
            return (3, -1)
        if first_action and not second_action:
            return (-1, 3)
        return (0, 0)


    def play(self, player1, player2):
        for _ in range(self.matches):
            first_action = player1.action()
            second_action = player2.action()
            p1_result, p2_result = self.game_result(first_action, second_action)
            player1.game_result(p1_result)
            player2.game_result(p2_result)
        if ((
            hasattr(self.registry.keys(), player1.__class__.__name__)
            and player1.coins > self.registry[player1.__class__.__name__])
            or not hasattr(self.registry.keys(), player1.__class__.__name__)
        ):
            self.registry[player1.__class__.__name__] = player1.coins
        if (
            player2.__class__.__name__ in self.registry.keys()
            and player2.coins > self.registry[player2.__class__.__name__]
            or not hasattr(self.registry.keys(), player2.__class__.__name__)
        ):
            self.registry[player2.__class__.__name__] = player2.coins


    def top3(self):
        # Выводим топ 3 по набранным монетам
        top_players = self.registry.most_common(3)
        print("Топ 3 игрока:")
        for i, (name, coins) in enumerate(top_players, 1):
            print(f"{i}. {name} — {coins} монет")


class Player:
    def __init__(self):
        self.cooperating = True
        self.coins = 0

    def action(self):
        return self.cooperating

    def game_result(self, game_result):
        self.coins += game_result
        is_winner = True
        if game_result <= 0:
            is_winner = False
        self.player_reaction(is_winner)


class Cheater(Player):
    def __init__(self):
        super().__init__()
        self.cooperating = False

    def player_reaction(self, is_winner):
        pass


class Cooperator(Player):
    def player_reaction(self, is_winner):
        pass


class Copycat(Player):
    def player_reaction(self, is_winner):
        self.cooperating = is_winner


class Gruder(Player):
    def player_reaction(self, is_winner):
        if not is_winner:
            self.cooperating = False


class Detective(Player):
    def __init__(self):
        super().__init__()
        self.opponent_is_cheat = False
        self.action_dict = [False, True, True]  # Первые три действия

    def player_reaction(self, is_winner):
        if self.opponent_is_cheat:
            self.cooperating = is_winner
            return
        if not is_winner:
            self.opponent_is_cheat = True
        if len(self.action_dict) > 0:
            self.cooperating = self.action_dict.pop()


class Jester(Player):
    def __init__(self):
        super().__init__()
        self.cooperating = random.randint(0, 1)

    def player_reaction(self, is_winner):
        self.cooperating = random.randint(0, 1)


if __name__ == "__main__":
    game = Game()
    players = [Jester(), Detective(), Gruder(), Copycat(), Cooperator(), Cheater()]
    for player1, player2 in combinations(players, 2):
            game.play(player1, player2)
    game.top3()
