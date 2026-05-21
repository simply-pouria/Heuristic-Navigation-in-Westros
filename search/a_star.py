import heapq
from search.infrastructure import ManOfTheNightsWatch

def a_star(initial_state):
    def heuristic(state):
        agent = state.get_agent_position()
        targets = list(state.get_targets_positions())

        if not targets:
            return 0
        MIN_STEP = 5
        remaining = set(range(len(targets)))
        current = agent
        h = 0
        while remaining:
            nearest_idx = min(
                remaining,
                key=lambda i: (
                    abs(targets[i][0] - current[0])
                    + abs(targets[i][1] - current[1])
                )
            )
            dist = (
                abs(targets[nearest_idx][0] - current[0])
                + abs(targets[nearest_idx][1] - current[1])
            )
            h += dist * MIN_STEP
            current = targets[nearest_idx]
            remaining.remove(nearest_idx)

    pass

