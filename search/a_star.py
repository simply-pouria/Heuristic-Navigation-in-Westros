import heapq
from search.infrastructure import ManOfTheNightsWatch


def a_star(initial_state):
    MIN_STEP_COST = 5
    ICE_STEP_COST = 100
    ICE_BONUS = ICE_STEP_COST - MIN_STEP_COST
    HEURISTIC_WEIGHT = 1.15
    TARGET_PROGRESS_BONUS = 60
    BONUS_KILL_ENABLED = True
    WEAPON_REWARD = 300
    KILL_REWARD = 500

    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _nearest_neighbour_chain(agent, targets):
        remaining = list(targets)
        current = agent
        h = 0

        while remaining:
            nearest_idx = min(
                range(len(remaining)),
                key=lambda i: _manhattan(current, remaining[i])
            )
            h += _manhattan(current, remaining[nearest_idx]) * MIN_STEP_COST
            current = remaining[nearest_idx]
            remaining.pop(nearest_idx)

        return h

    mst_cache = {}

    def _mst_cost(targets):
        targets = tuple(sorted(targets))
        if len(targets) <= 1:
            return 0

        if targets in mst_cache:
            return mst_cache[targets]

        used = {targets[0]}
        unused = set(targets[1:])
        total = 0

        while unused:
            best_dist = float('inf')
            best_target = None

            for u in used:
                for v in unused:
                    d = _manhattan(u, v)
                    if d < best_dist:
                        best_dist = d
                        best_target = v

            total += best_dist * MIN_STEP_COST
            used.add(best_target)
            unused.remove(best_target)

        mst_cache[targets] = total
        return total

    def _ice_penalty(targets):
        penalty = 0
        for r, c in targets:
            if initial_state._original_grid[r, c] == 'B':
                penalty += ICE_BONUS
        return penalty

    def _enemy_penalty(state):
        try:
            if not state.is_enemy_alive():
                return 0
        except Exception:
            return 0

        try:
            enemy = state.get_enemy_position()
            agent = state.get_agent_position()
        except Exception:
            return 0

        if enemy is None:
            return 0

        try:
            has_weapon = state.has_weapon()
        except Exception:
            has_weapon = False

        d = _manhattan(agent, enemy)

        if not has_weapon:
            if d <= 1:
                return 120
            if d == 2:
                return 60
            if d == 3:
                return 25
        else:
            return 0

        return 0

    def _weapon_adjustment(state):
        try:
            if not state.is_enemy_alive() or state.has_weapon():
                return 0

            weapon_pos = state.get_weapon_position()
            if weapon_pos is None:
                return 0

            d_weapon = _manhattan(state.get_agent_position(), weapon_pos)
            if d_weapon <= 4:
                return -40
            if d_weapon <= 7:
                return -20
        except Exception:
            return 0

        return 0

    def _enemy_point_and_cost(state, start_pos):
        enemy_positions = []

        try:
            p = state.get_enemy_position()
            if p is not None:
                enemy_positions.append(p)
        except Exception:
            pass

        try:
            p = state.get_enemy_next_position()
            if p is not None:
                enemy_positions.append(p)
        except Exception:
            pass

        if not enemy_positions:
            return None, float('inf')

        best = min(enemy_positions, key=lambda p: _manhattan(start_pos, p))
        return best, _manhattan(start_pos, best) * MIN_STEP_COST

    def _bonus_plan_cost(state, targets):
        try:
            if not BONUS_KILL_ENABLED:
                return float('inf')
            if not state.is_enemy_alive():
                return float('inf')

            weapon_pos = state.get_weapon_position()
            if weapon_pos is None:
                return float('inf')

            agent = state.get_agent_position()

            if state.has_weapon():
                enemy_pos, to_enemy = _enemy_point_and_cost(state, agent)
                if enemy_pos is None:
                    return float('inf')
                return to_enemy + _nearest_neighbour_chain(enemy_pos, targets)

            enemy_pos, weapon_to_enemy = _enemy_point_and_cost(state, weapon_pos)
            if enemy_pos is None:
                return float('inf')
            to_weapon = _manhattan(agent, weapon_pos) * MIN_STEP_COST
            return (
                to_weapon
                + weapon_to_enemy
                + _nearest_neighbour_chain(enemy_pos, targets)
            )
        except Exception:
            return float('inf')

    def _bonus_is_worth_it(state, targets):
        direct_cost = _nearest_neighbour_chain(state.get_agent_position(), targets)
        bonus_cost = _bonus_plan_cost(state, targets)

        try:
            possible_bonus = KILL_REWARD
            if not state.has_weapon():
                possible_bonus += WEAPON_REWARD
        except Exception:
            possible_bonus = KILL_REWARD + WEAPON_REWARD

        extra_cost = bonus_cost - direct_cost
        return extra_cost < possible_bonus

    def _bonus_adjustment(state, targets):
        if not _bonus_is_worth_it(state, targets):
            return 0

        try:
            agent = state.get_agent_position()

            if state.has_weapon():
                _, d_enemy = _enemy_point_and_cost(state, agent)
                return -min(250, max(40, KILL_REWARD - d_enemy) // 2)

            weapon_pos = state.get_weapon_position()
            d_weapon = _manhattan(agent, weapon_pos) * MIN_STEP_COST
            return -min(180, max(30, WEAPON_REWARD - d_weapon) // 2)
        except Exception:
            return 0

    def _should_continue_for_bonus(state):
        try:
            targets = list(state.get_targets_positions())
            if targets:
                return False
            return _bonus_is_worth_it(state, targets)
        except Exception:
            return False

    def heuristic(state):
        agent = state.get_agent_position()
        targets = list(state.get_targets_positions())

        if not targets:
            if _should_continue_for_bonus(state):
                return _bonus_plan_cost(state, targets)
            return 0

        nearest_target = min(_manhattan(agent, t) for t in targets) * MIN_STEP_COST

        mst_h = nearest_target + _mst_cost(targets)
        chain_h = _nearest_neighbour_chain(agent, targets)

        h = max(mst_h, chain_h)

        h += len(targets) * TARGET_PROGRESS_BONUS

        h += _ice_penalty(targets)
        h += _enemy_penalty(state)
        h += _weapon_adjustment(state)
        h += _bonus_adjustment(state, targets)

        return max(h, 0)

    arya = ManOfTheNightsWatch(toward_walls=False, avoid_collision=False)

    pq = []
    counter = 0

    start_h = heuristic(initial_state)
    heapq.heappush(pq, (HEURISTIC_WEIGHT * start_h, start_h, counter, 0.0, initial_state, []))

    visited = {}
    visited[arya.state_key(initial_state)] = 0.0

    while pq:
        f, h, _, g, current_state, path = heapq.heappop(pq)
        key = arya.state_key(current_state)

        if g > visited.get(key, float('inf')):
            continue

        if arya.is_goal(current_state) and not _should_continue_for_bonus(current_state):
            return path

        for action, cost, next_state in arya.next_states(current_state):
            if next_state.is_collision_state():
                continue

            next_key = arya.state_key(next_state)
            new_g = g + cost

            if new_g < visited.get(next_key, float('inf')):
                visited[next_key] = new_g
                next_h = heuristic(next_state)
                counter += 1

                new_f = new_g + HEURISTIC_WEIGHT * next_h
                heapq.heappush(pq, (new_f, next_h, counter, new_g, next_state, path + [action]))

    return []