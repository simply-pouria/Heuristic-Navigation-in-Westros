from collections import deque

from infrastructure import ManOfTheNightsWatch
from env.domain import GameState

def bfs(agent: ManOfTheNightsWatch, game: GameState):  # I am probably over-engineering this but anyway
    q = deque()
    q.append(agent.initial_position)
    visited = set()
    visited.add(agent.initial_position)
    while game.is_goal_state():




    pass
