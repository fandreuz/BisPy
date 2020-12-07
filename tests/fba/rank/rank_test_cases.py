import networkx as nx

graphs = []

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(6))
graph1.add_edges_from([(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (5, 2)])
graphs.append(graph1)

# 2 : tree
graph2 = nx.DiGraph()
graph2.add_nodes_from(range(7))
graph2.add_edges_from([(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)])
graphs.append(graph2)

# 3: cycle
graph3 = nx.DiGraph()
graph3.add_nodes_from(range(4))
graph3.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
graphs.append(graph3)

graphs_noderankdict = []

# 1
graphs_noderankdict.append((graph1, {4: 1, 2: 1, 3: 0, 5: 1, 1: 1, 0: 1}))

# 2 : tree
graphs_noderankdict.append((graph2, {3: 0, 2: 1, 1:2, 6: 0, 5: 1, 4: 2, 0: 3}))

# 3: cycle
graphs_noderankdict.append((graph3, {
    0: float('-inf'),
    1: float('-inf'),
    2: float('-inf'),
    3: float('-inf')
}))
