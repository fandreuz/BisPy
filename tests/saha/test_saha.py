import pytest
import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    prepare_graph,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    create_initial_partition,
)
from bisimulation_algorithms.saha.saha import check_old_blocks_relation, find_vertexes

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
