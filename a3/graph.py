from collections import namedtuple, OrderedDict


Step = namedtuple('Step', ['choices', 'domain'])


class ConstraintError(Exception):
    pass


class Graph:
    def __init__(self, n_nodes, edges):
        self.nodes = [i for i in range(n_nodes)]
        self.edges = {n: set() for n in self.nodes}
        for x, y in edges:
            self.edges[x].add(y)
            self.edges[y].add(x)

    @staticmethod
    def _domain_infeasible(domain):
        return not any([len(domain[n]) == 0 for n in domain])

    def _update_domain(self, node, choice, domain, lower_bound):
        """Update a given domain if a node chooses a value"""
        # Copy domain, removing values that are not under lower_bound
        # TODO only calc on lower_bound update to speed up
        lower_bound_set = set([i for i in range(lower_bound-1)])
        new_domain = {n: domain[n] & lower_bound_set for n in domain}
        if not self._domain_infeasible(new_domain):
            raise ConstraintError

        # Set node to only be allowed to be choice
        new_domain[node].clear()
        new_domain[node].add(choice)

        # Propogate changes to neighbouring nodes
        stack = [(node, choice)]
        while stack:
            n, c = stack.pop()
            for neighbour in self.edges[n]:
                if c in new_domain[neighbour]:
                    new_domain[neighbour].remove(c)
                    # If the neighbour can only be one value now, update new_domain
                    # from there as well
                    if len(new_domain[neighbour]) == 1:
                        stack.append((neighbour, next(iter(new_domain[neighbour]))))

        if not self._domain_infeasible(new_domain):
            raise ConstraintError
    
        return new_domain

    @staticmethod
    def _get_required_set(domain):
        s = set()
        for node_domain in domain.values():
            if len(node_domain) == 1:
                s.add(next(iter(node_domain)))
        return s

    def _get_solution(self, domain):
        for node_domain in domain.values():
            assert len(node_domain) == 1
        return [next(iter(domain[n])) for n in self.nodes]

    def solve(self, lower_bound=None):
        sorted_nodes = sorted(self.nodes, key=lambda n: -len(self.edges[n]))
        update_count = [0 for _ in sorted_nodes]
        if lower_bound is None:
            lower_bound = len(self.nodes)
            best_solution = [n for n in self.nodes]
        else:
            best_solution = None

        initial_choices = [0]
        initial_domain = {n: set([i for i in range(lower_bound)]) for n in self.nodes}
        stack = [Step(choices=initial_choices, domain=initial_domain)]
        while stack:
            # DEBUG
            update_count[len(stack)-1] += 1

            # Pick a valid choice
            step = stack[-1]
            choice = lower_bound
            while step.choices and choice >= lower_bound:
                choice = step.choices.pop()
            is_feasible = choice < lower_bound
            
            # If found a valid choice, update domain with this choice
            if is_feasible:
                try:
                    new_domain = self._update_domain(
                        node=sorted_nodes[len(stack)-1],
                        choice=choice,
                        domain=step.domain,
                        lower_bound=lower_bound
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
                lower_bound = len(set(best_solution))

                stack.pop()
                while stack and len(stack[-1].choices) == 0:
                    stack.pop()
                print(lower_bound)
                continue

            # Feasible non-leaf - append new choice possibilities to stack
            allowed_choices = self._get_required_set(new_domain)  # Choices that already exist in the graph
            allowed_choices.add(max(allowed_choices)+1)  # A new color is allowed for next node
            next_node = sorted_nodes[len(stack)]
            new_choices = list(allowed_choices & new_domain[next_node])  # node can only pick from domain
            new_choices.sort(key=lambda x: -x)  # Pick smallest colors first
            stack.append(Step(new_choices, new_domain))

        print(update_count)
        return best_solution
