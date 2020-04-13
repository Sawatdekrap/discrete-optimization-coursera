#!/usr/bin/python
# -*- coding: utf-8 -*-

from knapsack import solve_knapsack, Item


def get_inputs(input_data):
    lines = input_data.split('\n')
    item_count, capacity = lines[0].split(' ')
    items = []
    for ix, line in enumerate(lines[1:]):
        if not line:
            continue
        value, weight = line.split(' ')
        items.append(Item(ix, int(value), int(weight)))

    return int(item_count), int(capacity), items


def get_outputs(objective_function, is_optimal, x):
    return (
        "{} {}\n"
        "{}"
    ).format(objective_function, 1 if is_optimal else 0, ' '.join(['1' if i else '0' for i in x]))


def solve_it(input_data):
    item_count, capacity, items = get_inputs(input_data)

    # TODO solve
    obj, taken = solve_knapsack(capacity, items, inc=1)

    return get_outputs(obj, True, taken)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

