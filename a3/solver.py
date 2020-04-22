#!/usr/bin/python
# -*- coding: utf-8 -*-

from graph import Graph


def format_output(solution, is_optimal):
    s = (
        f"{max(solution)+1} {1 if is_optimal else 0}\n"
        f"{' '.join([str(c) for c in solution])}"
    )
    return s


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    graph = Graph(n_nodes=node_count, edges=edges)
    solution, is_optimal = graph.solve(timeout=5*60)

    return format_output(solution, is_optimal)


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

