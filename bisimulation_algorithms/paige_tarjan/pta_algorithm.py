import networkx as nx
from typing import List, Dict, Any, Tuple, Iterable

from .graph_decorator import initialize
from .pta import pta


def convert_to_integer_graph(
    graph: nx.Graph,
) -> Tuple[nx.Graph, Dict[Any, int]]:
    """Convert the given graph to an isomorphic graph whose nodes are integer
    numbers. Moreover, creates a Dict which maps nodes of the original graph to
     the corresponding node of the integer graph.

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


def rscp(
    graph: nx.Graph,
    initial_partition: Iterable[Iterable[int]] = None,
    is_integer_graph: bool = False,
) -> List[Tuple]:
    """Compute the RSCP of the given graph, with the given initial partition.
    This function needs to work with an integer graph (nodes represented by an
    integer), therefore it checks this property before starting the
    Paige-Tarjan algorithm, and creates an integer graph if it is not
    statisfied.

    Args:
        graph (nx.Graph): The input graph.
        initial_partition (Iterable[Iterable[int]], optional): The initial
        partition for the given graph. Defaults to None.
        is_integer_graph (bool, optional): If True, the function assumes that
        the graph is integer, and skips the integrality check (may be useful
        when performance is important). Defaults to False.

    Returns:
        List[Tuple]: The RSCP of the given (even non-integer) graph, with the
        given initial partition.
    """

    # if True, the input graph is already an integer graph
    original_graph_is_integer = is_integer_graph or check_normal_integer_graph(
        graph
    )

    # if initial_partition is None, then it's the trivial partition
    if initial_partition is None:
        # only list(graph.nodes) isn't OK
        initial_partition = [list(graph.nodes)]

    if not original_graph_is_integer:
        # convert the graph to an "integer" graph
        integer_graph, node_to_idx = convert_to_integer_graph(graph)

        # convert the initial partition to a integer partition
        integer_initial_partition = [
            [node_to_idx[old_node] for old_node in block]
            for block in initial_partition
        ]
    else:
        integer_graph = graph
        integer_initial_partition = initial_partition

    # compute the RSCP
    (q_partition, _) = initialize(integer_graph, integer_initial_partition)
    rscp = pta(q_partition)

    if original_graph_is_integer:
        return rscp
    else:
        # create a mapping from idx to the original nodes
        idx_to_node = sorted(node_to_idx, key=lambda node: node_to_idx[node])

        # compute the RSCP of the original graph
        return [tuple(idx_to_node[idx] for idx in block) for block in rscp]
