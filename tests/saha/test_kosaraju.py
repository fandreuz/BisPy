import pytest
from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _Edge,
)
import networkx as nx
from bisimulation_algorithms.saha.kosaraju import kosaraju
from bisimulation_algorithms.saha.graph_decorator import (
    prepare_nx_graph as prepare_graph,
)

def test_scc1():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4,), (4, 3), (3, 0), (4, 5)])

    vertexes, _ = prepare_graph(graph)
    result = kosaraju(vertexes)
    result = set([
        frozenset([v.label for v in s]) for s in result.values()
    ])

    assert set([0, 1, 2]) in result
    assert set([3,4]) in result
    assert set([5]) in result
    assert len(result) == 3

def test_scc2():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4,), (4, 3), (3, 0), (2,4), (4, 5)])

    vertexes, _ = prepare_graph(graph)
    result = kosaraju(vertexes)
    result = set([
        frozenset([v.label for v in s]) for s in result.values()
    ])

    assert set([0, 1, 2, 3,4]) in result
    assert set([5]) in result
    assert len(result) == 2

def test_scc3():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3,4), (4,5)])

    vertexes, _ = prepare_graph(graph)
    result = kosaraju(vertexes)
    result = set([
        frozenset([v.label for v in s]) for s in result.values()
    ])

    assert set([0,]) in result
    assert set([5,]) in result
    assert set([1,]) in result
    assert set([2,]) in result
    assert set([3,]) in result
    assert set([4,]) in result
    assert len(result) == 6
