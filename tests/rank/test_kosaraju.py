import pytest
from bispy.utilities.graph_entities import (
    _Vertex,
    _Edge,
)
import networkx as nx
from bispy.utilities.kosaraju import kosaraju
from bispy.utilities.graph_decorator import (
    decorate_nx_graph
)

def test_scc1():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4,), (4, 3), (3, 0), (4, 5)])

    vertexes, _ = decorate_nx_graph(graph)
    result = kosaraju(vertexes, return_sccs=True)
    result = set([
        frozenset([v.label for v in scc._vertexes]) for scc in result
    ])

    assert set([0, 1, 2]) in result
    assert set([3,4]) in result
    assert set([5]) in result
    assert len(result) == 3

def test_scc2():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4,), (4, 3), (3, 0), (2,4), (4, 5)])

    vertexes, _ = decorate_nx_graph(graph)
    result = kosaraju(vertexes, return_sccs=True)
    result = set([
        frozenset([v.label for v in scc._vertexes]) for scc in result
    ])

    assert set([0, 1, 2, 3,4]) in result
    assert set([5]) in result
    assert len(result) == 2

def test_scc3():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3,4), (4,5)])

    vertexes, _ = decorate_nx_graph(graph)
    result = kosaraju(vertexes, return_sccs=True)
    result = set([
        frozenset([v.label for v in scc._vertexes]) for scc in result
    ])

    assert set([0,]) in result
    assert set([5,]) in result
    assert set([1,]) in result
    assert set([2,]) in result
    assert set([3,]) in result
    assert set([4,]) in result
    assert len(result) == 6

def test_scc4():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 2), (0, 3), (1, 2), (2, 4), (3, 4), (0,0)])

    vertexes, _ = decorate_nx_graph(graph)
    result = kosaraju(vertexes, return_sccs=True)
    result = set([
        frozenset([v.label for v in scc._vertexes]) for scc in result
    ])

    assert set([0,]) in result
    assert set([1,]) in result
    assert set([2,]) in result
    assert set([3,]) in result
    assert set([4,]) in result
    assert len(result) == 5

def test_scc5():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0,3), (0,2), (1,2), (2,4), (3,4), ])

    vertexes, _ = decorate_nx_graph(graph)
    result = kosaraju(vertexes, return_sccs=True)
    result = set([
        frozenset([v.label for v in scc._vertexes]) for scc in result
    ])

    assert set([0,]) in result
    assert set([1,]) in result
    assert set([2,]) in result
    assert set([3,]) in result
    assert set([4,]) in result
    assert len(result) == 6

def test_kosaraju_unvisits():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4,), (4, 3), (3, 0), (4, 5)])

    vertexes, _ = decorate_nx_graph(graph)
    result = kosaraju(vertexes, return_sccs=True)

    for v in vertexes:
        assert not v.visited
