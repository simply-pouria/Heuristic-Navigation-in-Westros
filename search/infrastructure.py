from env.domain import GameState


class ManOfTheNightsWatch:  # the naming here is not the best SE I had done in my life, but I really like it so-
    def __init__(self, initial_position: (int, int), collected_targets: frozenset[(int, int)]):
        self.initial_position = initial_position
        self.collected_targets = collected_targets

    def next_state(self, game: GameState):
        for action, cost, next_state in game.get_successors():
            





