import pytest
import networkx as nx
from bisimulation_algorithms.saha.graph_decorator import (
    prepare_graph,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    create_initial_partition,
)
from bisimulation_algorithms.saha.saha import (
    check_old_blocks_relation,
    find_vertexes,
    add_edge,
    propagate_wf,
    propagate_nwf,
    check_new_scc,
)
from tests.fba.rank.rank_test_cases import graphs
from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
    compute_finishing_time_list,
)
from .saha_test_cases import (
    new_scc_correct_value,
    new_scc_graphs,
    new_scc_new_edge,
)


def test_check_old_blocks_relation():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 1)])

    vertexes = prepare_graph(graph)
    create_initial_partition(vertexes)

    assert check_old_blocks_relation(vertexes[0], vertexes[1])
    assert not check_old_blocks_relation(vertexes[1], vertexes[0])
    assert check_old_blocks_relation(vertexes[1], vertexes[2])
    assert check_old_blocks_relation(vertexes[2], vertexes[3])
    assert not check_old_blocks_relation(vertexes[0], vertexes[4])
    assert not check_old_blocks_relation(vertexes[4], vertexes[0])


def test_find_vertex():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 1)])

    vertexes = prepare_graph(graph)
    ranked_partition = create_initial_partition(vertexes)
    nonranked_partition = [
        qblock for rank in ranked_partition for qblock in rank
    ]

    assert find_vertexes(nonranked_partition, 0, 1) == (
        vertexes[0],
        vertexes[1],
    )


def test_add_edge():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 1)])

    vertexes = prepare_graph(graph)
    ranked_partition = create_initial_partition(vertexes)

    partition = []
    for rank in ranked_partition:
        for block in ranked_partition:
            partition.append(block)

    edge1 = add_edge(vertexes[0], vertexes[3])
    assert edge1.count is not None
    assert edge1.count.value == 2

    edge2 = add_edge(vertexes[3], vertexes[4])
    assert edge2.count is not None
    assert edge2.count.value == 1


def test_propagate_wf():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3)])

    vertexes = prepare_graph(graph)

    add_edge(vertexes[3], vertexes[4])
    vertexes[3].rank = 1

    propagate_wf(vertexes[3], vertexes)

    for idx in range(5):
        assert vertexes[idx].rank == 4 - idx


def test_compute_rank():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5)])

    copy = nx.DiGraph()
    copy.add_nodes_from(range(6))
    copy.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (4, 5)])

    vertexes = prepare_graph(graph)
    vertexes_copy = prepare_graph(copy)

    add_edge(vertexes[3], vertexes[4])
    add_edge(vertexes_copy[3], vertexes_copy[4])

    propagate_nwf(vertexes)

    finishing_time_list = compute_finishing_time_list(vertexes_copy)
    compute_rank(vertexes_copy, finishing_time_list)

    for i in range(len(vertexes)):
        assert vertexes[i].rank == vertexes_copy[i].rank


@pytest.mark.parametrize(
    "graph, new_edge, value",
    zip(new_scc_graphs, new_scc_new_edge, new_scc_correct_value),
)
def test_check_new_scc(graph, new_edge, value):
    vertexes = prepare_graph(graph)
    create_initial_partition(vertexes)

    add_edge(vertexes[new_edge[0]], vertexes[new_edge[1]])

    assert check_new_scc(vertexes[new_edge[0]], vertexes[new_edge[1]]) == value


@pytest.mark.parametrize(
    "graph, new_edge, value",
    zip(new_scc_graphs, new_scc_new_edge, new_scc_correct_value),
)
def test_check_new_scc_cleans(graph, new_edge, value):
    vertexes = prepare_graph(graph)
    create_initial_partition(vertexes)

    add_edge(vertexes[new_edge[0]], vertexes[new_edge[1]])

    check_new_scc(vertexes[new_edge[0]], vertexes[new_edge[1]])

    for vertex in vertexes:
        assert vertex.visited == False


def test_exists_causal_splitter():
    pass


def test_merge_condition():
    pass


def test_recursive_merge():
    pass


def test_merge_phase():
    pass


def test_merge_split_phase():
    pass
