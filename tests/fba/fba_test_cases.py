from bispy.utilities.graph_entities import (
    _QBlock as _Block,
    _Vertex,
)
import networkx as nx

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(4))
graph1.add_edges_from([(0, 1), (1, 1), (2, 3), (3, 1)])

# 2
graph2 = nx.DiGraph()
graph2.add_nodes_from(range(4))
graph2.add_edges_from([(0, 1), (0, 2), (0, 3), (3, 2), (2, 2)])

graphs = [
    graph1,
    graph2,
    nx.complete_graph(10).to_directed(),
    nx.star_graph(10).to_directed(),
    nx.empty_graph(20).to_directed(),
    nx.cycle_graph(10).to_directed(),
]

# block counterimage
block_counterimaged_block = []

block_counterimaged_block.append([1])

block_counterimaged_block.append([1, 2])

# FBA correctness
# 0
fba_correctness_graphs = []

graph0 = nx.DiGraph()
graph0.add_nodes_from(range(8))
graph0.add_edges_from(
    [(0, 1), (1, 2), (2, 0), (3, 0), (3, 4), (4, 5), (5, 0), (3, 6), (6, 7)]
)
fba_correctness_graphs.append(graph0)

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(8))
node_map = dict((t, 7 - t) for t in range(8))
graph1.add_edges_from(
    (node_map[src], node_map[dst]) for src, dst in graph0.edges
)
fba_correctness_graphs.append(graph1)

# 2
graph2 = nx.DiGraph()
graph2.add_nodes_from(range(7))
graph2.add_edges_from(
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (5, 6)]
)
fba_correctness_graphs.append(graph2)
