from collections import namedtuple


Step = namedtuple('Step', ['choices', 'domain'])


class Graph:
    def __init__(self, n_nodes, edges):
        self.nodes = [i for i in range(n_nodes)]
        self.edges = {n: set() for n in self.nodes}
        for x, y in edges:
            self.edges[x].add(y)
            self.edges[y].add(x)

    def _update_domain(self, node, choice, domain):
        """Update a given domain if a node chooses a value"""
        domain[node].clear()
        domain[node].add(choice)

        # Propogate changes to neighbouring nodes
        stack = [(node, choice)]
        while stack:
            n, c = stack.pop()
            for neighbour in self.edges[n]:
                if c in domain[neighbour]:
                    domain[neighbour].remove(c)
                    # If the neighbour can only be one value now, update domain
                    # from there as well
                    if len(domain[neighbour]) == 1:
                        stack.append((neighbour, domain[neighbour][0]))

    def _get_required_set(self, domain):
        s = set()
        for node_domain in domain.values():
            if len(node_domain) == 1:
                s.add(next(iter(node_domain)))
        return s

    def _domain_is_feasible(self, domain, lower_bound):
        """Return True/False describing the feasibility of this domain

        Infeasible if:
        - Any nodes have an empty domain
        - Best possible is greater than lower_bound
        """
        for node_domain in domain.values():
            if len(node_domain) == 0:
                return False
        
        if len(self._get_required_set(domain)) > lower_bound:
            return False
        
        return True

    def _get_solution(self, domain):
        for node_domain in domain.values():
            assert len(node_domain) == 1
        return [next(iter(domain[n])) for n in self.nodes]

    def solve(self):
        sorted_nodes = sorted(self.nodes, key=lambda n: -len(self.edges[n]))
        best_solution = None
        lower_bound = len(self.nodes)
        lower_bound_sum = sum(self.nodes)

        initial_choices = [0]
        initial_domain = {n: set([i for i in range(lower_bound)]) for n in self.nodes}
        stack = [Step(choices=initial_choices, domain=initial_domain)]
        while stack:
            step = stack[-1]
            choice = step.choices.pop()
            # DEBUG
            if choice > lower_bound:
                print('#', end='')
            new_domain = {n: step.domain[n].copy() for n in step.domain}
            self._update_domain(
                node=sorted_nodes[len(stack)-1],
                choice=choice,
                domain=new_domain,
            )

            is_leaf = len(stack) == len(self.nodes)
            if is_leaf:
                # If this leaf is the current best, replace existing best
                curr_solution = self._get_solution(domain=new_domain)
                curr_lowest = len(set(curr_solution))
                curr_lowest_sum = sum(curr_solution)
                if curr_lowest < lower_bound or (curr_lowest == lower_bound and curr_lowest_sum < lower_bound_sum):
                    print(lower_bound_sum)
                    best_solution = curr_solution
                    lower_bound = curr_lowest
                    lower_bound_sum = curr_lowest_sum

            # Append to stack
            if not is_leaf and self._domain_is_feasible(domain=new_domain, lower_bound=lower_bound):
                allowed_choices = self._get_required_set(new_domain)  # Choices that already exist in the graph
                allowed_choices.add(max(allowed_choices)+1)  # A new color
                allowed_choices = allowed_choices & set([i for i in range(lower_bound)])  # Make sure all choices are within lower bound
                next_node = sorted_nodes[len(stack)]
                new_choices = allowed_choices & new_domain[next_node].copy()
                stack.append(Step(new_choices, new_domain))

            # Backtrack if no choices
            while stack and len(stack[-1].choices) == 0:
                stack.pop()
            continue

        return best_solution
