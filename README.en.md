**Language:** [فارسی](README.md) | English (AI-Translated)

tags: [[Uni AI Course]]

## Heuristic Navigation in Westeros

# 1. Shared Infrastructure in `infrastructure.py`

To avoid duplicating code across the different search files, a helper class named `ManOfTheNightsWatch` is defined in `infrastructure.py`. This class acts as an adapter between the search algorithms and the game environment.

Algorithms such as `bfs.py`, `ucs.py`, `dls.py`, and `a_star.py` should not have to deal directly with the many details of `GameState`. Therefore, tasks such as constructing a unique key for a state, obtaining successors, and filtering dangerous collisions are handled by this class.

## 1.1 The `state_key` Method

The main responsibility of `state_key` is to create a hashable representation of each `GameState`. This key is used to detect repeated states in a `visited set` or `visited dictionary`.

In this project, the state key includes:

- the agent's current position;
- the set of remaining targets;
- the current phase of the enemy's movement cycle;
- whether the agent has the weapon;
- whether the Night King is still alive.

This information is sufficient for the search algorithms to distinguish states that can lead to different future behavior. For example, if Arya is standing on the same cell in two states but the remaining targets are different, those states must not be treated as identical. Likewise, acquiring the weapon or killing the Night King changes the future behavior of the environment, so these properties must also be included in the state key.

## 1.2 The `next_states` Method

The `next_states` method is responsible for generating successor states. It uses the environment's provided `get_successors()` function and converts its output into a form suitable for search.

Each successor contains three components:

- the action that was performed;
- the cost of that action;
- the new state after performing the action.

When `avoid_collision` is enabled, the method removes successors that cause dangerous collisions. This is particularly useful for uninformed algorithms such as **BFS**, **UCS**, and **DLS**, because these algorithms do not themselves have a special understanding of the danger posed by the Night King.

For **A\***, enemy collisions are handled more carefully because, in the bonus mode, colliding with the Night King is no longer a failure if Arya has the weapon; the collision can instead kill the enemy.

---

# 2. BFS Algorithm

## 2.1 Purpose of BFS

**BFS**, or **Breadth-First Search**, is an uninformed search algorithm. It explores states according to their depth: first all paths of length 1, then all paths of length 2, then length 3, and so on.

In this project, BFS finds the shortest path in terms of the number of actions, not the actual cost of the path.

Therefore, if a short path crosses expensive ice cells, BFS may still select it even when another route has more actions but a lower total cost.

## 2.2 BFS Data Structure

The BFS implementation uses `deque` because BFS requires a FIFO queue.

Each queue entry contains:

`current_state, path`

where `path` is the list of actions taken from the initial state to the current state.

A `visited set` is also maintained so that repeated states are not expanded again.

## 2.3 BFS Execution Process

The overall BFS procedure in this project is:

1. Insert the initial state into the queue.
2. Add the initial state to `visited`.
3. At each step, remove the oldest state from the queue.
4. If the current state is a goal, return the path.
5. Otherwise, generate the valid successors.
6. Add each previously unseen successor to the queue.
7. If no solution is found, return an empty path.

## 2.4 BFS Analysis

The advantage of BFS is that it is simple, complete, and reliable. If the state space is finite and a solution exists, BFS will find it.

Its main limitation is that it ignores path cost. Because different terrain types in this project have different costs, BFS does not always produce the best route in terms of final score or total cost.

For this reason, BFS is used mainly as a baseline for comparison with more advanced algorithms.

---

# 3. UCS Algorithm

## 3.1 Purpose of UCS

**UCS**, or **Uniform-Cost Search**, is the cost-aware counterpart of uninformed breadth-first exploration. Unlike BFS, which considers only the number of steps, UCS always expands the path with the lowest accumulated cost so far.

UCS is especially important in this project because movement over normal, snowy, and icy cells, as well as interactions with the enemy, can have different costs.

## 3.2 UCS Data Structure

UCS uses a `priority queue` implemented with `heapq`.

Each priority-queue entry contains:

`current_cost, counter, current_state, path`

Here, `current_cost` is `g(n)`, the actual cost of the path from the initial state to the current state.

The `counter` variable prevents comparison errors between states. If two states have the same priority, Python might otherwise attempt to compare the state objects themselves, which can cause an error.

## 3.3 `visited` in UCS

Unlike BFS, in UCS it is not enough to know that a state has already been seen. A state may previously have been reached with a high cost and later be found again through a cheaper path.

Therefore, UCS uses a dictionary:

`visited[state_key] = best_cost`

If the algorithm reaches the same state with a lower cost, the stored value is updated and the state is inserted into the priority queue again.

## 3.4 UCS Execution Process

The UCS procedure is:

1. Insert the initial state into the priority queue with cost zero.
2. Remove the state with the lowest cost.
3. If the current state is a goal, return the path.
4. Generate the valid successors.
5. Compute the new cost for each successor.
6. If this cost is better than the previously recorded cost, insert the successor into the queue.

## 3.5 UCS Analysis

UCS is complete and optimal when all costs are positive. If allowed to run to completion, it finds the least-cost path.

Its main weakness is that it has no heuristic: it does not know where the targets are and advances only according to the accumulated path cost. On large maps, this can cause many states to be expanded.

Therefore, UCS is suitable for cost-sensitive paths but is slower than A\* in this project.

---

# 4. DLS / IDS Algorithm

## 4.1 Purpose of DLS

**DLS**, or **Depth-Limited Search**, is a depth-first search with a depth limit. In this project, it is implemented iteratively: the depth limit starts at a small value and is gradually increased.

This behavior is similar to **IDS**, or **Iterative Deepening Search**.

## 4.2 Execution Process

The main function runs the search for different depth limits. At each depth, the following recursive function is used:

`depth_limited_search(state, depth, path, visited)`

This function checks:

1. whether the current state is a goal;
2. whether the depth has reached zero;
3. whether this state has already been seen with an equal or better remaining depth;
4. and then recursively explores the successors.

## 4.3 `visited` in DLS

To avoid unnecessary repetition, DLS uses a dictionary:

`visited[key] = depth`

If a state has already been seen with an equal or greater remaining depth, exploring it again is not useful. This reduces the number of expansions.

## 4.4 DLS Analysis

DLS uses less memory than BFS because it explores paths depth-first.

Its limitation is that, if the depth limit is not appropriate, it may fail to find the solution. IDS partly addresses this problem by gradually increasing the depth limit.

However, IDS may examine some states multiple times at different depths, so it can become slow on large maps.

---

# 5. A\* Algorithm

## 5.1 Purpose of A\*

**A\*** is the most important algorithm in this project because it uses a heuristic to reduce the number of expanded nodes.

Unlike UCS, A\* considers not only the cost already incurred but also an estimate of the remaining cost to the goal.

Its general formula is:

`f(n) = g(n) + h(n)`

In this implementation, a heuristic weight is also used:

`f(n) = g(n) + weight * h(n)`

`HEURISTIC_WEIGHT` is set to `1.15`. This makes the algorithm somewhat more aggressive in moving toward the targets and reduces the number of expanded nodes. Because the heuristic is weighted, however, this version of A\* no longer guarantees strict optimality. For the project's objective of reducing the number of expanded nodes, it performs better.

---

## 5.2 A\* Data Structure

Like UCS, A\* uses a `priority queue` implemented with `heapq`.

Each queue entry contains:

`f, h, counter, g, state, path`

where:

- `g` is the actual path cost to the current state;
- `h` is the heuristic estimate of the remaining cost;
- `f` is the weighted combination of those values;
- `path` is the sequence of actions leading to the current state.

The algorithm always expands the state with the smallest `f` value.

---

# 6. Heuristic Used in A\*

The implemented heuristic is not merely a simple distance function. Its purpose is to interact with the structure of the environment and better account for the actual state of the map.

Several components are therefore used in the heuristic.

## 6.1 Manhattan Distance

The first component is **Manhattan Distance**. Because the agent moves only in the four cardinal directions, Manhattan Distance is an appropriate distance estimate.

This distance is multiplied by the minimum step cost to convert it into an approximate path cost.

---

## 6.2 Nearest Target

The heuristic first computes the distance from the agent to the nearest remaining target. This prevents A\* from spreading aimlessly across the map and encourages it to move toward the nearest useful objective.

However, considering only the nearest target is not enough, because the agent must collect all targets rather than just one.

---

## 6.3 MST for the Remaining Targets

To give the heuristic a more global view of all remaining targets, the implementation uses the idea of an **MST**, or **Minimum Spanning Tree**.

The MST provides an estimate of the minimum cost required to connect all remaining targets. This helps A\* account for the amount of work that will still remain after reaching one target.

For efficiency, MST values for repeated target sets are cached in `mst_cache`, preventing the heuristic from recomputing the same value for equivalent target sets.

---

## 6.4 Nearest-Neighbour Chain

Alongside the MST, a greedy estimate is also used. Starting from the current position, this estimate selects the nearest target, then moves from that target to the next nearest target, and continues in the same manner.

This is implemented as `nearest_neighbour_chain`.

The MST provides a global estimate, whereas the nearest-neighbour chain more closely resembles an actual route. Combining the two produces a stronger heuristic.

---

## 6.5 Target Progress Bonus

The number of remaining targets is also important to the heuristic. A state with fewer targets remaining is generally preferable.

For this reason, the heuristic is sensitive to the number of remaining targets. This allows A\* to recognize that collecting a target is itself meaningful progress, rather than treating all movement purely as changes in position.

---

## 6.6 Accounting for Ice

Because moving over ice has a high cost, the heuristic is sensitive to targets located on expensive terrain.

This helps A\* avoid routes that appear short in terms of distance but are expensive in terms of actual path cost.

---

## 6.7 Accounting for the Night King

The heuristic is also sensitive to Arya's distance from the Night King. If Arya does not yet have the weapon, approaching the Night King is dangerous.

Therefore, when the agent is close to the enemy, the heuristic adds a penalty. The smaller the distance, the larger the penalty.

This prevents A\* from being blind to the enemy and makes dangerous routes less attractive.

---

# 7. Bonus Section: Weapon and Killing the Night King

In the bonus section, some maps contain a weapon. When Arya reaches the weapon cell, `has_weapon` becomes active. From that point onward, colliding with the Night King is no longer considered a failure.

If Arya reaches the Night King's cell while carrying the weapon, the enemy is removed and `is_enemy_alive` becomes false.

After the Night King is killed:

- the enemy is no longer a threat to the agent;
- the collision penalty is removed;
- subsequent paths become less constrained and safer.

An important point is that the algorithm should not always choose to collect the weapon. According to the project specification, the agent should decide intelligently whether moving toward the weapon and killing the Night King is worthwhile.

In the A\* implementation, the heuristic compares the approximate cost of going to the weapon and then to the enemy with the cost of a more direct route. If collecting the weapon and eliminating the enemy makes sense in terms of cost and reward, the weapon route becomes more attractive. Otherwise, the agent does not disrupt its route merely because a weapon exists.

---
