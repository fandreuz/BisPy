import networkx as nx
from typing import Dict, Tuple, Any, List


def convert_to_integer_graph(
    graph: nx.Graph,
) -> Tuple[nx.Graph, Dict[Any, int]]:
    """Convert the given graph to an isomorphic integer graph.

    :param graph: The input graph.
    :returns: A tuple whose items are:

        0. The integer ismorphic graph;
        1. A `dict` which may be used to recover the original graph.
    """

    integer_graph = nx.DiGraph()

    # add new integer nodes
    integer_graph.add_nodes_from(range(len(graph.nodes)))

    # map old nodes to integer nodes
    node_to_idx = {old_node: idx for idx, old_node in enumerate(graph.nodes)}

    # add integer edges
    integer_graph.add_edges_from(
        (node_to_idx[edge[0]], node_to_idx[edge[1]]) for edge in graph.edges
    )

    return integer_graph, node_to_idx


def check_normal_integer_graph(graph: nx.Graph) -> bool:
    """Check whether the given graph is integer.

    :param graph: The input graph.
    """

    return (
        all(map(lambda node: isinstance(node, int) and node >= 0, graph.nodes))
        and max(graph.nodes) == len(graph.nodes) - 1
    )


def back_to_original(
    partition: List[Tuple[int]], node_to_idx: Tuple[nx.Graph, Dict[Any, int]]
) -> List[Tuple[Any]]:
    """Convert the given partition of the nodes of an integer graph to the
    representation which uses nodes from the original graph using the mapping
    returned by :func:`convert_to_integer_graph`.

    :param partition: The partition of the set of nodes of an integer graph.
    :param node_to_idx: The mapping returned by
        :func:`convert_to_integer_graph`.
    """

    # create a mapping from idx to the original nodes
    idx_to_node = sorted(node_to_idx, key=lambda node: node_to_idx[node])

    # compute the RSCP of the original graph
    return [tuple(idx_to_node[idx] for idx in block) for block in partition]
