import pytest
import networkx as nx
from bisimulation_algorithms.saha.graph_decorator import (
    prepare_graph,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    create_initial_partition,
)
from bisimulation_algorithms.saha.saha import check_old_blocks_relation, find_vertexes, add_edge

def test_check_old_blocks_relation():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0,1), (1,2), (2,3), (4,1)])

    vertexes = prepare_graph(graph)
    partition = create_initial_partition(vertexes)

    assert check_old_blocks_relation(vertexes[0], vertexes[1])
    assert not check_old_blocks_relation(vertexes[1], vertexes[0])
    assert check_old_blocks_relation(vertexes[1], vertexes[2])
    assert check_old_blocks_relation(vertexes[2], vertexes[3])
    assert not check_old_blocks_relation(vertexes[0], vertexes[4])
    assert not check_old_blocks_relation(vertexes[4], vertexes[0])

def test_find_vertex():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0,1), (1,2), (2,3), (4,1)])

    vertexes = prepare_graph(graph)
    partition = create_initial_partition(vertexes)

    assert find_vertexes(partition, 0,1) == (vertexes[0], vertexes[1])

def test_add_edge():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0,1), (1,2), (2,3), (4,1)])

    vertexes = prepare_graph(graph)
    ranked_partition = create_initial_partition(vertexes)

    partition = []
    for rank in ranked_partition:
        for block in ranked_partition:
            partition.append(block)

    edge1 = add_edge(vertexes[0], vertexes[3], partition)
    assert edge1.count is not None
    assert edge1.count.value == 2

    edge2 = add_edge(vertexes[3], vertexes[4], partition)
    assert edge2.count is not None
    assert edge2.count.value == 1
