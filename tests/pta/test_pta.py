import pytest
import networkx as nx
from llist import dllist, dllistnode
import pta_test_cases as test_cases
import itertools

import utilities.rscp_utilities as rscp_utilities

import paige_tarjan.graph_entities as entities
import paige_tarjan.pta as pta
import paige_tarjan.graph_decorator as decorator
import paige_tarjan.pta_algorithm as pta_algorithm


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_preprocess(graph, initial_partition):
    vertexes = decorator.prepare_graph_abstraction(graph)
    processed_partition = decorator.preprocess_initial_partition(vertexes, initial_partition)

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
    (q_partition, _) = decorator.initialize(graph, initial_partition)

    vertexes = set()
    for qblock in q_partition:
        vertexes.update(qblock.vertexes)

    assert set(map(lambda vertex: vertex.label, vertexes)) == set(
        [idx for idx, _ in enumerate(graph.nodes)]
    )

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_initialize_right_types(graph, initial_partition):
    (q_partition, _) = decorator.initialize(graph, initial_partition)

    for qblock in q_partition:
        assert isinstance(qblock.vertexes, dllist)

    for qblock in q_partition:
        for vertex in qblock.vertexes:
            for v in vertex.image:
                assert isinstance(v, entities._Edge)
            for v in vertex.counterimage:
                assert isinstance(v, entities._Edge)
            assert isinstance(vertex.qblock, entities._QBlock)

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_count_initialize(graph, initial_partition):
    (_, vertexes) = decorator.initialize(graph, initial_partition)

    for vertex in vertexes:
        for edge in vertex.image:
            assert edge.count.value == len(vertex.image)

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_vertex_image_initialize(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    right_image = [set() for node in graph.nodes]
    for edge in graph.edges:
        right_image[edge[0]].add(entities._Edge(vertexes[edge[0]], vertexes[edge[1]]))

    for block in q_partition:
        for vertex in block.vertexes:
            vertex_image = set(vertex.image)
            assert vertex_image == right_image[vertex.label]


# test if decorator.initialize computed the vertexes counterimages properly
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_vertex_counterimage_initialize(graph, initial_partition):

    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    right_counterimage = [set() for node in graph.nodes]
    for edge in graph.edges:
        right_counterimage[edge[1]].add(entities._Edge(vertexes[edge[0]], vertexes[edge[1]]))

    for block in q_partition:
        for vertex in block.vertexes:
            vertex_counterimage = set(vertex.counterimage)
            assert vertex_counterimage == right_counterimage[vertex.label]


def test_choose_qblock():
    compoundblock = entities._XBlock()
    qblocks = [
        entities._QBlock([0, 3, 5], compoundblock),
        entities._QBlock([2, 4], compoundblock),
        entities._QBlock([1, 6, 8], compoundblock),
    ]
    for qblock in qblocks:
        compoundblock.append_qblock(qblock)

    splitter = pta.extract_splitter(compoundblock)
    assert splitter == qblocks[1]

    # check if compound block has been modified properly
    assert compoundblock.qblocks.size == 2

    compoundblock_qblocks = set()
    for i in range(2):
        compoundblock_qblocks.add(compoundblock.qblocks.nodeat(i).value)
    assert compoundblock_qblocks == set([qblocks[0], qblocks[2]])

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_build_block_counterimage(graph, initial_partition):
    (q_partition, _) = decorator.initialize(graph, initial_partition)
    for qblock in q_partition:

        def extract_vertex_label(llistobject):
            return llistobject.label

        block_counterimage = set(
            [vertex.label for vertex in pta.build_block_counterimage(qblock)]
        )

        right_block_counterimage = set()
        for edge in graph.edges:
            if edge[1] in list(map(lambda vertex: vertex.label, qblock.vertexes)):
                right_block_counterimage.add(edge[0])

        assert right_block_counterimage == block_counterimage

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_build_block_counterimage_aux_count(graph, initial_partition):
    (q_partition, _) = decorator.initialize(graph, initial_partition)

    for chosen_index in range(len(initial_partition)):
        qblock = q_partition[chosen_index]

        block_counterimage = pta.build_block_counterimage(qblock)

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
    (q_partition, _) = decorator.initialize(graph, initial_partition)

    block_counterimage = pta.build_block_counterimage(q_partition[0])

    for vertex in block_counterimage:
        qblock = vertex.qblock
        # this shouldn't raise an exception
        qblock.remove_vertex(vertex)
        assert True


# error "dllistnode belongs to another list" triggered by split when using the result of build_block_counterimage
# error "dllistnode doesn't belong to a list"
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_can_remove_any_vertex_from_its_list(graph, initial_partition):
    (q_partition, _) = decorator.initialize(graph, initial_partition)

    for qblock in q_partition:
        vertex = qblock.vertexes.first
        while vertex != None:
            qblock.vertexes.remove(vertex)
            vertex = vertex.next
            # check that this doesn't raise an exception
            assert True

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_split(graph, initial_partition):
    (q_partition, _) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    qblock_splitter = q_partition[0]
    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = pta.build_block_counterimage(qblock_splitter)
    pta.split(block_counterimage)

    # after split the partition should be stable with respect to the block chosen for the split
    for qblock in xblock.qblocks:
        assert rscp_utilities.check_block_stability(
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
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)
    (new_blocks, _) = pta.split(vertexes[3:7])

    for new_block in new_blocks:
        assert any([qblock == new_block for qblock in new_block.xblock.qblocks])

    for old_block in q_partition:
        assert old_block.size == 0 or any(
            [qblock == old_block for qblock in old_block.xblock.qblocks]
        )


# second_splitter should be E^{-1}(B) - E^{-1}(S-B), namely there should only be vertexes in E^{-1}(B) but not in E^{-1}(S-B)
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_second_splitter_counterimage(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    qblock_splitter = q_partition[0]

    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = pta.build_block_counterimage(qblock_splitter)
    pta.split(block_counterimage)

    # compute S - B
    second_splitter_s_minus_b_vertexes = list(
        filter(lambda vertex: vertex not in splitter_vertexes, vertexes)
    )

    # use the pta function to compute E^{-1}(B) - E^{-1}(S-B)
    second_splitter_counterimage = pta.build_exclusive_B_counterimage(
        splitter_vertexes
    )

    for vertex in second_splitter_counterimage:
        assert vertex in block_counterimage and not any(
            map(lambda edge: edge in second_splitter_s_minus_b_vertexes, vertex.image)
        )

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_second_split(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    qblock_splitter = q_partition[0]
    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = pta.build_block_counterimage(qblock_splitter)
    pta.split(block_counterimage)

    second_splitter_vertexes = list(
        filter(lambda vertex: vertex not in splitter_vertexes, vertexes)
    )
    # E^{-1}(B) - E^{-1}(S-B)
    second_splitter_counterimage = pta.build_exclusive_B_counterimage(
        splitter_vertexes
    )

    pta.split(second_splitter_counterimage)

    # after split the partition should be stable with respect to the block chosen for the split
    for qblock in xblock.qblocks:
        assert rscp_utilities.check_block_stability(
            [vertex for vertex in qblock.vertexes], second_splitter_vertexes
        )


# a refinement step should increase by one the number of xblocks
@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_increase_n_of_xblocks_after_refinement(graph, initial_partition):
    (q_partition, vertexes_dllistobejct) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    xblocks = [xblock]
    compound_xblocks = [xblock]

    qblock_splitter = q_partition[0]
    block_counterimage = pta.build_block_counterimage(qblock_splitter)
    pta.refine(xblocks=xblocks, compound_xblocks=compound_xblocks)

    assert len(xblocks) == 2

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_reset_aux_count_after_refinement(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    pta.refine([xblock], [xblock])

    for vertex in vertexes:
        assert vertex.aux_count == None

def test_count_after_refinement():
    graph = nx.DiGraph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 0), (3, 2), (4, 1), (4, 3)])
    graph.add_nodes_from(range(5))
    initial_partition = test_cases.initial_partitions[len(graph.nodes)]

    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    xblocks = [xblock]

    pta.refine(xblocks=xblocks, compound_xblocks=[xblock])

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
            assert ok_count[xblock_index(edge.destination.qblock.xblock)][vertex.label] == edge.count.value


@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_no_negative_edge_counts(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    pta.refine([xblock], [xblock])

    for vertex in vertexes:
        for edge in vertex.image:
            assert edge.count == None or edge.count.value > 0

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_refine_updates_compound_xblocks(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)

    x_partition = [q_partition[0].xblock]
    compound_xblocks = [x_partition[0]]

    pta.refine(compound_xblocks=compound_xblocks, xblocks=x_partition)

    for xblock in x_partition:
        if len(xblock.qblocks) > 1:
            assert xblock in compound_xblocks

@pytest.mark.parametrize("graph, initial_partition", test_cases.graph_partition_tuples)
def test_pta_result_is_stable_partition(graph, initial_partition):
    (q_partition, vertexes) = decorator.initialize(graph, initial_partition)
    result = pta.pta(q_partition)
    assert rscp_utilities.is_stable_partition([[vertexes[vertex_idx] for vertex_idx in block] for block in result])

@pytest.mark.parametrize(
    "graph, initial_partition, expected_q_partition",
    test_cases.graph_partition_rscp_tuples,
)
def test_pta_correctness(graph, initial_partition, expected_q_partition):
    rscp = pta_algorithm.rscp(graph, initial_partition)
    assert set(rscp) == expected_q_partition

def test_pta_no_initial_partition():
    graph = test_cases.build_full_graphs(10)
    rscp = pta_algorithm.rscp(graph)
    assert True