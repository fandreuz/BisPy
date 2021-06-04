import pytest
import networkx as nx

from bispy.utilities.rank_computation import (
    compute_rank,
)
from bispy.utilities.graph_decorator import (
    decorate_nx_graph,
)
from .rank_test_cases import noderank_dicts, graphs


@pytest.mark.parametrize("graph, node_rank_dict", zip(graphs, noderank_dicts))
def test_compute_rank(graph, node_rank_dict: dict):
    vertexes, _ = decorate_nx_graph(graph)

    for idx in range(len(vertexes)):
        assert vertexes[idx].rank == node_rank_dict[idx]

def test_rank2():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(7))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (5, 6)])
    vertexes, _ = decorate_nx_graph(graph)

def test_rank3():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 2), (0, 3), (1, 2), (2, 4), (2, 0), (3, 4)])
    vertexes, _ = decorate_nx_graph(graph)

    assert vertexes[0].rank == 2
    assert vertexes[1].rank == 2
    assert vertexes[2].rank == 2
    assert vertexes[3].rank == 1
    assert vertexes[4].rank == 0

def test_rank4():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(8))
    graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 7), (1, 2), (1, 7), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (4, 7), (5, 6), (6, 7), (4,1)])
    vertexes, _ = decorate_nx_graph(graph)

    assert vertexes[4].rank == 3

def test_rank5():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0,3), (0,2), (1,2), (2,4), (3,4), (2,2)])
    vertexes, _ = decorate_nx_graph(graph)

    assert vertexes[0].rank == 2
    assert vertexes[1].rank == 1
    assert vertexes[2].rank == 1
    assert vertexes[3].rank == 1
    assert vertexes[4].rank == 0
    assert vertexes[5].rank == 0

def test_rank6():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 2), (0, 3), (1, 2), (2, 4), (3, 4), (4,4)])
    vertexes, _ = decorate_nx_graph(graph)

    for vx in vertexes:
        assert vx.rank == float('-inf')


def test_rank_clears_visited():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(8))
    graph.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 7), (1, 2), (1, 7), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (4, 7), (5, 6), (6, 7), (4,1)])
    vertexes, _ = decorate_nx_graph(graph)

    for vx in vertexes:
        assert not vx.visited
