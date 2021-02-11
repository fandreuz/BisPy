import pytest
import networkx as nx
from bisimulation_algorithms.saha.graph_decorator import (
    prepare_graph,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    create_initial_partition,
    build_block_counterimage,
)
from bisimulation_algorithms.saha.saha import (
    check_old_blocks_relation,
    find_vertexes,
    add_edge,
    propagate_wf,
    propagate_nwf,
    check_new_scc,
    exists_causal_splitter,
    both_blocks_go_to_block,
    merge_condition,
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
    exists_causal_splitter_qblocks,
    exists_causal_splitter_result_map,
    both_blocks_goto_result_map,
)
from tests.pta.pta_test_cases import graph_partition_rscp_tuples
from bisimulation_algorithms.paige_tarjan.graph_decorator import initialize
import itertools
from bisimulation_algorithms.paige_tarjan.pta import pta


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


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, both_blocks_goto_result_map),
)
def test_both_blocks_go_to_block(qblocks, result_map):
    counterimages = [build_block_counterimage(block) for block in qblocks]

    for ints, result in result_map:
        block1, block2, block = ints
        assert (
            both_blocks_go_to_block(
                qblocks[block1], qblocks[block2], counterimages[block]
            )
            == result
        )


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, both_blocks_goto_result_map),
)
def test_both_blocks_go_to_block_commutative(qblocks, result_map):
    counterimages = [build_block_counterimage(block) for block in qblocks]

    for ints, result in result_map:
        block1, block2, block = ints
        assert both_blocks_go_to_block(
            qblocks[block1], qblocks[block2], counterimages[block]
        ) == both_blocks_go_to_block(
            qblocks[block2], qblocks[block1], counterimages[block]
        )


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, exists_causal_splitter_result_map),
)
def test_exists_causal_splitter(qblocks, result_map):
    counterimages = [
        (block, build_block_counterimage(block)) for block in qblocks
    ]

    for couple, result in result_map:
        assert result == exists_causal_splitter(
            qblocks[couple[0]], qblocks[couple[1]], counterimages
        )


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, exists_causal_splitter_result_map),
)
def test_exists_causal_splitter_commutative(qblocks, result_map):
    counterimages = [
        (block, build_block_counterimage(block)) for block in qblocks
    ]

    for couple, _ in result_map:
        assert exists_causal_splitter(
            qblocks[couple[1]], qblocks[couple[0]], counterimages
        ) == exists_causal_splitter(
            qblocks[couple[0]], qblocks[couple[1]], counterimages
        )


def test_merge_condition():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (3, 1), (4, 6), (0, 6), (5, 6)])

    qblocks, vertexes = initialize(graph, [(0, 1, 2, 3), (4, 5), (6,)])
    rscp_qblocks = pta(qblocks)

    node_to_qblock = [None for _ in graph.nodes]
    for qb in rscp_qblocks:
        for vertex in qb.vertexes:
            node_to_qblock[vertex.label] = qb

    blocks_and_counterimages = [
        (block, build_block_counterimage(block)) for block in rscp_qblocks
    ]

    # can't merge because no same initial partition
    assert not merge_condition(
        node_to_qblock[2], node_to_qblock[6], blocks_and_counterimages
    )

    # different rank
    assert not merge_condition(
        node_to_qblock[2], node_to_qblock[1], blocks_and_counterimages
    )

    # same block
    assert not merge_condition(
        node_to_qblock[4], node_to_qblock[4], blocks_and_counterimages
    )

    # exists causal splitter
    assert not merge_condition(
        node_to_qblock[0], node_to_qblock[3], blocks_and_counterimages
    )


@pytest.mark.parametrize(
    "graph, initial_partition",
    map(lambda tp: (tp[0], tp[1]), graph_partition_rscp_tuples),
)
def test_merge_condition_with_initial_partition(graph, initial_partition):
    qblocks, vertexes = initialize(graph, initial_partition)

    blocks_and_counterimages = [
        (block, build_block_counterimage(block)) for block in qblocks
    ]

    for tp in itertools.product(qblocks, qblocks):
        assert not merge_condition(tp[0], tp[1], blocks_and_counterimages)


@pytest.mark.parametrize(
    "graph, initial_partition",
    map(lambda tp: (tp[0], tp[1]), graph_partition_rscp_tuples),
)
def test_merge_condition_with_rscp(graph, initial_partition):
    qblocks, vertexes = initialize(graph, initial_partition)
    rscp = pta(qblocks)

    blocks_and_counterimages = [
        (block, build_block_counterimage(block)) for block in rscp
    ]

    for tp in itertools.product(rscp, rscp):
        assert not merge_condition(tp[0], tp[1], blocks_and_counterimages)


def test_recursive_merge():
    pass


def test_merge_phase():
    pass


def test_merge_split_phase():
    pass
