import networkx as nx

# 1
graph = nx.balanced_tree(2, 3, create_using=nx.DiGraph)
initial_edges = [(1, 0), (4, 0)]
correct_results = (
    [(3, 4, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,)],
    [(3, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,), (4,)],
)

ins_n_outs = [(graph, initial_edges, correct_results)]
