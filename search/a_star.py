import heapq
from search.infrastructure import ManOfTheNightsWatch

def a_star(initial_state):
    MIN_STEP_COST = 5
    ICE_STEP_COST = 100
    ICE_BONUS     = 95
    KILL_REWARD   = 500

    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def _nearest_neighbour_chain(agent, targets):
        remaining = list(targets)
        current   = agent
        h         = 0

        while remaining:
            nearest_idx = min(
                range(len(remaining)),
                key=lambda i: _manhattan(current, remaining[i])
            )
            h += _manhattan(current, remaining[nearest_idx]) * MIN_STEP_COST
            current = remaining[nearest_idx]
            remaining.pop(nearest_idx)

        return h
    def _ice_penalty(targets):
        penalty = 0
        for t in targets:
            r, c = t
            if initial_state._original_grid[r, c] == 'B':
                penalty += ICE_BONUS  # = ICE_STEP_COST(100) - MIN_STEP_COST(5)
        return penalty

    def _weapon_adjustment(state, targets):
        if not state.is_enemy_alive():
            return 0  

        weapon_pos = state.get_weapon_position()
        if weapon_pos is None or state.has_weapon():
            return 0  

        cost_to_weapon = _manhattan(state.get_agent_position(), weapon_pos) * MIN_STEP_COST

        if cost_to_weapon < KILL_REWARD:
            net_saving = KILL_REWARD - cost_to_weapon
            return -(net_saving // 4)

        return 0
        


    def heuristic(state):
        agent= state.get_agent_position()
        targets= list(state.get_targets_positions())

        if not targets:
            return 0
        MIN_STEP = 5
        remaining= set(range(len(targets)))
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
        if state.is_enemy_alive() and not state.has_weapon():
            enemy_pos= state.get_enemy_position()
            if enemy_pos:
                nearby = sum(
                    1 for t in targets
                    if abs(t[0] - enemy_pos[0]) + abs(t[1] - enemy_pos[1]) <= 2
                )
                h += nearby * 5  

        return h
    arya=ManOfTheNightsWatch(toward_walls=False, avoid_collision=False)
    pq=[]
    counter= 0
    start_h= heuristic(initial_state)
    heapq.heappush(pq, (start_h, counter, 0.0, initial_state, []))


    while pq :
        f, _,g,current_state, path = heapq.heappop(pq)
        key= arya.state_key(current_state)
        if g >visited.get(key, float('inf')):
            continue

        if arya.is_goal(current_state):
            return path
        for action, cost, next_state in arya.next_states(current_state):
           if next_state.is_collision_state():
                continue

            next_key= arya.state_key(next_state)
            new_g= g + cost
            if new_g < visited.get(next_key, float('inf')):
                visited[next_key]=new_g
                h =heuristic(next_state)
                new_f =new_g + h
                counter += 1
                heapq.heappush(pq, (new_f, counter, new_g, next_state, path + [action]))

    return []
             

