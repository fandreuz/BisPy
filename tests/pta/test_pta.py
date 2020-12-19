import pytest
import networkx as nx
from llist import dllist, dllistnode
import tests.pta.pta_test_cases as test_cases
import itertools

from tests.pta.rscp_utilities import check_block_stability, is_stable_partition

from bisimulation_algorithms.paige_tarjan.graph_entities import _Vertex, _Edge, _QBlock, _XBlock
from bisimulation_algorithms.paige_tarjan.pta import split, extract_splitter, build_block_counterimage, build_exclusive_B_counterimage, refine, pta
from bisimulation_algorithms.paige_tarjan.graph_decorator import initialize, prepare_graph_abstraction, preprocess_initial_partition
from bisimulation_algorithms.paige_tarjan.pta_algorithm import rscp as evaluate_rscp, convert_to_integer_graph, check_normal_integer_graph

import pta_test_cases as test_cases

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_preprocess(graph, initial_partition):
    vertexes = prepare_graph_abstraction(graph)
    processed_partition = preprocess_initial_partition(
        vertexes, initial_partition
    )

    # check if leafs and non-leafs aren't mixed
    for block in processed_partition:
        leafs_count = 0
        for (idx, vertex_idx) in enumerate(block):
            if len(vertexes[vertex_idx].image) == 0:
                # fine
                if idx == 0:
                    leafs_count += 1
                else:
                    assert leafs_count != 0
            else:
                assert leafs_count == 0


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_qpartition_initialize(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)

    vertexes = set()
    for qblock in q_partition:
        vertexes.update(qblock.vertexes)

    assert set(map(lambda vertex: vertex.label, vertexes)) == set(
        [idx for idx, _ in enumerate(graph.nodes)]
    )


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_initialize_right_types(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)

    for qblock in q_partition:
        assert isinstance(qblock.vertexes, dllist)

    for qblock in q_partition:
        for vertex in qblock.vertexes:
            for v in vertex.image:
                assert isinstance(v, _Edge)
            for v in vertex.counterimage:
                assert isinstance(v, _Edge)
            assert isinstance(vertex.qblock, _QBlock)


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_count_initialize(graph, initial_partition):
    (_, vertexes) = initialize(graph, initial_partition)

    for vertex in vertexes:
        for edge in vertex.image:
            assert edge.count.value == len(vertex.image)


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_vertex_image_initialize(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)

    right_image = [set() for node in graph.nodes]
    for edge in graph.edges:
        right_image[edge[0]].add(_Edge(vertexes[edge[0]], vertexes[edge[1]]))

    for block in q_partition:
        for vertex in block.vertexes:
            vertex_image = set(vertex.image)
            assert vertex_image == right_image[vertex.label]


# test if initialize computed the vertexes counterimages properly
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_vertex_counterimage_initialize(graph, initial_partition):

    (q_partition, vertexes) = initialize(graph, initial_partition)

    right_counterimage = [set() for node in graph.nodes]
    for edge in graph.edges:
        right_counterimage[edge[1]].add(
            _Edge(vertexes[edge[0]], vertexes[edge[1]])
        )

    for block in q_partition:
        for vertex in block.vertexes:
            vertex_counterimage = set(vertex.counterimage)
            assert vertex_counterimage == right_counterimage[vertex.label]


def test_choose_qblock():
    compoundblock = _XBlock()
    qblocks = [
        _QBlock([0, 3, 5], compoundblock),
        _QBlock([2, 4], compoundblock),
        _QBlock([1, 6, 8], compoundblock),
    ]
    for qblock in qblocks:
        compoundblock.append_qblock(qblock)

    splitter = extract_splitter(compoundblock)
    assert splitter == qblocks[1]

    # check if compound block has been modified properly
    assert compoundblock.qblocks.size == 2

    compoundblock_qblocks = set()
    for i in range(2):
        compoundblock_qblocks.add(compoundblock.qblocks.nodeat(i).value)
    assert compoundblock_qblocks == set([qblocks[0], qblocks[2]])


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_build_block_counterimage(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)
    for qblock in q_partition:

        def extract_vertex_label(llistobject):
            return llistobject.label

        block_counterimage = set(
            [vertex.label for vertex in build_block_counterimage(qblock)]
        )

        right_block_counterimage = set()
        for edge in graph.edges:
            if edge[1] in list(map(lambda vertex: vertex.label, qblock.vertexes)):
                right_block_counterimage.add(edge[0])

        assert right_block_counterimage == block_counterimage


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_build_block_counterimage_aux_count(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)

    for chosen_index in range(len(initial_partition)):
        qblock = q_partition[chosen_index]

        block_counterimage = build_block_counterimage(qblock)

        right_count = [0 for vertex in block_counterimage]
        for edge in graph.edges:
            if edge[1] in list(map(lambda vertex: vertex.label, qblock.vertexes)):
                # update the count for edge[0]
                for idx in range(len(block_counterimage)):
                    if block_counterimage[idx].label == edge[0]:
                        right_count[idx] += 1

        assert right_count == [vertex.aux_count.value for vertex in block_counterimage]

        for vertex in block_counterimage:
            vertex.aux_count = None


# error "dllistnode belongs to another list" triggered by split when using the result of build_block_counterimage
# error "dllistnode doesn't belong to a list"
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_vertex_taken_from_right_list(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)

    block_counterimage = build_block_counterimage(q_partition[0])

    for vertex in block_counterimage:
        qblock = vertex.qblock
        # this shouldn't raise an exception
        qblock.remove_vertex(vertex)
        assert True


# error "dllistnode belongs to another list" triggered by split when using the result of build_block_counterimage
# error "dllistnode doesn't belong to a list"
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_can_remove_any_vertex_from_its_list(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)

    for qblock in q_partition:
        vertex = qblock.vertexes.first
        while vertex != None:
            qblock.vertexes.remove(vertex)
            vertex = vertex.next
            # check that this doesn't raise an exception
            assert True


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_split(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    qblock_splitter = q_partition[0]
    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = build_block_counterimage(qblock_splitter)
    split(block_counterimage)

    # after split the partition should be stable with respect to the block chosen for the split
    for qblock in xblock.qblocks:
        assert check_block_stability(
            [vertex for vertex in qblock.vertexes], splitter_vertexes
        )

    # test if the size of the qblocks after the split is equal to the number of vertexes
    for qblock in xblock.qblocks:
        assert qblock.size == len(qblock.vertexes)

    # check if the qblock a vertex belongs to corresponds to the value vertex.qblock for each of its vertexes
    for qblock in xblock.qblocks:
        for vertex in qblock.vertexes:
            assert vertex.qblock == qblock


# check if the new blocks are in the right xblock after a call to split
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_split_helper_block_right_xblock(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)
    (new_blocks, _) = split(vertexes[3:7])

    for new_block in new_blocks:
        assert any([qblock == new_block for qblock in new_block.xblock.qblocks])

    for old_block in q_partition:
        assert old_block.size == 0 or any(
            [qblock == old_block for qblock in old_block.xblock.qblocks]
        )


# second_splitter should be E^{-1}(B) - E^{-1}(S-B), namely there should only be vertexes in E^{-1}(B) but not in E^{-1}(S-B)
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_second_splitter_counterimage(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    qblock_splitter = q_partition[0]

    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = build_block_counterimage(qblock_splitter)
    split(block_counterimage)

    # compute S - B
    second_splitter_s_minus_b_vertexes = list(
        filter(lambda vertex: vertex not in splitter_vertexes, vertexes)
    )

    # use the pta function to compute E^{-1}(B) - E^{-1}(S-B)
    second_splitter_counterimage = build_exclusive_B_counterimage(splitter_vertexes)

    for vertex in second_splitter_counterimage:
        assert vertex in block_counterimage and not any(
            map(lambda edge: edge in second_splitter_s_minus_b_vertexes, vertex.image)
        )


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_second_split(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    qblock_splitter = q_partition[0]
    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = build_block_counterimage(qblock_splitter)
    split(block_counterimage)

    second_splitter_vertexes = list(
        filter(lambda vertex: vertex not in splitter_vertexes, vertexes)
    )
    # E^{-1}(B) - E^{-1}(S-B)
    second_splitter_counterimage = build_exclusive_B_counterimage(splitter_vertexes)

    split(second_splitter_counterimage)

    # after split the partition should be stable with respect to the block chosen for the split
    for qblock in xblock.qblocks:
        assert check_block_stability(
            [vertex for vertex in qblock.vertexes], second_splitter_vertexes
        )


# a refinement step should increase by one the number of xblocks
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_increase_n_of_xblocks_after_refinement(graph, initial_partition):
    (q_partition, vertexes_dllistobejct) = initialize(
        graph, initial_partition
    )

    xblock = q_partition[0].xblock

    xblocks = [xblock]
    compound_xblocks = [xblock]

    qblock_splitter = q_partition[0]
    block_counterimage = build_block_counterimage(qblock_splitter)
    refine(xblocks=xblocks, compound_xblocks=compound_xblocks)

    assert len(xblocks) == 2


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_reset_aux_count_after_refinement(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    refine([xblock], [xblock])

    for vertex in vertexes:
        assert vertex.aux_count == None


def test_count_after_refinement():
    graph = nx.DiGraph()
    graph.add_edges_from(
        [(0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 0), (3, 2), (4, 1), (4, 3)]
    )
    graph.add_nodes_from(range(5))
    initial_partition = test_cases.initial_partitions[len(graph.nodes)]

    (q_partition, vertexes) = initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    xblocks = [xblock]

    refine(xblocks=xblocks, compound_xblocks=[xblock])

    ok_count = [[0 for _ in vertexes] for _ in xblocks]
    for (xblock_idx, xblock) in enumerate(xblocks):
        for qblock in xblock.qblocks:
            for vertex in qblock.vertexes:
                for source in [edge.source for edge in vertex.counterimage]:
                    ok_count[xblock_idx][source.label] += 1

    def xblock_index(xblock):
        for idx in range(len(xblocks)):
            if xblocks[idx] == xblock:
                return idx

    for vertex in vertexes:
        for edge in vertex.image:
            assert (
                ok_count[xblock_index(edge.destination.qblock.xblock)][vertex.label]
                == edge.count.value
            )


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_no_negative_edge_counts(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    refine([xblock], [xblock])

    for vertex in vertexes:
        for edge in vertex.image:
            assert edge.count == None or edge.count.value > 0


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_refine_updates_compound_xblocks(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)

    x_partition = [q_partition[0].xblock]
    compound_xblocks = [x_partition[0]]

    refine(compound_xblocks=compound_xblocks, xblocks=x_partition)

    for xblock in x_partition:
        if len(xblock.qblocks) > 1:
            assert xblock in compound_xblocks


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_pta_result_is_stable_partition(graph, initial_partition):
    (q_partition, vertexes) = initialize(graph, initial_partition)
    result = pta(q_partition)
    assert is_stable_partition(
        [[vertexes[vertex_idx] for vertex_idx in block] for block in result]
    )


@pytest.mark.parametrize(
    "graph, initial_partition, expected_q_partition",
    test_cases.graph_partition_rscp_tuples,
)
def test_pta_correctness(graph, initial_partition, expected_q_partition):
    rscp = evaluate_rscp(graph, initial_partition)
    assert set(rscp) == set(expected_q_partition)


def test_pta_no_initial_partition():
    graph = test_cases.build_full_graphs(10)
    rscp = evaluate_rscp(graph)
    assert True


def test_pta_no_integer_nodes():
    graph = nx.DiGraph()
    graph.add_nodes_from(["a", 0, 1, 2, 3, frozenset("x")])
    graph.add_edges_from([("a", 0), (0, 1), (1, 2), (2, 3)])
    rscp = evaluate_rscp(graph, [["a", 0, 1, 2], [3, frozenset("x")]])
    assert set(rscp) == set([("a",), (0,), (1,), (2,), (3, frozenset("x"))])


def test_no_compound_xblocks():
    G = nx.DiGraph()
    G.add_edges_from([[0, 1], [1, 2], [2, 1]])
    assert len(evaluate_rscp(G)) == 1

def test_integer_graph():
    nodes = [0, 1, 2, 'a', 'b', frozenset([5]), None, nx.DiGraph()]

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
    g2.add_nodes_from(['a', 0, 2, 3, 4])
    assert not check_normal_integer_graph(g2)

    # 3
    g3 = nx.DiGraph()
    g3.add_nodes_from([0, 1, 2, 3, 4])
    assert check_normal_integer_graph(g3)

    # 4
    g4 = nx.DiGraph()
    g4.add_nodes_from([0, 2, 3, 4])
    assert not check_normal_integer_graph(g4)
