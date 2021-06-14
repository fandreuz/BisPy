import pytest
import networkx as nx
from bispy.utilities.graph_decorator import (
    decorate_nx_graph,
    decorate_bispy_graph,
)
from bispy.dovier_piazza_policriti.fba import fba
from bispy.dovier_piazza_policriti.fba import (
    create_initial_partition,
    build_block_counterimage,
)
from bispy.utilities.rank_computation import (
    scc_finishing_time_list,
)
from bispy.saha.saha import (
    check_old_blocks_relation,
    find_vertexes,
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
    update_rscp,
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
from bispy.paige_tarjan.pta import pta, rscp as paige_tarjan
from bispy.utilities.graph_entities import _Edge, _XBlock
from bispy.saha.ranked_pta import pta as ranked_pta
from itertools import chain, product
from bispy.utilities.kosaraju import kosaraju


def test_check_old_blocks_relation():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 1)])

    vertexes, _ = decorate_nx_graph(graph)
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

    vertexes, _ = decorate_nx_graph(graph)
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

    vertexes, _ = decorate_nx_graph(graph)
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
    create_initial_partition(vertexes)

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
    create_initial_partition(vertexes)

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
    create_initial_partition(vertexes)

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
    create_initial_partition(vertexes)

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
    rscp_qblocks = pta(qblocks)

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
    qblocks = [
        block for ls in create_initial_partition(vertexes) for block in ls
    ]

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
    qblocks = [
        block for ls in create_initial_partition(vertexes) for block in ls
    ]

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

    qpartition = [
        block for ls in create_initial_partition(vertexes) for block in ls
    ]

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
    vertexes, qblocks  = decorate_nx_graph(graph, initial_partition)
    qblocks = pta(qblocks)

    # compute incrementally
    update_rscp(qblocks, new_edge, vertexes)

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
    qblocks = pta(qblocks)

    # compute incrementally
    update_result = update_rscp(qblocks, new_edge, vertexes)
    update_result = vertexes_to_set(update_result)

    # compute from scratch
    graph2 = nx.DiGraph()
    graph2.add_nodes_from(graph.nodes)
    graph2.add_edges_from(graph.edges)
    graph2.add_edge(*new_edge)
    new_vertexes, new_qblocks = decorate_nx_graph(graph2, initial_partition)
    new_rscp = pta(new_qblocks)
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
        qblocks = update_rscp(qblocks, edge, vertexes)
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
        qblocks = update_rscp(qblocks, edge, vertexes)
        qblocks_as_int = [
            tuple(vx.label for vx in block.vertexes) for block in qblocks
        ]
        qblocks_as_int = ints_to_set(qblocks_as_int)

        assert qblocks_as_int == rscp

def test_saha_big_graph():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(100))
    graph.add_edges_from([(0, 8), (0, 18), (0, 25), (0, 31), (0, 36), (0, 37), (0, 82), (0, 95), (1, 8), (1, 9), (1, 47), (1, 69), (1, 83), (2, 3), (2, 8), (2, 27), (2, 51), (2, 81), (3, 4), (3, 42), (3, 55), (3, 58), (3, 60), (3, 71), (4, 18), (4, 21), (4, 29), (4, 54), (4, 80), (5, 11), (5, 20), (5, 34), (5, 36), (5, 43), (5, 56), (5, 71), (6, 2), (6, 9), (6, 15), (6, 22), (6, 64), (6, 79), (6, 83), (7, 27), (7, 34), (7, 45), (7, 55), (7, 70), (7, 84), (8, 2), (8, 32), (8, 78), (8, 90), (9, 26), (9, 30), (9, 45), (9, 84), (9, 88), (10, 17), (10, 21), (10, 59), (11, 17), (11, 38), (12, 25), (12, 28), (12, 67), (13, 2), (13, 19), (13, 23), (13, 36), (13, 96), (14, 92), (14, 93), (15, 21), (15, 87), (15, 92), (16, 29), (16, 51), (16, 77), (16, 89), (17, 19), (17, 27), (17, 40), (17, 45), (17, 68), (17, 74), (17, 81), (18, 21), (18, 22), (18, 49), (18, 55), (18, 72), (19, 2), (19, 39), (19, 70), (19, 74), (20, 16), (20, 21), (20, 40), (20, 57), (21, 37), (21, 46), (21, 54), (21, 73), (21, 93), (22, 4), (22, 18), (22, 24), (23, 13), (23, 16), (23, 58), (23, 84), (24, 68), (25, 3), (25, 12), (25, 15), (25, 74), (25, 76), (26, 13), (26, 28), (26, 50), (26, 83), (26, 87), (27, 18), (27, 50), (27, 51), (27, 76), (28, 16), (28, 18), (28, 30), (28, 45), (28, 65), (28, 80), (29, 6), (29, 8), (29, 10), (29, 16), (29, 46), (29, 78), (29, 88), (30, 36), (30, 41), (31, 34), (31, 65), (32, 28), (32, 48), (32, 75), (33, 24), (33, 25), (33, 26), (33, 34), (33, 38), (33, 62), (33, 69), (33, 75), (34, 38), (34, 55), (34, 60), (34, 65), (34, 85), (35, 16), (35, 47), (35, 53), (35, 61), (36, 27), (36, 34), (37, 42), (37, 60), (37, 74), (37, 97), (38, 4), (38, 41), (38, 48), (38, 77), (39, 20), (39, 61), (39, 70), (39, 95), (40, 8), (40, 11), (40, 17), (40, 34), (40, 85), (40, 91), (41, 9), (41, 12), (41, 26), (41, 68), (42, 18), (42, 39), (42, 44), (42, 75), (43, 11), (43, 12), (43, 19), (43, 81), (43, 96), (44, 3), (44, 4), (44, 17), (44, 21), (44, 51), (44, 57), (44, 66), (44, 69), (45, 20), (45, 31), (45, 34), (45, 38), (45, 47), (45, 60), (45, 67), (45, 81), (45, 94), (46, 0), (46, 30), (47, 13), (47, 32), (47, 34), (47, 43), (47, 73), (47, 79), (48, 18), (48, 49), (48, 97), (49, 0), (49, 12), (49, 21), (49, 25), (49, 39), (49, 52), (49, 55), (49, 61), (50, 32), (50, 45), (50, 47), (50, 58), (50, 67), (50, 76), (50, 84), (51, 9), (51, 22), (51, 27), (51, 33), (51, 52), (51, 60), (51, 66), (51, 87), (52, 42), (52, 51), (52, 62), (52, 66), (52, 71), (52, 72), (52, 79), (52, 92), (53, 3), (53, 8), (53, 16), (53, 83), (53, 88), (53, 98), (54, 4), (54, 11), (54, 14), (54, 39), (54, 49), (54, 79), (55, 53), (55, 62), (56, 14), (56, 60), (57, 51), (57, 70), (57, 82), (58, 5), (58, 21), (58, 57), (58, 67), (58, 82), (59, 14), (59, 32), (59, 37), (59, 38), (59, 78), (59, 87), (60, 4), (60, 7), (60, 17), (60, 18), (60, 38), (60, 44), (60, 73), (60, 74), (61, 9), (61, 17), (61, 30), (61, 35), (61, 38), (61, 40), (61, 50), (61, 62), (62, 22), (62, 46), (63, 5), (63, 21), (63, 89), (64, 5), (64, 65), (66, 33), (66, 36), (66, 67), (66, 74), (67, 14), (68, 1), (68, 4), (68, 21), (68, 34), (68, 78), (69, 21), (69, 40), (69, 57), (69, 59), (69, 62), (69, 91), (70, 3), (70, 9), (70, 23), (70, 30), (70, 45), (70, 71), (71, 5), (71, 12), (71, 22), (71, 27), (71, 47), (71, 61), (71, 98), (72, 15), (72, 27), (72, 42), (72, 43), (72, 46), (72, 55), (72, 59), (72, 63), (73, 10), (73, 61), (74, 1), (74, 19), (74, 20), (74, 33), (74, 36), (74, 67), (75, 7), (75, 32), (75, 65), (75, 71), (75, 99), (76, 91), (77, 54), (77, 57), (77, 71), (77, 79), (77, 92), (78, 2), (78, 24), (79, 19), (79, 20), (79, 39), (79, 46), (79, 77), (79, 78), (79, 80), (80, 57), (80, 67), (80, 68), (80, 76), (80, 77), (81, 29), (81, 32), (82, 24), (82, 38), (82, 48), (82, 98), (83, 4), (83, 79), (83, 80), (83, 85), (83, 88), (84, 4), (84, 25), (84, 32), (84, 34), (84, 45), (84, 74), (85, 26), (85, 30), (85, 32), (85, 33), (85, 94), (85, 96), (86, 6), (86, 27), (86, 28), (86, 50), (86, 55), (86, 61), (86, 68), (87, 13), (87, 21), (87, 28), (87, 35), (87, 48), (88, 11), (88, 34), (88, 69), (88, 74), (89, 8), (89, 15), (89, 16), (89, 24), (89, 29), (90, 9), (90, 10), (90, 67), (90, 74), (90, 77), (90, 94), (91, 24), (91, 88), (91, 96), (92, 25), (92, 69), (92, 70), (92, 99), (93, 3), (93, 44), (93, 94), (94, 78), (94, 89), (94, 90), (95, 8), (95, 14), (95, 36), (95, 67), (96, 8), (96, 27), (96, 51), (96, 82), (96, 86), (97, 5), (97, 10), (97, 13), (97, 26), (97, 78), (98, 20), (98, 21), (98, 25), (98, 45), (98, 61), (98, 84), (98, 94), (99, 21), (99, 51), (99, 55), (99, 61), (99, 74)])

    initial_partition = [tuple(range(len(graph.nodes)))]

    vertexes, qblocks = decorate_nx_graph(graph, initial_partition)
    qblocks = pta(qblocks)

    qb2 = update_rscp(qblocks, vertexes, [44, 45])
