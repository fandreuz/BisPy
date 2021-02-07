import networkx as nx

# new scc
new_scc_graphs = []
new_scc_new_edge = []
new_scc_correct_value = []

# 0
g0 = nx.DiGraph()
g0.add_nodes_from(range(5))
g0.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
new_scc_graphs.append(g0)

new_scc_new_edge.append((2,0))
new_scc_correct_value.append(True)

# 1
g1 = nx.DiGraph()
g1.add_nodes_from(range(8))
g1.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
new_scc_graphs.append(g1)

new_scc_new_edge.append((3, 4))
new_scc_correct_value.append(False)

# 2
g2 = nx.DiGraph()
g2.add_nodes_from(range(5))
g2.add_edges_from([(0, 1), (1, 2), (2, 3), (3,4)])
new_scc_graphs.append(g2)

new_scc_new_edge.append((0, 4))
new_scc_correct_value.append(False)
