import sys
import cv2
import random
from map import Map
import utils

ESCAPE_KEY_CHARACTER = 27
SLEEP_TIME_IN_MILLISECONDS = 500

GRAPH = {}
COLORED_STATES = {}
N_COLORS = 4
COLORING_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
NONE_COLOR = (0, 0, 0)
BACKTRACK_COUNT = 0

MAP = None
FILTERING_MODE = None
USE_VARIABLE_ORDERING = None
USE_VALUE_ORDERING = None


def colorize_map(manual=False):
    for i in range(len(MAP.nodes)):
        if (COLORED_STATES[i] == None):
            MAP.change_region_color(MAP.nodes[i], NONE_COLOR)
        else:
            MAP.change_region_color(MAP.nodes[i], COLORING_COLORS[COLORED_STATES[i]])
    cv2.imshow('Colorized Map', MAP.image)
    if not manual:
        key = cv2.waitKey(SLEEP_TIME_IN_MILLISECONDS)
    else:
        key = cv2.waitKey()
    if key == ESCAPE_KEY_CHARACTER:
        cv2.destroyAllWindows()
        exit()


'''BACKTRACKING CSP SOLVER'''


def backtrack_solve(domains):
    """
    Returns True when the CSP is solved, and False when backtracking is necessary.

    You will need to use the global variables GRAPH and COLORED_STATES, refer to preprocess() and try to see what they represent.
    Use FILTERING_MODE, USE_VARIABLE_ORDERING, and USE_VALUE_ORDERING for branching into each mode.
    FILTERING_MODE is either "-n", "-fc", or "ac", and the other two are booleans.

    HINT: You may want to import deepcopy to generate the input to the recursive calls.
    NOTE: Remember to call colorize_map() after each value assignment for the graphical update.
              Use colorize_map(True) if you want to manually progress by pressing any key.
    NOTE: Don't forget to update BACKTRACK_COUNT on each backtrack.
    """
    global BACKTRACK_COUNT
    if utils.is_solved(GRAPH, COLORED_STATES):
        print("solved")
        print(f"backtrack count: {BACKTRACK_COUNT}")
        colorize_map(True)
        exit(0)

    next_var = utils.get_chosen_variable(GRAPH, COLORED_STATES,
                                         domains) if USE_VARIABLE_ORDERING else utils.get_next_variable(COLORED_STATES,
                                                                                                        domains)
    if next_var is None:
        return


    if FILTERING_MODE == '-ac' and utils.ac3(GRAPH, COLORED_STATES, domains):
        return


    ordered_domain = domains[next_var] if not USE_VALUE_ORDERING else utils.get_ordered_domain(GRAPH, domains, next_var)

    print(ordered_domain)
    for value in ordered_domain:
        COLORED_STATES[next_var] = value
        colorize_map(True)

        if not utils.is_consistent(GRAPH, COLORED_STATES):
            BACKTRACK_COUNT += 1
            continue

        domains_copy = [l.copy() for l in domains]
        domains_copy[next_var] = [value]

        if FILTERING_MODE == '-fc' and utils.forward_check(GRAPH, COLORED_STATES, domains_copy, next_var, value):
            BACKTRACK_COUNT += 1
            continue

        elif FILTERING_MODE == '-ac' and utils.ac3(GRAPH, COLORED_STATES, domains_copy):
            continue

        backtrack_solve(domains_copy)
        BACKTRACK_COUNT += 1

    COLORED_STATES[next_var] = None


'''ITERATIVE IMPROVEMENT SOLVER'''


def iterative_improvement_solve(domains, max_steps=100):
    """
    Solves the CSP iteratively by initializing all variables randomly and then changing conflicting values until solved, using max_steps to avoid infinite loops.

    You will need to use the global variables GRAPH and COLORED_STATES, refer to preprocess() and try to see what they represent.
    Don't forget to call colorize_map().
    """
    for state in COLORED_STATES:
        COLORED_STATES[state] = random.randint(0, len(COLORING_COLORS) - 1)

    colorize_map(True)
    steps = 0
    while steps < max_steps and not utils.is_solved(GRAPH, COLORED_STATES):
        steps += 1
        var = utils.random_choose_conflicted_var(GRAPH, COLORED_STATES)
        val = utils.get_chosen_value(GRAPH, COLORED_STATES, domains, var)
        COLORED_STATES[var] = val
        colorize_map(True)

    print("solved")
    colorize_map(True)


def preprocess():
    MAP.initial_preprocessing()
    for vertex in range(len(MAP.nodes)):
        GRAPH[vertex], COLORED_STATES[vertex] = set(), None
    for v in MAP.nodes:
        for adj in v.adj:
            GRAPH[v.id].add(adj)
            GRAPH[adj].add(v.id)


def assign_boolean_value(argument):
    if argument == "-t":
        return True
    elif argument == "-f":
        return False
    else:
        return None


if __name__ == "__main__":
    try:
        MAP_IMAGE_PATH = sys.argv[1]
        FILTERING_MODE = sys.argv[2]
        is_ii_mode = FILTERING_MODE == "-ii"
        if not is_ii_mode:
            USE_VARIABLE_ORDERING = assign_boolean_value(sys.argv[3])
            USE_VALUE_ORDERING = assign_boolean_value(sys.argv[4])
            if USE_VARIABLE_ORDERING == None or USE_VALUE_ORDERING == None:
                print("invalid ordering flags")
                exit(1)
    except IndexError:
        print("Error: invalid arguments.")
        exit(1)

    try:
        MAP = Map(cv2.imread(MAP_IMAGE_PATH, cv2.IMREAD_COLOR))
    except Exception as e:
        print("Could not read the specified image")
        exit(1)

    preprocess()
    domains = [list(range(N_COLORS)) for _ in range(len(GRAPH.keys()))]
    if not is_ii_mode:
        print(
            f"filtering mode: {FILTERING_MODE}, use variable ordering: {USE_VARIABLE_ORDERING}, use value ordering: {USE_VALUE_ORDERING}")
        backtrack_solve(domains)
    else:
        iterative_improvement_solve(domains)
