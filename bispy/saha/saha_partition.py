from bispy.saha.saha import saha as saha_algorithm
from bispy.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)
from bispy.utilities.graph_decorator import decorate_nx_graph, to_tuple_list
from bispy.paige_tarjan.paige_tarjan import paige_tarjan_qblocks
import networkx as nx
from typing import Union, List, Dict, Any, Tuple
from bispy.utilities.graph_entities import _QBlock, _Vertex


class SahaPartition:
    """
    A convenient class to recompute incrementally the maximum bisimulation
    using *Saha*'s algorithm. Create instances using :meth:`saha`.

    :param qblocks: The current partition of the nodes of the graph.
    :param qblocks: Nodes in the graph.
    :param node_to_idx: A `dict` which maps nodes from the original graph
        to nodes of the isomorphic integer graph (see
        :mod:`bispy.utilities.graph_normalization`).
    """

    def __init__(
        self,
        qblocks: List[_QBlock],
        vertexes: List[_QBlock],
        node_to_idx: Dict[Any, int],
    ):
        self.qblocks = qblocks
        self.vertexes = vertexes
        self.node_to_idx = node_to_idx

    def add_edge(
        self, edge: Tuple[Any, Any], verbose=True
    ) -> Union[None, List[Tuple[Any]]]:
        """Add a new edge to the graph, and recompute its maximum bisimulation
        incrementally.

        :param edge: The new edge (the first item is the source, the second
            item is the destination).
        :param verbose: If `True`, this methods returns the new maximum
            bisimulation after the addition of the new edge. Disabling this
            feature may increase performance (an additive factor
            :math:`\\Theta(|V|)` is saved). Defaults to True.
        :return: The maximim bisimulation after the addition of the new edge
            if `verbose` is `True`.
        """

        # if the original graph was not integer the user is going to expect
        # to be able to insert a new edge mentioning the original nodes
        if self.node_to_idx is not None:
            edge = (self.node_to_idx[edge[0]], self.node_to_idx[edge[1]])

        self.qblocks = saha_algorithm(self.qblocks, self.vertexes, edge)
        if verbose:
            max_bisi = to_tuple_list(self.qblocks)
            if self.node_to_idx is None:
                return max_bisi
            else:
                return back_to_original(max_bisi, self.node_to_idx)


def saha(graph, initial_partition=None, is_integer_graph=False) -> SahaPartition:
    """
    Returns an instance of the class :class:`SahaPartition` which can be used
    to recompute the maximum bisimulation incrementally.

    :param graph: The initial graph.
    :initial_partition: The initial partition, or labeling set. This is
        **not** the partition from which we start, but an indication of which
        nodes cannot be bisimilar. Defaultsto `None`, in which case the trivial
        labeling set (one block which contains all the nodes) is used.
    :param is_integer_graph: If `True`, the function assumes that
        the graph is integer, and skips the integer check (may slightly
        improve performance). Defaults to `False`.
    """

    if not isinstance(graph, nx.DiGraph):
        raise Exception("graph should be a directed graph (nx.DiGraph)")

    # if True, the input graph is already an integer graph
    original_graph_is_integer = is_integer_graph or check_normal_integer_graph(graph)
    if not original_graph_is_integer:
        # convert the graph to an "integer" graph
        integer_graph, node_to_idx = convert_to_integer_graph(graph)

        if initial_partition is not None:
            # convert the initial partition to a integer partition
            integer_initial_partition = [
                [node_to_idx[old_node] for old_node in block]
                for block in initial_partition
            ]
        else:
            integer_initial_partition = None
    else:
        integer_graph = graph
        integer_initial_partition = initial_partition
        node_to_idx = None

    vertexes, q_partition = decorate_nx_graph(
        integer_graph,
        integer_initial_partition,
    )

    # compute the current maximum bisimulation
    q_partition = paige_tarjan_qblocks(q_partition)
    return SahaPartition(q_partition, vertexes, node_to_idx)
