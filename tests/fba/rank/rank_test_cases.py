import networkx as nx

graphs = []
noderank_dicts = []

# 0
graph0 = nx.DiGraph()
graph0.add_nodes_from(range(6))
graph0.add_edges_from([(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (5, 2)])
graphs.append(graph0)
noderank_dicts.append({4: 1, 2: 1, 3: 0, 5: 1, 1: 1, 0: 1})

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(7))
graph1.add_edges_from([(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)])
graphs.append(graph1)
noderank_dicts.append({3: 0, 2: 1, 1: 2, 6: 0, 5: 1, 4: 2, 0: 3})

# 2
graph2 = nx.DiGraph()
graph2.add_nodes_from(range(4))
graph2.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
graphs.append(graph2)
noderank_dicts.append(dict((node, float("-inf")) for node in range(4)))

# 3
graph3 = nx.DiGraph()
graph3.add_nodes_from(range(4))
graph3.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 0)])
graphs.append(graph3)
noderank_dicts.append(dict((node, float("-inf")) for node in range(4)))

# 4
graph4 = nx.DiGraph()
graph4.add_nodes_from(range(6))
graph4.add_edges_from(
    [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 5), (5, 3), (5, 2)]
)
graphs.append(graph4)
noderank_dicts.append(dict((node, float("-inf")) for node in range(6)))

# 5
graph5 = nx.DiGraph()
graph5.add_nodes_from(range(8))
graph5.add_edges_from(
    [(0, 1), (1, 2), (2, 0), (3, 0), (3, 4), (4, 5), (5, 0), (3, 6), (6, 7)]
)
graphs.append(graph5)
noderank_dicts.append(
    {
        0: float("-inf"),
        1: float("-inf"),
        2: float("-inf"),
        5: float("-inf"),
        4: float("-inf"),
        7: 0,
        6: 1,
        3: 2,
    }
)

# 6
graph6 = nx.DiGraph()
graph6.add_nodes_from(range(8))
node_map = dict((t, 7 - t) for t in range(8))
graph6.add_edges_from(
    (node_map[src], node_map[dst]) for src, dst in graph5.edges
)
graphs.append(graph6)
noderank_dicts.append(
    dict((node_map[node], noderank_dicts[-1][node]) for node in range(8))
)

# 7
graph7 = nx.DiGraph()
graph7.add_nodes_from(range(7))
graph7.add_edges_from(
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (5, 6)]
)
graphs.append(graph7)
noderank_dicts.append(
    {
        6: 0,
        5: 1,
        0: 2,
        1: 2,
        2: 2,
        3: 2,
        4: 2,
    }
)

graph8 = nx.DiGraph()
graph8.add_nodes_from(range(5))
graph8.add_edges_from(
    [(0,1), (0,4), (1,2), (2,3), (3,0)]
)
graphs.append(graph8)
noderank_dicts.append(
    {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 0
    }
)

graph9 = nx.DiGraph()
graph9.add_nodes_from(range(5))
graph9.add_edges_from(
    [(0,1), (0,4), (1,2), (2,3), (3,0), (2,4)]
)
graphs.append(graph9)
noderank_dicts.append(
    {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 0
    }
)
