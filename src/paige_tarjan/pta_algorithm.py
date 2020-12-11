import networkx as nx
import paige_tarjan.graph_decorator as decorator
import paige_tarjan.pta as pta
from typing import List


def rscp(graph: nx.Graph, initial_partition: List[List[int]] = None):
    if initial_partition == None:
        # the partition must be a list of lists
        initial_partition = [list(range(len(graph.nodes)))]
    (q_partition, _) = decorator.initialize(graph, initial_partition)
    rscp = pta.pta(q_partition)
    return [tuple(sorted(tp)) for tp in rscp]
