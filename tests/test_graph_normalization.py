import pytest
import networkx as nx

from bispy.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)


def test_integer_graph():
    nodes = [0, 1, 2, "a", "b", frozenset([5]), nx.DiGraph()]

    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)

    # add an edge to the next node, and to the first node in the list
    for i in range(len(nodes) - 1):
        graph.add_edge(nodes[i], nodes[0])
        graph.add_edge(nodes[i], nodes[i + 1])

    integer_graph, node_to_idx = convert_to_integer_graph(graph)

    # test the map's correctness
    for node in nodes:
        assert nodes[node_to_idx[node]] == node

    # test the correctness of edges
    for edge in integer_graph.edges:
        assert edge[1] == edge[0] + 1 or edge[1] == 0


def test_integrality_check():
    # 1
    g1 = nx.DiGraph()
    g1.add_nodes_from([1, 2, 3, 4])
    assert not check_normal_integer_graph(g1)

    # 2
    g2 = nx.DiGraph()
    g2.add_nodes_from(["a", 0, 2, 3, 4])
    assert not check_normal_integer_graph(g2)

    # 3
    g3 = nx.DiGraph()
    g3.add_nodes_from([0, 1, 2, 3, 4])
    assert check_normal_integer_graph(g3)

    # 4
    g4 = nx.DiGraph()
    g4.add_nodes_from([0, 2, 3, 4])
    assert not check_normal_integer_graph(g4)


def test_back_to_original():
    nodes = [0, 1, 2, "a", "b", frozenset([5])]

    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)

    _, node_to_idx = convert_to_integer_graph(graph)

    partition = [("a", "b"), (0, 1, 2), (frozenset([5]),)]
    integer_partition = [
        (node_to_idx[node] for node in block) for block in partition
    ]

    assert set(
        frozenset(tp)
        for tp in back_to_original(integer_partition, node_to_idx)
    ) == set(frozenset(tp) for tp in partition)
