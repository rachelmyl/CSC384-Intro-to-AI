#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# initialize prev_state and prev_heuristic
if 'prev_state' not in globals():
    prev_state = None
if 'prev_heur' not in globals():
    prev_heur = None 

# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    '''
    1. check deadlock condition using deadlock()
    2. after checking whether the puzzle is solvable and we still need to move
    3. we calculate the optimal heuristic value considering:
        1) the robots position and their possible movements
        2) the obstacles
    '''
    
    global prev_state
    global prev_heur
    
    if prev_state == state.boxes: 
        return prev_heur            # if the algorithm doesn't make any move, return
    else:
        prev_state = state.boxes    # update new state
        
    ext_box = list(set(state.boxes) - set(state.storage))
    ext_storage = list(set(state.storage) - set(state.boxes))
    # boxes and storages that haven't been settled
    
    if deadlock(state, ext_box, ext_storage):
        prev_heur = math.inf
        return prev_heur
    else:
        # the state is solvable and we have other moves to do
        sum_dist = 0
        dist_robot_to_box = {}
        for box in ext_box:
            min_dist_from_robot = math.inf
            for robot in state.robots:
                rb = (robot, box)
                if rb not in dist_robot_to_box:
                    dist_robot_to_box[rb] = manhattan_dist(robot, box) + obstacle_count(state, box, robot)
                min_dist_from_robot = min(min_dist_from_robot, dist_robot_to_box[rb])
            
            min_dist_to_storage = math.inf
            for storage in ext_storage:
                bs = (box, storage)
                if bs not in dist_robot_to_box:  
                    dist_robot_to_box[bs] = manhattan_dist(box, storage) + obstacle_count(state, storage, box)
                min_dist_to_storage = min(min_dist_to_storage, dist_robot_to_box[bs])
            
            sum_dist += min_dist_from_robot + min_dist_to_storage
        
        prev_heur = sum_dist
        return prev_heur
    
'''ADDED: calculate the attribute we want to take into account other than mahattan distance'''
def obstacle_count(state, destination, start):
    '''
    Return a list of every point on the Manhattan path between position1 and position2,
    moving only horizontally or vertically.
    '''
    obstacle_list = list(state.boxes) + list(state.obstacles) + list(state.robots)
    if (destination in obstacle_list):
        obstacle_list.remove(destination)
    if (start in obstacle_list):
        obstacle_list.remove(start) 
    
    path = path_between(start, destination)
    count = 0
    for i in path:
        if i in obstacle_list:
            count += 3
    return count
    
def path_between(pos1, pos2):
    '''Algorithm: first move in x direction and then y (CAN BE MODIFIED FOR TESTING OPTIMAL)'''
    path = [pos1]
    x1, y1 = pos1
    x2, y2 = pos2

    # Move horizontally first
    step_x = 1 if x2 > x1 else -1
    for x in range(x1, x2, step_x):
        path.append((x + step_x, y1))

    # Move vertically next
    step_y = 1 if y2 > y1 else -1
    for y in range(y1, y2, step_y):
        path.append((x2, y + step_y))

    return path

'''ADDED: help check the deadlock situation, return yes if the box cannot move anymore'''
def deadlock(state, ext_box, ext_storage):
    '''
    There is 2 possible situation that the box cannot move any more
    1. the box is adjacent to at least two obstable/wall at two non-opposite sides
        1) the box is at one of four corners OR
        2) the box is trapped in the corner set up by wall/obstacle |_
    2. the box is by the wall but there's no storage along that side
        Note: no move to pull the box away from that wall
    Input: state, remaining box and storage
    Ouput: yes for deadlock, no for no deadlock
    '''
    
    for box in ext_box:
        if corner_deadlock(state, box):
            return True
        elif along_wall_deadlock(state, box, ext_storage):
            return True
        
    return False

def corner_deadlock(state, box):
    '''Situation one described in deadlock()'''
    pos = set(state.obstacles).union(set(state.boxes))
    
    up = (box[0], box[1] - 1)
    down = (box[0], box[1] + 1)
    left = (box[0] - 1, box[1])
    right = (box[0] + 1, box[1])
    
    if (box[1] == 0 or box[1] == state.height - 1) and (box[0] == 0 or box[0] == state.width - 1):
        return True
    elif (up in pos or down in pos) and (left in pos or right in pos):
        return True
    elif (box[1] == 0 or box[1] == state.height - 1) and (left in pos or right in pos):
        return True
    elif (up in pos or down in pos) and (box[0] == 0 or box[0] == state.width - 1):
        return True
    
    return False

def along_wall_deadlock(state, box, available_storage):
    '''Situation 2 described in deadlock()'''
    if box[1] == 0:
        # is against vertical wall
        for storage in available_storage:
            if storage[1] == 0:
                return False
    elif box[1] == state.height - 1:
        for storage in available_storage:
            if storage[1] == state.height - 1:
                return False
    elif box[0] == 0:
        # is against horizontal wall
        for storage in available_storage:
            if storage[0] == 0:
                return False
    elif box[0] == state.width - 1:
        for storage in available_storage:
            if storage[0] == state.width - 1:
                return False
    else: 
        return False        # not near the wall
    
    return True

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    sum = 0
    for box in state.boxes:
        dist = math.inf     # for each box, see which storage is the closest
        for storage in state.storage:
            dist = min(dist, manhattan_dist(box, storage))
        sum += dist
    return sum

'''ADDED: calculate the closest manhattan distance sum for every boxes'''
def manhattan_dist(box, storage):
    man_dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
    return man_dist

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    
    S_engine = SearchEngine('custom', 'full')
    wrapped_fval_funtion = lambda sN: fval_function(sN, weight) # Given in part 6
    deadline = os.times()[4] + timebound  
    
    S_engine.init_search(initial_state, goal_fn = sokoban_goal_state, heur_fn = heur_fn, fval_function = wrapped_fval_funtion)
    final, stats = S_engine.search(timebound=(deadline - os.times()[4]), costbound=(math.inf, math.inf, math.inf))
    
    return final, stats

def iterative_astar(initial_state, heur_fn, weight=1, timebound=10):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    S_engine = SearchEngine('custom', 'full')
    wrapped_fval_function = lambda sN: fval_function(sN, weight)
    deadline = os.times()[4] + timebound
    
    S_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    countdown = deadline - os.times()[4]
    best_result = 0
    best_gval = math.inf
    first_search = True
    
    while (countdown > 0):
        found, stats = S_engine.search(timebound = countdown, costbound=(math.inf, math.inf, best_gval))
        # best gval should be lowest g value till now
        '''
        costbound[a, b, c]
        a = pathcost - g value (actual cost ammunulated so far to reach a node)
        b = heuristic calue - h value (estimated of remaining cost to reach the goal from the node)
        c = total estimation cost - f value (f = g+h; lower f value more likely to be optimal)
        '''
        weight = weight * 0.5
        if found == False:
            if (first_search):
                return found, stats
        else:
            if (best_gval > found.gval):
                best_gval = found.gval
                best_result = found, stats
        first_search = False
        countdown = deadline - os.times()[4]
        '''
        if time_left < 0:
            return best_result[0], best_result[1]
        '''
        
    return best_result[0], best_result[1]

def iterative_gbfs(initial_state, heur_fn, timebound=10):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    S_engine = SearchEngine('best_first', "full")
    deadline = os.times()[4] + timebound
    
    S_engine.init_search(initial_state, sokoban_goal_state, heur_fn, fval_function)
    countdown = deadline - os.times()[4]
    best_result = 0
    best_gval = math.inf
    first_search = True

    while (countdown > 0):
        found, stats = S_engine.search(timebound=countdown, costbound=(best_gval, math.inf, math.inf))
        if found == False:
            if(first_search):
                return found, stats
        else:
            if (best_gval > found.gval):
                best_gval = found.gval
                best_result = found, stats
        first_search = False
        countdown = deadline - os.times()[4]
        
    return best_result[0], best_result[1] 


