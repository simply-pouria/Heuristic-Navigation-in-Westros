from typing import Iterable, Protocol, Hashable, Any

# since I am supposed to be the "architect" here, here is a class to creating search interfaces easier for Shayan & Reyhane
class SearchState(Protocol):
    def get_successors(self, toward_walls: bool = False) -> list[tuple[str, float, Any]]:
        ...

    def is_goal_state(self) -> bool:
        ...

    def is_collision_state(self) -> bool:
        ...

    def get_agent_position(self) -> tuple[int, int]:
        ...

    def get_targets_positions(self) -> frozenset[tuple[int, int]]:
        ...

    def get_enemy_cycle(self):
        ...

    def has_weapon(self) -> bool:
        ...

    def is_enemy_alive(self) -> bool:
        ...


class ManOfTheNightsWatch:  # the naming here is not the best SE I had done in my life, but I really like it so-
    """
    This class does not replace GameState.
    It only gives BFS/UCS/A* a clean interface.
    """

    def __init__(self, toward_walls: bool = False, avoid_collision: bool = True):
        self.toward_walls = toward_walls
        self.avoid_collision = avoid_collision

    def is_goal(self, state: SearchState) -> bool:
        return state.is_goal_state()

    def state_key(self, state: SearchState) -> Hashable:
        return (
            state.get_agent_position(),
            frozenset(state.get_targets_positions()),
            state.get_enemy_cycle(),
            state.has_weapon(),
            state.is_enemy_alive(),
        )

    def next_states(self, state: SearchState) -> Iterable[tuple[str, float, SearchState]]:
        for action, cost, next_state in state.get_successors(toward_walls=self.toward_walls):
            if self.avoid_collision and next_state.is_collision_state():
                continue

            yield action, cost, next_state