from collections import namedtuple, deque
from array import array
from itertools import zip_longest


Item = namedtuple("Item", ['index', 'value', 'weight'])


def solve_knapsack(capacity, items, inc=1):
    """Solve knapsack problem and return objective function and array of taken items"""
    
    # Initialize DP array
    n_items = len(items)
    n_k = capacity // inc
    print("{} {}".format(n_k, n_items))
    #a = [[0] * (n_items+1) for _ in range(n_k+1)]  # Leave room for empty items and 0 capacity
    a = [array('I', [0] * (n_items+1)) for _ in range(n_k+1)]

    # Fill array
    for k in range(1, n_k+1):
        for i, item in enumerate(items, start=1):
            if item.weight > k:
                a[k][i] = a[k][i-1]
            else:
                a[k][i] = max(a[k][i-1], a[k-item.weight][i-1] + item.value)

    # print_array(a)

    # Find optimal path (i and k are pointing to the optimal objective)
    obj = a[k][i]
    taken = deque()
    while i > 0:
        did_take = a[k][i] != a[k][i-1]
        taken.appendleft(did_take)
        if did_take:
            k -= items[i-1].weight
        i -= 1
    
    # Obj, x
    return obj, taken


def solve_branch_and_bound(capacity, items: list):
    n_items = len(items)
    value_density = lambda i: i.value / i.weight
    sorted_items = sorted(items, key=value_density, reverse=True)
    stack = [True]
    current_best = 0
    current_best_path = None

    def get_upper_bound():
        c = v = 0
        for i, select in zip_longest(sorted_items, stack, fillvalue=None):
            if select is False:
                continue
            if c + i.weight > capacity:
                v += (capacity - c) * i.value / i.weight
                break
            c += i.weight
            v += i.value
        
        return v
    
    def is_feasible():
        return sum([i.weight for i, select in zip(sorted_items, stack) if select]) <= capacity
    
    def get_leaf_value():
        return sum([i.value for i, select in zip(sorted_items, stack) if select])
    
    def prune():
        while stack and stack[-1] == False:
            stack.pop()
        if stack:
            stack[-1] = False

    while len(stack) > 0:
        # Check current node is feasible
        if not is_feasible():
            prune()
            continue

        # Get upper bound, prune if worse than current best
        upper_bound = get_upper_bound()
        if upper_bound < current_best:
            prune()
            continue

        # If not leaf, go to next
        if len(stack) != n_items:
            stack.append(True)
            continue

        # If leaf, set current_best if best and go to next
        value = get_leaf_value()
        if value > current_best:
            current_best = value
            current_best_path = stack.copy()
        prune()
        # print("Current Best: {}, Stack: {}".format(current_best, current_best_path))

    best_items = [0] * n_items
    for selected, item in zip(current_best_path, sorted_items):
        best_items[item.index] = selected
    return current_best, best_items

    
def print_array(a):
    for line in a:
        for x in line:
            print('{:3} '.format(x), end='')
        print()
