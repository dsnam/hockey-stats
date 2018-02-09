"""
Determines if a team can still win the President's Trophy.

The idea is to construct a graph with a source node that connects to g game nodes, with game node i,j representing
games between teams i and j. The capacity of the edge to node i,j is the number of points up for grabs in the remaining
games. Every game node i,j connects to two team nodes i and j. These edges have infinite capacity. Finally, the
team nodes connect to the sink node and have capacity w_k + r_k - w_j, where w_k is the current points total for the
team in question, r_k is the remaining possible points for the team to win, and w_j is the number of points that
opponent j has already won.
"""

import networkx as nx
from networkx.algorithms.flow import edmonds_karp
from nhl_api import NHL

def can_win_league(team):
    """
    :param team: tuple of (id, 'Team Name')
    :return: True if the team can still win the league, false otherwise
    """
    G = nx.DiGraph()

    nhl = NHL()

    standings = nhl.get_points_gp()
    games = nhl.get_remaining_games_against()
    teams = nhl.get_teams_list()

    for t in teams:
        w_k = standings[team]['pts']
        r_k = (82-standings[team]['gp'])*2
        w_j = standings[t]['pts']
        if t != team:
            G.add_edge(t,'t', capacity=w_k + r_k - w_j)
        else:
            G.add_edge(t,'t', capacity=0)


    for t, remaining in games.items():
        #print(t, remaining)
        for opponent,rem_games in remaining.items():
            #print(t, opponent)
            if (t, opponent) not in G and (opponent, t) not in G:
                G.add_edge('s', (t, opponent), capacity=rem_games*2)
                G.add_edge((t, opponent), t, capacity=float('inf'))
                G.add_edge((t, opponent), opponent, capacity=float('inf'))

    print(G.edges(data=True))

    S = 0
    for e in G.edges(data=True):
        if e[0] == 's':
            S += e[2]['capacity']

    R = edmonds_karp(G, 's', 't')
    flow = R.graph['flow_value']

    return flow == S

