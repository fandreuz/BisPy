from unittest import TestCase
import unittest
import networkx as nx
import pta
from llist import dllist, dllistnode
from networkx.drawing.nx_agraph import to_agraph
import matplotlib.pyplot as plt


def draw(graph, file_name):
    for node in graph.nodes:
        graph.nodes[node]["height"] = 0.1
        graph.nodes[node]["shape"] = "circle"

        graph.nodes[node]["width"] = 0.3
        graph.nodes[node]["height"] = 0.3
        graph.nodes[node]["fixedsize"] = True
        graph.nodes[node]["fontsize"] = 6

    for edge in graph.edges:
        graph.edges[edge]["arrowsize"] = 0.2

    A = to_agraph(graph)
    A.layout("sfdp")
    A.graph_attr["nodesep"] = 1
    A.graph_attr["dpi"] = 300
    A.graph_attr["height"] = 500
    A.draw("{}.png".format(file_name))


class TestFBADataStructures(TestCase):
    def test_qpartition(self):
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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        vertexes = set()
        for qblock in q_partition:
            vertexes.update(qblock.vertexes)

        self.assertEqual(
            set(map(lambda vertex: vertex.label, vertexes)),
            set([idx for idx, _ in enumerate(graph.nodes)]),
            "q_partition is a proper partition of V",
        )

    def test_parse_right_types(self):
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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        for qblock in q_partition:
            self.assertEqual(type(qblock.vertexes), dllist)

        for qblock in q_partition:
            for vertex in qblock.vertexes:
                for v in vertex.image:
                    self.assertEqual(type(v), pta.Edge)
                for v in vertex.counterimage:
                    self.assertEqual(type(v), pta.Edge)
                self.assertEqual(type(vertex.qblock), dllistnode)

    # test if parse_graph computed the vertexes counterimages properly
    def test_vertex_counterimage(self):
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

        (q_partition, vertexes_dllistnode) = pta.parse_graph(graph, initial_partition)

        right_counterimage = [set() for node in graph.nodes]
        for edge in graph.edges:
            right_counterimage[edge[1]].add(
                pta.Edge(vertexes_dllistnode[edge[0]], vertexes_dllistnode[edge[1]])
            )

        for block in q_partition:
            for vertex in block.vertexes:
                vertex_counterimage = set(vertex.counterimage)

                print(vertex_counterimage)
                print(right_counterimage[vertex.label])

                self.assertEqual(
                    vertex_counterimage,
                    right_counterimage[vertex.label],
                    "the counter image of {} is fine".format(vertex.label),
                )

    def test_count(self):
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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        """ image = [set() for node in graph.nodes]
        for edge in graph.edges:
            image[edge[0]].add(edge[1])

        for block in q_partition:
            for vertex in block.vertexes:
                vertex_image = set(map(lambda source: source.value.label, vertex.image))

                self.assertEqual(vertex_image, image[vertex.label], 'the initial count of (X \cap E({})) is fine'.format(vertex.label)) """

    def test_choose_qblock(self):
        compoundblock = pta.XBlock(0)
        qblocks = [
            pta.QBlock([0, 3, 5], compoundblock),
            pta.QBlock([2, 4], compoundblock),
            pta.QBlock([1, 6, 8], compoundblock),
        ]
        for qblock in qblocks:
            compoundblock.append_qblock(qblock)

        splitter = pta.extract_splitter(compoundblock)
        self.assertEqual(splitter, qblocks[1], "the right qblock has been chosen")

        # check if compound block has been modified properly
        self.assertEqual(
            compoundblock.qblocks.size,
            2,
            "an item has been deleted from XBlock.qblocks",
        )

        compoundblock_qblocks = set()
        for i in range(2):
            compoundblock_qblocks.add(compoundblock.qblocks.nodeat(i).value)
        self.assertEqual(
            compoundblock_qblocks,
            set([qblocks[0], qblocks[2]]),
            "the right item has been deleted from XBlock.qblocks",
        )

    def test_build_block_counterimage(self):
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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        for chosen_index in range(4):
            chosen_qblock_frozenset = list(initial_partition)[chosen_index]

            def extract_vertex_label(llistobject):
                return llistobject.value.label

            block_counterimage = set(
                map(
                    extract_vertex_label,
                    pta.build_block_counterimage(q_partition[chosen_index]),
                )
            )

            right_block_counterimage = set()
            for edge in graph.edges:
                if edge[1] in chosen_qblock_frozenset:
                    right_block_counterimage.add(edge[0])

            self.assertEqual(
                right_block_counterimage,
                block_counterimage,
                "the counterimage of the block was calculated properly",
            )

    # check if the returned value is [|chosen_qblock \cap E({x})|, x \in V]
    def test_build_block_counterimage_count(self):
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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        """ for chosen_index in range(4):
            chosen_qblock_frozenset = list(initial_partition)[chosen_index]

            # this should contain, for each vertex x in the graph, the number of vertexes y such that (y \in B, x -> y)
            count_line = pta.build_block_counterimage(q_partition[chosen_index])[1]

            right_count_line = [0 for i in range(len(graph.nodes))]
            for edge in graph.edges:
                if edge[1] in chosen_qblock_frozenset:
                    right_count_line[edge[0]] += 1

            self.assertEqual(right_count_line, count_line, 'count line calcolata correttamente') """

    # error "dllistnode belongs to another list" triggered by split when using the result of build_block_counterimage
    # error "dllistnode doesn't belong to a list"
    def test_vertex_taken_from_right_list(self):
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

            (q_partition, _) = pta.parse_graph(graph, initial_partition)

            block_counterimage = pta.build_block_counterimage(q_partition[0])

            for vertex in block_counterimage:
                qblock = vertex.value.qblock
                # this shouldn't raise an exception
                qblock.value.remove_vertex(vertex)

    # error "dllistnode belongs to another list" triggered by split when using the result of build_block_counterimage
    # error "dllistnode doesn't belong to a list"
    def test_can_remove_any_vertex_from_its_list(self):
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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        for qblock in q_partition:
            vertex = qblock.vertexes.first
            while vertex != None:
                qblock.vertexes.remove(vertex)
                vertex = vertex.next

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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)
        block_counterimage = pta.build_block_counterimage(q_partition[0])

        for qblock in q_partition:
            vertex = qblock.vertexes.first
            while vertex != None:
                qblock.vertexes.remove(vertex)
                vertex = vertex.next

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

        (q_partition, _) = pta.parse_graph(graph, initial_partition)
        block_counterimage = pta.build_block_counterimage(q_partition[0])
        pta.split(block_counterimage)

        for qblock in q_partition:
            vertex = qblock.vertexes.first
            while vertex != None:
                qblock.vertexes.remove(vertex)
                vertex = vertex.next

    def test_check_block_stability(self):
        # this is a stable couple: E(A) is a subset of B
        A_vertexes = [pta.Vertex(i) for i in range(3)]
        B_vertexes = [pta.Vertex(i) for i in range(3, 7)]

        A_block = pta.QBlock(A_vertexes, None)
        B_block = pta.QBlock(B_vertexes, None)

        for i in range(len(A_vertexes)):
            A_vertexes[i].add_to_image(
                pta.Edge(A_block.vertexes.nodeat(i), B_block.vertexes.nodeat(i))
            )
        self.assertTrue(
            pta.check_block_stability(
                [vertex for vertex in A_block.vertexes],
                [vertex for vertex in B_block.vertexes],
            )
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
                pta.Edge(A_block.vertexes.nodeat(i), C_block.vertexes.nodeat(i))
            )
        self.assertTrue(
            pta.check_block_stability(
                [vertex for vertex in A_block.vertexes],
                [vertex for vertex in B_block.vertexes],
            )
        )

        # this is a non-stable couple
        A_vertexes = [pta.Vertex(i) for i in range(3)]
        B_vertexes = [pta.Vertex(i) for i in range(3, 7)]

        A_block = pta.QBlock(A_vertexes, None)
        B_block = pta.QBlock(B_vertexes, None)

        for i in range(1,len(A_vertexes)):
            A_vertexes[i].add_to_image(
                pta.Edge(A_block.vertexes.nodeat(i), B_block.vertexes.nodeat(i))
            )

        # this is the edge which will fail the stability check
        A_vertexes[0].add_to_image(
            pta.Edge(A_block.vertexes.nodeat(0), A_block.vertexes.nodeat(1))
        )

        self.assertFalse(
            pta.check_block_stability(
                [vertex for vertex in A_block.vertexes],
                [vertex for vertex in B_block.vertexes],
            )
        )

    def test_split(self):
        graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
        draw(graph, 'graph')
        initial_partition = set(
            [
                frozenset([0, 3, 4]),
                frozenset([1, 2, 9]),
                frozenset([8, 5]),
                frozenset([7]),
                frozenset([6]),
            ]
        )

        (q_partition, _) = pta.parse_graph(graph, initial_partition)

        xblock = q_partition[0].xblock

        qblock_splitter = q_partition[0]
        # qblock_splitter may be modified by split, therefore we need to keep a copy
        splitter_vertexes = [vertex for vertex in qblock_splitter.vertexes]

        block_counterimage = pta.build_block_counterimage(qblock_splitter)
        pta.split(block_counterimage)

        # after split the partition should be stable with respect to the block chosen for the split
        for qblock in xblock.qblocks:
            self.assertTrue(
                pta.check_block_stability(
                    [vertex for vertex in qblock.vertexes], splitter_vertexes
                )
            )


if __name__ == "__main__":
    unittest.main()
