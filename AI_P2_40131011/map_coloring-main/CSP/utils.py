import random
from collections import defaultdict

def is_consistent(graph, variable_value_pairs):
    """
    Returns True if the variables that have been assigned a value so far are consistent with the constraints,
    and False otherwise.

    variable_value_pairs can be used to access any value of any variable from the variable as a key.
    You can use variable_value_pairs.items() to traverse it as (state, color) pairs,
                variable_value_pairs.keys() to get all the variables,
            and variable_value_pairs.values() to get all the values.
    """
    for variable, value in variable_value_pairs.items():
        if value != None:
            for adjacent_variable in graph[variable]:
                if variable_value_pairs[adjacent_variable] == value:
                    return False

    return True



def is_solved(graph: dict, variable_value_pairs):
    """
    Returns True if the CSP is solved, and False otherwise.
    """
    if any(value is None for value in variable_value_pairs.values()):
        return False

    for n, value in variable_value_pairs.items():
        if value is not None:
            for adj in graph[n]:
                if variable_value_pairs[adj] == value:
                    return False

    return True


def get_next_variable(variable_value_pairs, domains):
    """
    Returns the index of the next variable from the default order of the unassigned variables.
    """
    for var in variable_value_pairs.keys():
        if variable_value_pairs[var] is None:
            return var


def get_chosen_variable(graph, variable_value_pairs, domains):
    """
    Returns the next variable that is deemed the best choice by the proper heuristic,
    using a second heuristic for breaking ties from the first heuristic.
    """
    best_var = (None, float('inf'), 0)

    for var in variable_value_pairs.keys():
        if variable_value_pairs[var] is None:
            domain_size = len(domains[var])
            degree = len(graph[var])

            if domain_size < best_var[1]:
                best_var = (var, domain_size, degree)
            elif domain_size == best_var[1]:
                if degree > best_var[2]:
                    best_var = (var, domain_size, degree)

    return best_var[0]


def get_ordered_domain(graph, domains, variable):
    """
    Returns the domain of the variable after ordering its values by the proper heuristic.
    """
    ord_domain = []
    count = 0
    for value in domains[variable]:
        count = 0
        for adj_var in graph[variable]:
            if value in domains[adj_var]:
                count += 1
        ord_domain.append((value, count))

    sorted(ord_domain, key=lambda n: n[1])
    res = []
    for i in ord_domain:
        res.append(i[0])
    return res



def forward_check(graph, variable_value_pairs, domains: list, variable, value):
    """
    Removes the value assigned to the current variable from its neighbors
    and returns True if backtracking is necessary, and False otherwise.
    """
    for adj in graph[variable]:
        if value in domains[adj]:
            domains[adj].remove(value)
            if not domains[adj]:
                return True

    return False




def revise(domains, v, t):
    """
    Attempts to revise the domain of variable t based on the assignment of variable v.
    Returns True if the domain of t is revised, and False otherwise.
    """
    revised = False
    values_to_remove = []

    for value in domains[t]:
        if value in domains[v] and len(domains[v]) == 1:
            values_to_remove.append(value)
            revised = True

    for value in values_to_remove:
        domains[t].remove(value)

    return revised



def ac3(graph, variable_value_pairs, domains):
    """
    Maintains arc-consistency and returns True if backtracking is necessary, and False otherwise.
    """
    queue = [(v, t) for v in graph.keys() for t in graph[v]]

    while queue:
        v, t = queue.pop()

        if revise(domains, v, t):
            if not domains[t]:
                return True

            queue.extend((t, i) for i in domains[t] if i!= v)

    return False



def random_choose_conflicted_var(graph, variable_value_pairs):
    """
    Returns a random variable that is conflicting with a constraint.
    """
    conflicting_vars = []

    for var in variable_value_pairs:
        for adj in graph[var]:
            if variable_value_pairs[var] == variable_value_pairs[adj]:
                conflicting_vars.append(var)
                break

    return random.choice(conflicting_vars)



def get_chosen_value(graph, variable_value_pairs, domains, variable):
    """
    Returns the value by using the proper heuristic, handling tie-breaking by random.
    """
    best_value = (None, float('inf'))

    for val in domains[variable]:
        constraint_count = sum(val == variable_value_pairs[adj] for adj in graph[variable])

        if constraint_count < best_value[1]:
            best_value = (val, constraint_count)
        elif constraint_count == best_value[1]:
            if random.random() < 0.5:  # Randomly choose between 0 and 1
                best_value = (val, constraint_count)

    return best_value[0]
