import pytest
from bispy.saha.saha import saha
from bispy.saha.saha_partition import saha as saha_partition
from .saha_test_cases import (
    update_rscp_graphs,
    update_rscp_initial_partition,
)
from tests.paige_tarjan.paige_tarjan_test_cases import graph_partition_rscp_tuples
from bispy.utilities.graph_decorator import to_set, to_tuple_list
from itertools import chain
import networkx as nx
from bispy.paige_tarjan.paige_tarjan import paige_tarjan


@pytest.mark.parametrize(
    "goal_graph, initial_partition",
    chain(
        [(tp[0], tp[1]) for tp in graph_partition_rscp_tuples],
        zip(
            update_rscp_graphs,
            update_rscp_initial_partition,
        ),
    ),
)
def test_incremental_update_rscp_correctness(goal_graph, initial_partition):
    initial_graph = nx.DiGraph()
    initial_graph.add_nodes_from(goal_graph.nodes)

    partition = saha_partition(initial_graph, initial_partition)

    edges = []
    for edge in goal_graph.edges:
        edges.append(edge)

        g = nx.DiGraph()
        g.add_nodes_from(goal_graph.nodes)
        g.add_edges_from(edges)

        # compute its rscp
        rscp = set(
            map(frozenset, paige_tarjan(g, initial_partition, is_integer_graph=True))
        )

        # compute the rscp incrementally
        rscp2 = partition.add_edge(edge)

        assert to_set(rscp2) == rscp


def test_graph_normalization():
    graph = nx.DiGraph()
    nodes = ["nodo1", "nodo2", "nodo3"]
    edges = [(0, 1), (2, 0)]
    graph.add_nodes_from(nodes)
    graph.add_edges_from(map(lambda tp: (nodes[tp[0]], nodes[tp[1]]), edges))

    partition = saha_partition(graph)

    assert set(map(frozenset, partition.add_edge(("nodo2", "nodo3")))) == set(
        [frozenset(nodes)]
    )
