from collections import deque
from search.infrastructure import ManOfTheNightsWatch


def bfs(initial_state):
    arya = ManOfTheNightsWatch(toward_walls=False, avoid_collision=True)

    queue = deque()
    visited = set()

    queue.append((initial_state, []))
    visited.add(arya.state_key(initial_state))

    while queue:
        current_state, path = queue.popleft()

        if arya.is_goal(current_state):
            return path

        for action, cost, next_state in arya.next_states(current_state):
            key = arya.state_key(next_state)

            if key in visited:
                continue

            visited.add(key)
            queue.append((next_state, path + [action]))

    return []



