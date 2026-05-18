import heapq
from search.infrastructure import ManOfTheNightsWatch

def ucs(initial_state):
    arya = ManOfTheNightsWatch(toward_walls=False, avoid_collision=True)
    pq = []
    counter = 0
    heapq.heappush(pq, (0.0, counter, initial_state, []))
    visited = {}
    visited[arya.state_key(initial_state)] = 0.0
    while pq:
        current_cost, _, current_state, path = heapq.heappop(pq)
        if arya.is_goal(current_state):
            return path
        key = arya.state_key(current_state)
        if current_cost > visited.get(key, float('inf')):
            continue
        for action, cost, next_state in arya.next_states(current_state):
            next_key = arya.state_key(next_state)
            new_cost = current_cost + cost
            if new_cost < visited.get(next_key, float('inf')):
                visited[next_key] = new_cost
                counter += 1
                heapq.heappush(pq, (new_cost, counter, next_state, path + [action]))
    return []