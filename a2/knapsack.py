from collections import namedtuple, deque
from array import array


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


def print_array(a):
    for line in a:
        for x in line:
            print('{:3} '.format(x), end='')
        print()
