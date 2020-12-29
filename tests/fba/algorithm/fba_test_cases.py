from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Block,
    _Vertex,
)
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    prepare_graph,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    create_initial_partition,
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
