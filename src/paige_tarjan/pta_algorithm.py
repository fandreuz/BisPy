import networkx as nx
import paige_tarjan.graph_decorator as decorator
import paige_tarjan.pta as pta
from typing import List, Dict, Any, Set, Tuple


def convert_to_integer_graph(graph: nx.Graph) -> (nx.Graph, Dict[Any, int]):
    integer_graph = nx.DiGraph()

    # add new integer nodes
    integer_graph.add_nodes_from(range(len(graph.nodes)))

    # map old nodes to integer nodes
    node_to_idx = {old_node: idx for idx, old_node in enumerate(graph.nodes)}

    # add integer edges
    integer_graph.add_edges_from(
        [(node_to_idx[edge[0]], node_to_idx[edge[1]]) for edge in graph.edges]
    )

    return integer_graph, node_to_idx


def convert_to_integer_partition(
    partition: List[List[Any]], node_to_idx: Dict[Any, int]
) -> List[List[int]]:
    return [[node_to_idx[old_node] for old_node in block] for block in partition]


def rscp(graph: nx.Graph, initial_partition: List[List[int]] = None) -> Set[Tuple]:
    # convert the graph to an "integer" graph
    integer_graph, node_to_idx = convert_to_integer_graph(graph)

    # if initial_partition is None, then it's the trivial partition
    if initial_partition == None:
        initial_partition = [list(graph.nodes)]
    # convert the initial partition to a integer partition
    integer_initial_partition = convert_to_integer_partition(
        initial_partition, node_to_idx
    )

    # compute the RSCP
    (q_partition, _) = decorator.initialize(integer_graph, integer_initial_partition)
    rscp = pta.pta(q_partition)
    sorted_rscp = [sorted(tp) for tp in rscp]

    # create a mapping from idx to the original nodes
    idx_to_node = sorted(node_to_idx, key=lambda node: node_to_idx[node])

    # compute the RSCP of the original graph
    return set([tuple([idx_to_node[idx] for idx in block]) for block in sorted_rscp])
