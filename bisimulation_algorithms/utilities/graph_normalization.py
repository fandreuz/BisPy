import networkx as nx
from typing import Dict, Tuple, Any, List


def convert_to_integer_graph(
    graph: nx.Graph,
) -> Tuple[nx.Graph, Dict[Any, int]]:
    """Convert the given graph to an isomorphic graph whose nodes are integer
    numbers. Moreover, creates a Dict which maps nodes of the original graph to
     the corresponding node of the integer graph. Nodes in the graph have be
     hashable objects.

    Args:
        graph (nx.Graph): The input graph.

    Returns:
        Tuple[nx.Graph, Dict[Any, int]]: A tuple containing the integer graph
        and the mapping Dict.
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
    """Checks whether the nodes in the given graph form an integer interval
    starting from zero without holes.

    Args:
        graph (nx.Graph): The input graph.

    Returns:
        bool: True if the graph satisfies the "normal integrality" property.
    """

    return (
        all(map(lambda node: isinstance(node, int) and node >= 0, graph.nodes))
        and max(graph.nodes) == len(graph.nodes) - 1
    )


def back_to_original(
    partition: List[Tuple[int]], node_to_idx: Tuple[nx.Graph, Dict[Any, int]]
) -> List[Tuple[Any]]:
    """Convert the given integer partition to a partition made by the original
    elements of the graph, using the mapping node_to_idx.

    Args:
        partition (List[Tuple[int]]): The input partition.
        node_to_idx (Tuple[nx.Graph, Dict[Any, int]]): The mapping node->idx
        returned by convert_to_integer_graph.

    Returns:
        List[Tuple[Any]]: The given partition, represented with the symbols
        (nodes) of the original graph.
    """

    # create a mapping from idx to the original nodes
    idx_to_node = sorted(node_to_idx, key=lambda node: node_to_idx[node])

    # compute the RSCP of the original graph
    return [tuple(idx_to_node[idx] for idx in block) for block in partition]
