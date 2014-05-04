"""Utilities and search functions.  Adapted from AIMA libraries."""

import sys


def update(x, **entries):
    """Update a dict; or an object with slots; according to entries.
    >>> update({'a': 1}, a=10, b=20)
    {'a': 10, 'b': 20}
    >>> update(Struct(a=1), a=10, b=20)
    Struct(a=10, b=20)
    """
    if isinstance(x, dict):
        x.update(entries)
    else:
        x.__dict__.update(entries)
    return x


class Queue:
    """Queue is an abstract class/interface. There are three types:
        Stack(): A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(order, f): Queue in sorted order (default min-first).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
        item in q       -- does q contain item?
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def __init__(self):
        abstract

    def extend(self, items):
        for item in items: self.append(item)

def Stack():
    """Return an empty list, suitable as a Last-In-First-Out Queue."""
    return []

class FIFOQueue(Queue):
    """A First-In-First-Out Queue."""
    def __init__(self):
        self.A = []; self.start = 0
    def append(self, item):
        self.A.append(item)
    def __len__(self):
        return len(self.A) - self.start
    def extend(self, items):
        self.A.extend(items)
    def pop(self):
        e = self.A[self.start]
        self.start += 1
        if self.start > 5 and self.start > len(self.A)/2:
            self.A = self.A[self.start:]
            self.start = 0
        return e
    def __contains__(self, item):
        return item in self.A[self.start:]


class Problem(object):
    """The abstract class for a formal problem.  You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial; self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        abstract

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        abstract

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Override this
        method if checking against a single self.goal is not enough."""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract
#______________________________________________________________________________

class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        "Create a search tree Node, derived from a parent by an action."
        update(self, state=state, parent=parent, action=action,
               path_cost=path_cost, depth=0)
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node %s>" % (self.state,)

    def expand(self, problem):
        "List the nodes reachable in one step from this node."
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        "Fig. 3.10"
        next = problem.result(self.state, action)
        return Node(next, self, action,
                    problem.path_cost(self.path_cost, self.state, action, next))

    def solution(self):
        "Return the sequence of actions to go from the root to this node."
        return [node.action for node in self.path()[1:]]

    def path(self):
        "Return a list of nodes forming the path from the root to this node."
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

#______________________________________________________________________________
# Uninformed Search algorithms

def tree_search(problem, frontier):
    """Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Don't worry about repeated paths to a state. [Fig. 3.7]"""
    
    frontier.append(Node(problem.initial))
    maxfrontier = 1
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return maxfrontier
        frontier.extend(node.expand(problem))

        #added code
        maxftmp = len(frontier)
        if(maxftmp > maxfrontier):
            maxfrontier = maxftmp
            
    return maxfrontier

def breadth_first_tree_search(problem):
    "Search the shallowest nodes in the search tree first."
    return tree_search(problem, FIFOQueue())

def depth_first_tree_search(problem):
    "Search the deepest nodes in the search tree first."
    return tree_search(problem, Stack())

def depth_limited_search(problem, limit=50):
    "[Fig. 3.17]"
    def recursive_dls(node, problem, limit):
        if problem.goal_test(node.state):
            #added code
            return node.depth
        elif node.depth == limit:
            return 'cutoff'
        else:
            cutoff_occurred = False
            for child in node.expand(problem):
                result = recursive_dls(child, problem, limit)
                if result == 'cutoff':
                    cutoff_occurred = True
                elif result is not None:
                    return result
            #added code
            return 'cutoff' if cutoff_occurred else node.depth

    # Body of depth_limited_search:
    return recursive_dls(Node(problem.initial), problem, limit)

def iterative_deepening_search(problem):
    "[Fig. 3.18]"
    for depth in xrange(sys.maxint):
        result = depth_limited_search(problem, depth)
        if result != 'cutoff':
            return result
