import pytest
import networkx as nx
from bispy.utilities.graph_decorator import (
    decorate_nx_graph,
    decorate_bispy_graph,
)
from bispy.dovier_piazza_policriti.ranked_partition import RankedPartition
from bispy.dovier_piazza_policriti.dovier_piazza_policriti import (
    build_block_counterimage,
)
from bispy.utilities.rank_computation import (
    scc_finishing_time_list,
)
from bispy.saha.saha import (
    is_in_image,
    add_edge,
    propagate_wf,
    propagate_nwf,
    check_new_scc,
    exists_causal_splitter,
    both_blocks_go_or_dont_go_to_block,
    merge_condition,
    recursive_merge,
    merge_phase,
    merge_split_phase,
    build_well_founded_topological_list,
    saha,
)
from tests.rank.rank_test_cases import graphs
from .saha_test_cases import (
    new_scc_correct_value,
    new_scc_graphs,
    new_scc_new_edge,
    exists_causal_splitter_qblocks,
    exists_causal_splitter_result_map,
    both_blocks_goto_result_map,
    new_scc_finishing_time,
    update_rscp_graphs,
    update_rscp_initial_partition,
    update_rscp_new_edge,
)
from tests.pta.pta_test_cases import graph_partition_rscp_tuples
from bispy.paige_tarjan.paige_tarjan import paige_tarjan_qblocks, paige_tarjan
from bispy.utilities.graph_entities import _Edge, _XBlock
from bispy.saha.ranked_pta import pta as ranked_pta
from itertools import chain, product
from bispy.utilities.kosaraju import kosaraju


def test_is_in_image():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 1)])

    vertexes, _ = decorate_nx_graph(graph)
    RankedPartition(vertexes)

    assert is_in_image(vertexes[0].qblock, vertexes[1].qblock)
    assert not is_in_image(vertexes[1].qblock, vertexes[0].qblock)
    assert is_in_image(vertexes[1].qblock, vertexes[2].qblock)
    assert is_in_image(vertexes[2].qblock, vertexes[3].qblock)
    assert not is_in_image(vertexes[0].qblock, vertexes[4].qblock)
    assert not is_in_image(vertexes[4].qblock, vertexes[0].qblock)


def test_add_edge():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 1)])

    vertexes, _ = decorate_nx_graph(graph)
    ranked_partition = RankedPartition(vertexes)

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

    vertexes, qblocks = decorate_nx_graph(graph, [(0,), (1,), (2,), (3, 4)])
    max_rank = max(map(lambda vx: vx.rank, vertexes))

    # be careful: for build_well_founded_topological vertexes in the same
    # block have to be of the same rank
    topo = build_well_founded_topological_list(qblocks, vertexes[3], max_rank)

    add_edge(vertexes[3], vertexes[4])

    propagate_wf(vertexes[3], topo, vertexes)

    for idx in range(5):
        assert vertexes[idx].rank == 4 - idx


@pytest.mark.parametrize(
    "graph, new_edge, value",
    zip(new_scc_graphs, new_scc_new_edge, new_scc_correct_value),
)
def test_check_new_scc(graph, new_edge, value):
    vertexes, _ = decorate_nx_graph(graph)

    add_edge(vertexes[new_edge[0]], vertexes[new_edge[1]])

    assert (
        check_new_scc(vertexes[new_edge[0]], vertexes[new_edge[1]], [])
        == value
    )


@pytest.mark.parametrize(
    "graph, new_edge, value",
    zip(new_scc_graphs, new_scc_new_edge, new_scc_correct_value),
)
def test_check_new_scc_cleans(graph, new_edge, value):
    vertexes, _ = decorate_nx_graph(graph)

    add_edge(vertexes[new_edge[0]], vertexes[new_edge[1]])

    check_new_scc(vertexes[new_edge[0]], vertexes[new_edge[1]], [])

    for vertex in vertexes:
        assert vertex.visited == False


@pytest.mark.parametrize(
    "graph, new_edge, value",
    zip(new_scc_graphs, new_scc_new_edge, new_scc_correct_value),
)
def test_check_new_scc_qblocks_visited(graph, new_edge, value):
    vertexes, _ = decorate_nx_graph(graph)

    add_edge(vertexes[new_edge[0]], vertexes[new_edge[1]])

    finishing_time_list = []
    check_new_scc(
        vertexes[new_edge[0]], vertexes[new_edge[1]], finishing_time_list
    )

    for vx in finishing_time_list:
        assert vx.qblock.visited


@pytest.mark.parametrize(
    "graph, new_edge, value, correct_finishing_time",
    zip(
        new_scc_graphs,
        new_scc_new_edge,
        new_scc_correct_value,
        new_scc_finishing_time,
    ),
)
def test_check_new_scc_computes_finishing_time(
    graph, new_edge, value, correct_finishing_time
):
    if correct_finishing_time is None:
        return

    vertexes, _ = decorate_nx_graph(graph)

    add_edge(vertexes[new_edge[0]], vertexes[new_edge[1]])

    finishing_time_list = []
    check_new_scc(
        vertexes[new_edge[0]], vertexes[new_edge[1]], finishing_time_list
    )

    assert len(finishing_time_list) == len(correct_finishing_time)

    for i in range(len(finishing_time_list)):
        assert finishing_time_list[i].label == correct_finishing_time[i]


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, both_blocks_goto_result_map),
)
def test_both_blocks_go_or_dont_go_to_block(qblocks, result_map):
    counterimages = [build_block_counterimage(block) for block in qblocks]

    for ints, result in result_map:
        block1, block2, block = ints
        assert (
            both_blocks_go_or_dont_go_to_block(
                qblocks[block1], qblocks[block2], counterimages[block]
            )
            == result
        )


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, both_blocks_goto_result_map),
)
def test_both_blocks_go_or_dont_go_to_block_commutative(qblocks, result_map):
    counterimages = [build_block_counterimage(block) for block in qblocks]

    for ints, result in result_map:
        block1, block2, block = ints
        assert both_blocks_go_or_dont_go_to_block(
            qblocks[block1], qblocks[block2], counterimages[block]
        ) == both_blocks_go_or_dont_go_to_block(
            qblocks[block2], qblocks[block1], counterimages[block]
        )


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, exists_causal_splitter_result_map),
)
def test_exists_causal_splitter(qblocks, result_map):
    for couple, result in result_map:
        assert (
            exists_causal_splitter(
                qblocks[couple[0]], qblocks[couple[1]], check_visited=False
            )
            == result
        )


@pytest.mark.parametrize(
    "qblocks, result_map",
    zip(exists_causal_splitter_qblocks, exists_causal_splitter_result_map),
)
def test_exists_causal_splitter_commutative(qblocks, result_map):
    for couple, _ in result_map:
        assert exists_causal_splitter(
            qblocks[couple[1]], qblocks[couple[0]], check_visited=False
        ) == exists_causal_splitter(
            qblocks[couple[0]], qblocks[couple[1]], check_visited=False
        )


def test_merge_condition():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from([(0, 1), (1, 2), (3, 1), (4, 6), (0, 6), (5, 6)])
    ip = [(0, 1, 2, 3), (4, 5), (6,)]

    vertexes, qblocks = decorate_nx_graph(graph, ip)
    rscp_qblocks = paige_tarjan_qblocks(qblocks)

    node_to_qblock = [None for _ in graph.nodes]
    for qb in rscp_qblocks:
        for vertex in qb.vertexes:
            node_to_qblock[vertex.label] = qb

    # can't merge because no same initial partition
    assert not merge_condition(
        node_to_qblock[2],
        node_to_qblock[6],
    )

    # different rank
    assert not merge_condition(
        node_to_qblock[2],
        node_to_qblock[1],
    )

    # same block
    assert not merge_condition(
        node_to_qblock[4],
        node_to_qblock[4],
    )

    # exists causal splitter
    assert not merge_condition(
        node_to_qblock[0],
        node_to_qblock[3],
    )


@pytest.mark.parametrize(
    "graph, initial_partition",
    map(lambda tp: (tp[0], tp[1]), graph_partition_rscp_tuples),
)
def test_merge_condition_with_initial_partition(graph, initial_partition):
    vertexes, qblocks = decorate_nx_graph(graph, initial_partition)

    for tp in product(qblocks, qblocks):
        assert not merge_condition(tp[0], tp[1])


# this kind of test is misleading: exists_causal_splitter may ignore a
# causal splitter when it's not low-rank with respect of the two blocks.
# this is done expecting a split in the future (if needed)
""" @pytest.mark.parametrize(
    "graph, initial_partition",
    map(lambda tp: (tp[0], tp[1]), graph_partition_rscp_tuples),
)
def test_merge_condition_with_rscp(graph, initial_partition):
    qblocks, vertexes = initialize(graph, initial_partition)
    rscp = pta(qblocks)
    prepare_internal_graph(vertexes, initial_partition)

    for tp in itertools.product(rscp, rscp):
        assert not merge_condition(tp[0], tp[1]) """


def vertexes_dllist_to_label_list(vx_dllist):
    return list(vx.label for vx in vx_dllist)


def test_recursive_merge():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (2, 3)])

    partition = [(0, 2), (1,), (3,), (4,)]

    vertexes, _ = decorate_nx_graph(g, partition)

    vertexes[0].qblock._mitosis([0], [2])

    recursive_merge(vertexes[1].qblock, vertexes[3].qblock)

    assert vertexes[0].qblock == vertexes[2].qblock
    assert vertexes[1].qblock == vertexes[3].qblock
    assert vertexes[0].qblock != vertexes[1].qblock


def test_update_rank():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (1, 0), (2, 3), (3, 1)])

    vertexes, _ = decorate_nx_graph(g)

    # now split
    vertexes[2].qblock._mitosis([2], [3])

    # and then add a new vertex
    new_edge = _Edge(vertexes[3], vertexes[4])
    vertexes[3].add_to_image(new_edge)
    vertexes[4].add_to_counterimage(new_edge)

    # update rank
    vertexes[3].scc._rank = 1

    sccs = kosaraju(vertexes[3], return_sccs=True)
    for scc in sccs:
        scc.compute_image()
    scc_finishing_time = scc_finishing_time_list(sccs)
    propagate_nwf(vertexes[3].scc, scc_finishing_time)

    assert vertexes[0].rank == float("-inf")
    assert vertexes[1].rank == float("-inf")
    assert vertexes[2].rank == 1
    assert vertexes[3].rank == 1
    assert vertexes[4].rank == 0


def test_merge_phase():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (1, 0), (2, 1), (2, 4), (3, 1)])

    partition = [(2, 3), (1, 0), (4,)]

    vertexes, _ = decorate_nx_graph(g, partition)

    # now split
    vertexes[2].qblock._mitosis([2], [3])

    # and then add a new vertex
    new_edge = _Edge(vertexes[3], vertexes[4])
    vertexes[3].add_to_image(new_edge)
    vertexes[4].add_to_counterimage(new_edge)

    # update rank
    vertexes[3].rank = 1
    propagate_nwf(vertexes[3].scc, kosaraju(vertexes, return_sccs=True))

    merge_phase(vertexes[3].qblock, vertexes[4].qblock)

    assert vertexes[3].qblock == vertexes[2].qblock

    # other qblocks not modified
    assert vertexes[0].qblock == vertexes[1].qblock
    assert vertexes[0].qblock != vertexes[2].qblock
    assert vertexes[2].qblock != vertexes[4].qblock
    assert vertexes[4].qblock != vertexes[0].qblock


def test_initial_partition_block_idx_not_none():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (1, 0), (2, 1), (2, 4), (3, 1)])

    partition = [(2, 3), (1, 0), (4,)]

    vertexes, _ = decorate_nx_graph(g, partition)

    for vx in vertexes:
        assert vx.initial_partition_block_id is not None

    for block in partition:
        block_id = vertexes[block[0]].initial_partition_block_id
        for vx_idx in block:
            assert vertexes[vx_idx].initial_partition_block_id == block_id

        other_vertexes_idx = set(range(5)) - set(block)
        for vx_idx in other_vertexes_idx:
            assert vertexes[vx_idx].initial_partition_block_id != block_id


def test_merge_split_phase():
    pass


def test_merge_split_resets_visited_allowvisit_oldqblockid():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (1, 0), (2, 1), (2, 4), (3, 1)])

    partition = [(2, 3), (1, 0), (4,)]

    vertexes, _ = decorate_nx_graph(g, partition)
    qblocks = [block for ls in RankedPartition(vertexes) for block in ls]

    finishing_time_list = [vertexes[2], vertexes[1], vertexes[0]]

    merge_split_phase(qblocks, finishing_time_list)

    assert all([not vertex.visited for vertex in vertexes])
    assert all([not vertex.allow_visit for vertex in vertexes])


def test_merge_split_resets_visited_triedmerge_qblocks():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (1, 0), (2, 1), (2, 4), (3, 1)])

    partition = [(2, 3), (1, 0), (4,)]

    vertexes, _ = decorate_nx_graph(g, partition)
    qblocks = [block for ls in RankedPartition(vertexes) for block in ls]

    qblocks[0].visited = True
    qblocks[2].visited = True

    finishing_time_list = [vertexes[2], vertexes[1], vertexes[0]]

    qpartition = merge_split_phase(qblocks, finishing_time_list)

    assert all([not block.visited for block in qpartition])
    assert all([not block.tried_merge for block in qpartition])


def test_well_founded_topological():
    g = nx.DiGraph()
    g.add_nodes_from(range(8))
    g.add_edges_from([(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 6)])

    partition = [(0, 3), (1, 4), (2, 5), (6, 7)]

    vertexes, _ = decorate_nx_graph(g, partition)

    max_rank = max(map(lambda vx: vx.rank, vertexes))

    qpartition = [block for ls in RankedPartition(vertexes) for block in ls]

    topo = build_well_founded_topological_list(
        qpartition, vertexes[5], max_rank
    )

    assert len(topo) == 6

    last_rank = None
    for vx in topo:
        assert vx.wf
        if last_rank is not None:
            assert last_rank <= vx.rank
        last_rank = vx.rank


def all_possible_new_edges(graph, initial_partition):
    for source, dest in product(graph.nodes, graph.nodes):
        if not (source, dest) in graph.edges:
            yield (graph, (source, dest), initial_partition)


def vertexes_to_set(qblocks):
    return set(
        [
            frozenset(map(lambda vx: vx.label, block.vertexes))
            for block in qblocks
        ]
    )


@pytest.mark.parametrize(
    "graph, new_edge, initial_partition",
    chain(
        [
            tp
            for iterator in map(
                lambda x: (all_possible_new_edges(x[0], x[1])),
                graph_partition_rscp_tuples,
            )
            for tp in iterator
        ],
        zip(
            update_rscp_graphs,
            update_rscp_new_edge,
            update_rscp_initial_partition,
        ),
    ),
)
def test_update_rank_procedures(graph, new_edge, initial_partition):
    vertexes, qblocks = decorate_nx_graph(graph, initial_partition)
    qblocks = paige_tarjan_qblocks(qblocks)

    # compute incrementally
    saha(qblocks, vertexes, new_edge)

    # compute from scratch
    graph2 = nx.DiGraph()
    graph2.add_nodes_from(graph.nodes)
    graph2.add_edges_from(graph.edges)
    graph2.add_edge(*new_edge)
    new_vertexes, new_qblocks = decorate_nx_graph(graph2, initial_partition)

    for i in range(len(vertexes)):
        assert vertexes[i].rank == new_vertexes[i].rank


def ints_to_set(blocks):
    return set([frozenset(block) for block in blocks])


@pytest.mark.parametrize(
    "graph, new_edge, initial_partition",
    chain(
        [
            tp
            for iterator in map(
                lambda x: (all_possible_new_edges(x[0], x[1])),
                graph_partition_rscp_tuples,
            )
            for tp in iterator
        ],
        zip(
            update_rscp_graphs,
            update_rscp_new_edge,
            update_rscp_initial_partition,
        ),
    ),
)
def test_update_rscp_correctness(graph, new_edge, initial_partition):
    vertexes, qblocks = decorate_nx_graph(graph, initial_partition)
    qblocks = paige_tarjan_qblocks(qblocks)

    # compute incrementally
    update_result = saha(qblocks, vertexes, new_edge)
    update_result = vertexes_to_set(update_result)

    # compute from scratch
    graph2 = nx.DiGraph()
    graph2.add_nodes_from(graph.nodes)
    graph2.add_edges_from(graph.edges)
    graph2.add_edge(*new_edge)
    new_vertexes, new_qblocks = decorate_nx_graph(graph2, initial_partition)
    new_rscp = paige_tarjan_qblocks(new_qblocks)
    new_rscp = vertexes_to_set(new_rscp)

    assert update_result == new_rscp


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
    vertexes, qblocks = decorate_nx_graph(initial_graph, initial_partition)

    edges = []
    for edge in goal_graph.edges:
        edges.append(edge)

        g = nx.DiGraph()
        g.add_nodes_from(goal_graph.nodes)
        g.add_edges_from(edges)

        # compute its rscp
        rscp = paige_tarjan(g, initial_partition, is_integer_graph=True)
        rscp = ints_to_set(rscp)

        # compute the rscp incrementally
        qblocks = saha(qblocks, vertexes, edge)
        qblocks_as_int = [
            tuple(vx.label for vx in block.vertexes) for block in qblocks
        ]
        qblocks_as_int = ints_to_set(qblocks_as_int)

        assert qblocks_as_int == rscp


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
def test_reverse_incremental_update_rscp_correctness(
    goal_graph, initial_partition
):
    initial_graph = nx.DiGraph()
    initial_graph.add_nodes_from(goal_graph.nodes)
    vertexes, qblocks = decorate_nx_graph(initial_graph, initial_partition)

    edges = []
    full_edges = list(goal_graph.edges)
    full_edges.reverse()

    for edge in full_edges:
        edges.append(edge)

        g = nx.DiGraph()
        g.add_nodes_from(goal_graph.nodes)
        g.add_edges_from(edges)

        # compute its rscp
        rscp = paige_tarjan(g, initial_partition, is_integer_graph=True)
        rscp = ints_to_set(rscp)

        # compute the rscp incrementally
        qblocks = saha(qblocks, vertexes, edge)
        qblocks_as_int = [
            tuple(vx.label for vx in block.vertexes) for block in qblocks
        ]
        qblocks_as_int = ints_to_set(qblocks_as_int)

        assert qblocks_as_int == rscp
