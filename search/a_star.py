import heapq
from search.infrastructure import ManOfTheNightsWatch


def a_star(initial_state):
    MIN_STEP_COST = 5
    ICE_STEP_COST = 100
    ICE_BONUS = ICE_STEP_COST - MIN_STEP_COST
    KILL_REWARD = 500

    arya = ManOfTheNightsWatch(
        toward_walls=False,
        avoid_collision=False
    )

    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _grid_cell(pos):
        """
        Safely read a cell from the original grid.

        Supports:
        - NumPy style: grid[r, c]
        - Python list style: grid[r][c]
        - Missing _original_grid
        """
        grid = getattr(initial_state, "_original_grid", None)

        if grid is None:
            return None

        r, c = pos

        try:
            return grid[r, c]
        except Exception:
            try:
                return grid[r][c]
            except Exception:
                return None

    def _nearest_neighbour_chain(agent, targets):
        remaining = list(targets)
        current = agent
        h = 0

        while remaining:
            nearest_idx = min(
                range(len(remaining)),
                key=lambda i: _manhattan(current, remaining[i])
            )

            nearest_target = remaining[nearest_idx]
            h += _manhattan(current, nearest_target) * MIN_STEP_COST

            current = nearest_target
            remaining.pop(nearest_idx)

        return h

    def _ice_penalty(targets):
        penalty = 0

        for target in targets:
            if _grid_cell(target) == "B":
                penalty += ICE_BONUS

        return penalty

    def _weapon_adjustment(state, targets):
        if not state.is_enemy_alive():
            return 0

        if state.has_weapon():
            return 0

        weapon_pos = state.get_weapon_position()

        if weapon_pos is None:
            return 0

        agent_pos = state.get_agent_position()
        cost_to_weapon = _manhattan(agent_pos, weapon_pos) * MIN_STEP_COST

        if cost_to_weapon < KILL_REWARD:
            net_saving = KILL_REWARD - cost_to_weapon
            return -(net_saving // 4)

        return 0

    def heuristic(state):
        agent = state.get_agent_position()
        targets = list(state.get_targets_positions())

        if not targets:
            return 0

        h = 0
        h += _nearest_neighbour_chain(agent, targets)
        h += _ice_penalty(targets)
        h += _weapon_adjustment(state, targets)

        return max(h, 0)

    pq = []
    counter = 0

    start_g = 0
    start_h = heuristic(initial_state)
    start_f = start_g + start_h

    heapq.heappush(
        pq,
        (start_f, counter, start_g, initial_state, [])
    )

    visited = {
        arya.state_key(initial_state): start_g
    }

    while pq:
        f, _, g, current_state, path = heapq.heappop(pq)

        current_key = arya.state_key(current_state)

        if g > visited.get(current_key, float("inf")):
            continue

        if arya.is_goal(current_state):
            return path

        for action, cost, next_state in arya.next_states(current_state):
            if next_state.is_collision_state():
                continue

            next_key = arya.state_key(next_state)
            new_g = g + cost

            if new_g < visited.get(next_key, float("inf")):
                visited[next_key] = new_g

                h = heuristic(next_state)
                new_f = new_g + h

                counter += 1

                heapq.heappush(
                    pq,
                    (new_f, counter, new_g, next_state, path + [action])
                )

    return []