import pytest
import networkx as nx
import pta
from llist import dllist, dllistnode


def test_preprocess():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    vertexes = pta.parse_graph(graph)
    processed_partition = pta.preprocess_initial_partition(vertexes, initial_partition)

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


def test_initialize_invalid_initial_partition():
    with pytest.raises(Exception):
        graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
        initial_partition = set(
            [
                frozenset([0, 3, 4]),
                frozenset([1, 2, 9]),
                frozenset([8, 5]),
                frozenset([7]),
                frozenset([6, 1]),
            ]
        )

        (q_partition, _) = pta.initialize(graph, initial_partition)

    with pytest.raises(Exception):
        graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
        initial_partition = set(
            [
                frozenset([0, 3, 4]),
                frozenset([1, 2, 9]),
                frozenset([8, 5]),
                frozenset([7]),
            ]
        )

        (q_partition, _) = pta.initialize(graph, initial_partition)


def test_qpartition_initialize():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)

    vertexes = set()
    for qblock in q_partition:
        vertexes.update(qblock.vertexes)

    assert set(map(lambda vertex: vertex.label, vertexes)) == set(
        [idx for idx, _ in enumerate(graph.nodes)]
    )


def test_initialize_right_types():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)

    for qblock in q_partition:
        assert isinstance(qblock.vertexes, dllist)

    for qblock in q_partition:
        for vertex in qblock.vertexes:
            for v in vertex.image:
                assert isinstance(v, pta.Edge)
            for v in vertex.counterimage:
                assert isinstance(v, pta.Edge)
            assert isinstance(vertex.qblock, pta.QBlock)


def test_count_initialize():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (_, vertexes) = pta.initialize(graph, initial_partition)

    for vertex in vertexes:
        for edge in vertex.image:
            assert edge.count.value == len(vertex.image)


def test_vertex_image_initialize():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, vertexes) = pta.initialize(graph, initial_partition)

    right_image = [set() for node in graph.nodes]
    for edge in graph.edges:
        right_image[edge[0]].add(pta.Edge(vertexes[edge[0]], vertexes[edge[1]]))

    for block in q_partition:
        for vertex in block.vertexes:
            vertex_image = set(vertex.image)
            assert vertex_image == right_image[vertex.label]


# test if initialize computed the vertexes counterimages properly
def test_vertex_counterimage_initialize():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, vertexes) = pta.initialize(graph, initial_partition)

    right_counterimage = [set() for node in graph.nodes]
    for edge in graph.edges:
        right_counterimage[edge[1]].add(pta.Edge(vertexes[edge[0]], vertexes[edge[1]]))

    for block in q_partition:
        for vertex in block.vertexes:
            vertex_counterimage = set(vertex.counterimage)
            assert vertex_counterimage == right_counterimage[vertex.label]


def test_choose_qblock():
    compoundblock = pta.XBlock()
    qblocks = [
        pta.QBlock([0, 3, 5], compoundblock),
        pta.QBlock([2, 4], compoundblock),
        pta.QBlock([1, 6, 8], compoundblock),
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


def test_build_block_counterimage():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)

    for qblock in q_partition:
        def extract_vertex_label(llistobject):
            return llistobject.label

        block_counterimage = set(
            [
                vertex.label
                for vertex in pta.build_block_counterimage(qblock)
            ]
        )

        right_block_counterimage = set()
        for edge in graph.edges:
            if edge[1] in list(map(lambda vertex: vertex.label, qblock.vertexes)):
                right_block_counterimage.add(edge[0])

        assert right_block_counterimage == block_counterimage


def test_build_block_counterimage_aux_count():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)

    for chosen_index in range(4):
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
def test_vertex_taken_from_right_list():
    for i in range(10):
        graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
        initial_partition = set(
            [
                frozenset([0, 3, 4]),
                frozenset([1, 2, 9]),
                frozenset([8, 5]),
                frozenset([7]),
                frozenset([6]),
            ]
        )

        (q_partition, _) = pta.initialize(graph, initial_partition)

        block_counterimage = pta.build_block_counterimage(q_partition[0])

        for vertex in block_counterimage:
            qblock = vertex.qblock
            # this shouldn't raise an exception
            qblock.remove_vertex(vertex)
            assert True


# error "dllistnode belongs to another list" triggered by split when using the result of build_block_counterimage
# error "dllistnode doesn't belong to a list"
def test_can_remove_any_vertex_from_its_list():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)

    for qblock in q_partition:
        vertex = qblock.vertexes.first
        while vertex != None:
            qblock.vertexes.remove(vertex)
            vertex = vertex.next
            assert True

    # ------
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)
    block_counterimage = pta.build_block_counterimage(q_partition[0])

    for qblock in q_partition:
        vertex = qblock.vertexes.first
        while vertex != None:
            qblock.vertexes.remove(vertex)
            vertex = vertex.next
            assert True

    # -----
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)
    block_counterimage = pta.build_block_counterimage(q_partition[0])
    pta.split(block_counterimage)

    for qblock in q_partition:
        vertex = qblock.vertexes.first
        while vertex != None:
            qblock.vertexes.remove(vertex)
            vertex = vertex.next
            assert True


def test_check_block_stability():
    # this is a stable couple: E(A) is a subset of B
    A_vertexes = [pta.Vertex(i) for i in range(3)]
    B_vertexes = [pta.Vertex(i) for i in range(3, 7)]

    A_block = pta.QBlock(A_vertexes, None)
    B_block = pta.QBlock(B_vertexes, None)

    for i in range(len(A_vertexes)):
        A_vertexes[i].add_to_image(
            pta.Edge(A_block.vertexes.nodeat(i).value, B_block.vertexes.nodeat(i).value)
        )
    assert pta.check_block_stability(
        [vertex for vertex in A_block.vertexes],
        [vertex for vertex in B_block.vertexes],
    )

    # this is a stable couple: the intersection of E(A) and B is empty
    A_vertexes = [pta.Vertex(i) for i in range(3)]
    B_vertexes = [pta.Vertex(i) for i in range(3, 7)]
    C_vertexes = [pta.Vertex(i) for i in range(3)]

    A_block = pta.QBlock(A_vertexes, None)
    B_block = pta.QBlock(B_vertexes, None)
    C_block = pta.QBlock(C_vertexes, None)

    for i in range(len(A_vertexes)):
        A_vertexes[i].add_to_image(
            pta.Edge(A_block.vertexes.nodeat(i).value, C_block.vertexes.nodeat(i).value)
        )
    assert pta.check_block_stability(
        [vertex for vertex in A_block.vertexes],
        [vertex for vertex in B_block.vertexes],
    )

    # this is a non-stable couple
    A_vertexes = [pta.Vertex(i) for i in range(3)]
    B_vertexes = [pta.Vertex(i) for i in range(3, 7)]

    A_block = pta.QBlock(A_vertexes, None)
    B_block = pta.QBlock(B_vertexes, None)

    for i in range(1, len(A_vertexes)):
        A_vertexes[i].add_to_image(
            pta.Edge(A_block.vertexes.nodeat(i).value, B_block.vertexes.nodeat(i).value)
        )

    # this is the edge which will fail the stability check
    A_vertexes[0].add_to_image(
        pta.Edge(A_block.vertexes.nodeat(0).value, A_block.vertexes.nodeat(1).value)
    )

    assert not pta.check_block_stability(
        [vertex for vertex in A_block.vertexes],
        [vertex for vertex in B_block.vertexes],
    )


def test_split():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, _) = pta.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    qblock_splitter = q_partition[0]
    # qblock_splitter may be modified by split, therefore we need to keep a copy
    splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

    block_counterimage = pta.build_block_counterimage(qblock_splitter)
    pta.split(block_counterimage)

    # after split the partition should be stable with respect to the block chosen for the split
    for qblock in xblock.qblocks:
        assert pta.check_block_stability(
            [vertex for vertex in qblock.vertexes], splitter_vertexes
        )

    # test if the size of the qblocks after the split is equal to the number of vertexes
    for qblock in xblock.qblocks:
        assert qblock.size == len(qblock.vertexes)

    # check if the qblock a vertex belongs to corresponds to the value vertex.qblock for each of its vertexes
    for qblock in xblock.qblocks:
        for vertex in qblock.vertexes:
            assert vertex.qblock == qblock


# second_splitter should be E^{-1}(B) - E^{-1}(S-B), namely there should only be vertexes in E^{-1}(B) but not in E^{-1}(S-B)
def test_second_splitter_counterimage():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, vertexes) = pta.initialize(graph, initial_partition)

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
    second_splitter_counterimage = pta.build_second_splitter_counterimage(
        splitter_vertexes
    )

    for vertex in second_splitter_counterimage:
        assert vertex in block_counterimage and not any(
            map(lambda edge: edge in second_splitter_s_minus_b_vertexes, vertex.image)
        )


def test_second_split():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, vertexes) = pta.initialize(graph, initial_partition)

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
    second_splitter_counterimage = pta.build_second_splitter_counterimage(
        splitter_vertexes
    )

    pta.split(second_splitter_counterimage)

    # after split the partition should be stable with respect to the block chosen for the split
    for qblock in xblock.qblocks:
        assert pta.check_block_stability(
            [vertex for vertex in qblock.vertexes], second_splitter_vertexes
        )


# a refinement step should increase by one the number of xblocks
def test_increase_n_of_xblocks_after_refinement():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, vertexes_dllistobejct) = pta.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock

    xblocks = [xblock]
    compound_xblocks = [xblock]

    qblock_splitter = q_partition[0]
    block_counterimage = pta.build_block_counterimage(qblock_splitter)
    pta.refine(xblocks, xblocks)

    assert len(xblocks) == 2


def test_reset_aux_count_after_refinement():
    graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
    initial_partition = set(
        [
            frozenset([0, 3, 4]),
            frozenset([1, 2, 9]),
            frozenset([8, 5]),
            frozenset([7]),
            frozenset([6]),
        ]
    )

    (q_partition, vertexes) = pta.initialize(graph, initial_partition)

    xblock = q_partition[0].xblock
    pta.refine([xblock], [xblock])

    for vertex in vertexes:
        assert vertex.aux_count == None
