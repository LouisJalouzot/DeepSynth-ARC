from program import *
from pcfg import *

from collections import deque 
from heapq import heappush, heappop, heappushpop

def bfs(G : PCFG, beam_width = 5000):
    '''
    A generator that enumerates all programs using a BFS.
    Assumes that the PCFG only generates programs of bounded depth.
    '''
    initial_non_terminals = deque()
    initial_non_terminals.append(G.start)
    
    frontier = [(None, initial_non_terminals)]

    while len(frontier) != 0 or len(new_frontier) != 0:
        new_frontier = []
        while True:
            try:
                partial_program, non_terminals = frontier.pop()
                if len(non_terminals) == 0: 
                    yield partial_program
                else:
                    S = non_terminals.pop()
                    for P in G.rules[S]:
                        args_P, _ = G.rules[S][P]
                        new_partial_program = (P, partial_program)
                        new_non_terminals = non_terminals.copy()
                        for arg in args_P:
                            new_non_terminals.append(arg)
                        if len(new_frontier) <= beam_width:
                            new_frontier.append((new_partial_program, new_non_terminals))
            except IndexError:
                frontier = new_frontier
                break