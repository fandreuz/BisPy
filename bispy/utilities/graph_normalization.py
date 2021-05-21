import networkx as nx
from typing import Dict, Tuple, Any, List


def convert_to_integer_graph(graph: nx.Graph):
    """Convert the given graph to an isomorphic *integer graph*. Moreover,
    creates a Dict which maps nodes of the original graph to the corresponding
    node of the integer graph.

    Since we use a `dict` to store the mappings, nodes in the original graph
    must be hashable objects, moreover duplicates are not allowed.

    :param graph: The input graph. `graph.nodes` must be hashable.
    :type graph: `networkx.DiGraph`
    :return: A tuple such that `tuple[0]` is the integer graph isomorphic to
        the the parameter `graph`, and `tuple[1]` is a `dict` which maps nodes
        from the old graph to nodes to the new graph.
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


def check_normal_integer_graph(graph):
    """Checks whether the given graph is an *integer graph*.

    :param graph: The graph to be checked.
    :type graph: `networkx.DiGraph`
    :return: `True` if `graph` is an *integer graph*, `False` otherwise.
    :rtype: bool
    """

    return (
        all(map(lambda node: isinstance(node, int) and node >= 0, graph.nodes))
        and max(graph.nodes) == len(graph.nodes) - 1
    )


def back_to_original(
    partition, node_to_idx:Dict[Any, int]
):
    """Convert the given integer partition to a partition made of the original
    elements of the graph, using the given mapping `node_to_idx`.

    :param partition: The input partition.
    :type partition: list(tuple(int))
    :param node_to_idx: The mapping (most likely given by
        :func:`convert_to_integer_graph`).
    :type node_to_idx: dict(Any,int)
    :return: The given partition, with each integer replaced by the
        corresponding node of the original graph.
    :rtype: list(tuple(Any))
    """

    # create a mapping from idx to the original nodes
    idx_to_node = sorted(node_to_idx, key=lambda node: node_to_idx[node])

    # compute the RSCP of the original graph
    return [tuple(idx_to_node[idx] for idx in block) for block in partition]
