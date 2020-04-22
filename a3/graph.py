from collections import namedtuple, OrderedDict
from functools import reduce
import time


Step = namedtuple('Step', ['node', 'choices', 'domain'])


class ConstraintError(Exception):
    pass


class Graph:
    def __init__(self, n_nodes, edges):
        self.nodes = {i for i in range(n_nodes)}
        self.edges = [[0] * n_nodes for _ in range(n_nodes)]
        for x, y in edges:
            self.edges[x][y] = 1
            self.edges[y][x] = 1
        self.neighbours = {n: [x for x in self.nodes if self.edges[n][x] == 1] for n in self.nodes}
        self.deg = {n: sum(self.edges[n]) for n in self.nodes}

    def _get_next_node(self, domain, selected):
        possible_nodes = self.nodes - selected
        sorted_nodes = sorted(possible_nodes, key=lambda n: sum(domain[n])*1000 + 999-self.deg[n])  # Break domain ties with highest deg first
        return sorted_nodes[0]

    def _domain_infeasible(self, domain):
        return not any([sum(domain[n]) == 0 for n in self.nodes])
    
    def _get_remaining_color(self, domain, node):
        sol = None
        for c in range(len(domain[node])):
            if domain[node][c] == 1:
                if sol is not None:
                    return None
                sol = c
        return sol


    def _update_domain(self, node, choice, domain, upper_bound):
        """Update a given domain if a node chooses a value"""
        # Copy domain, removing values that are not under upper_bound
        new_domain = [[domain[y][x] for x in range(upper_bound)] for y in range(len(self.nodes))]
        if not self._domain_infeasible(new_domain):
            raise ConstraintError

        # Set node to only be allowed to be choice
        for c in range(len(new_domain[node])):
            new_domain[node][c] = 0
        new_domain[node][choice] = 1

        # Propogate changes to neighbouring nodes
        stack = [(node, choice)]
        while stack:
            n, c = stack.pop()
            for neighbour in self.neighbours[n]:
                if new_domain[neighbour][c] == 1:
                    new_domain[neighbour][c] = 0
                    # If the neighbour can only be one value now, update new_domain
                    # from there as well
                    last_col = self._get_remaining_color(new_domain, neighbour)
                    if last_col is not None:
                        stack.append((neighbour, last_col))

        if not self._domain_infeasible(new_domain):
            raise ConstraintError
    
        return new_domain

    def _get_required_set(self, domain):
        s = set()
        for n in self.nodes:
            last_col = self._get_remaining_color(domain, n)
            if last_col is not None:
                s.add(last_col)
        return s

    def _get_solution(self, domain):
        # TODO add check?
        return [domain[n].index(1) for n in self.nodes]

    def _print_domain(self, domain, node):
        print(node)
        for l in domain:
            print(l)
        print()

    def solve(self, timeout=None):
        upper_bound = len(self.nodes)-1
        best_solution = [i for i in range(len(self.nodes))]
        optimal = True

        initial_choices = [0]
        initial_domain = [[1 for _i in range(upper_bound)] for _n in range(len(self.nodes))]
        inital_node = self._get_next_node(initial_domain, set())
        stack = [Step(node=inital_node, choices=initial_choices, domain=initial_domain)]
        start_time = time.time()
        while stack:
            # Check timeout
            if timeout is not None:
                if time.time() - start_time > timeout:
                    optimal = False
                    break
            # Pick a valid choice
            step = stack[-1]
            choice = upper_bound
            while step.choices and not choice < upper_bound:
                choice = step.choices.pop()
            is_feasible = choice < upper_bound
            
            # If found a valid choice, update domain with this choice
            if is_feasible:
                try:
                    new_domain = self._update_domain(
                        node=step.node,
                        choice=choice,
                        domain=step.domain,
                        upper_bound=upper_bound
                    )
                except ConstraintError:
                    is_feasible = False

            # Backtrack if no choices
            if not is_feasible:
                while stack and len(stack[-1].choices) == 0:
                    stack.pop()
                continue

            # Feasible leaf - update LB and solution, backtrack
            is_leaf = len(stack) == len(self.nodes)
            if is_leaf:
                # This is automatically the best solution - replace values
                best_solution = self._get_solution(domain=new_domain)
                upper_bound = len(set(best_solution))-1

                stack.pop()
                while stack and len(stack[-1].choices) == 0:
                    stack.pop()
                print(upper_bound)
                continue

            #self._print_domain(new_domain, step.node)

            # Feasible non-leaf - append new choice possibilities to stack
            allowed_choices = self._get_required_set(new_domain)  # Choices that already exist in the graph
            extra_color = max(allowed_choices)+1
            if extra_color < upper_bound:
                allowed_choices.add(extra_color)  # A new color is allowed for next node
            previous_nodes = [s.node for s in stack]
            next_node = self._get_next_node(new_domain, set(previous_nodes))
            try:
                new_choices = [c for c in allowed_choices if new_domain[next_node][c] == 1]
            except:
                print()
                print(allowed_choices)
                print(upper_bound)
                self._print_domain(new_domain, step.node)
                raise
            new_choices.sort(key=lambda x: -x)  # Pick smallest colors first (we pop stack)
            stack.append(Step(next_node, new_choices, new_domain))

        return best_solution, optimal
