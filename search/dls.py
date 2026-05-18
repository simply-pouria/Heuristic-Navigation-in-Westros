from search.infrastructure import ManOfTheNightsWatch


def dls(initial_state):
    arya = ManOfTheNightsWatch(toward_walls=False, avoid_collision=True)

    def depth_limited_search(state, depth, path, visited):
        if arya.is_goal(state):
            return path
        if depth <= 0:
            return None
        key = arya.state_key(state)
        if key in visited and visited[key] >= depth:
            return None
        visited[key] = depth
        for action, cost, next_state in arya.next_states(state):
            result = depth_limited_search(next_state, depth - 1, path + [action], visited)
            if result is not None:
                return result
        return None

    for limit in range(201):
        visited = {}
        result = depth_limited_search(initial_state, limit, [], visited)
        if result is not None:
            return result
    return []