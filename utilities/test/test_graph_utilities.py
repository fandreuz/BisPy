import sys
from pathlib import Path
sys.path.append("{}/utilities/".format(Path(__file__).parent.parent.parent))

from graph_utilities import *
from graph_entities import *

def test_check_block_stability():
    # this is a stable couple: E(A) is a subset of B
    A_vertexes = [Vertex(i) for i in range(3)]
    B_vertexes = [Vertex(i) for i in range(3, 7)]

    A_block = QBlock(A_vertexes, None)
    B_block = QBlock(B_vertexes, None)

    for i in range(len(A_vertexes)):
        A_vertexes[i].add_to_image(
            Edge(A_block.vertexes.nodeat(i).value, B_block.vertexes.nodeat(i).value)
        )
    assert check_block_stability(
        [vertex for vertex in A_block.vertexes],
        [vertex for vertex in B_block.vertexes],
    )

    # this is a stable couple: the intersection of E(A) and B is empty
    A_vertexes = [Vertex(i) for i in range(3)]
    B_vertexes = [Vertex(i) for i in range(3, 7)]
    C_vertexes = [Vertex(i) for i in range(3)]

    A_block = QBlock(A_vertexes, None)
    B_block = QBlock(B_vertexes, None)
    C_block = QBlock(C_vertexes, None)

    for i in range(len(A_vertexes)):
        A_vertexes[i].add_to_image(
            Edge(A_block.vertexes.nodeat(i).value, C_block.vertexes.nodeat(i).value)
        )
    assert check_block_stability(
        [vertex for vertex in A_block.vertexes],
        [vertex for vertex in B_block.vertexes],
    )

    # this is a non-stable couple
    A_vertexes = [Vertex(i) for i in range(3)]
    B_vertexes = [Vertex(i) for i in range(3, 7)]

    A_block = QBlock(A_vertexes, None)
    B_block = QBlock(B_vertexes, None)

    for i in range(1, len(A_vertexes)):
        A_vertexes[i].add_to_image(
            Edge(A_block.vertexes.nodeat(i).value, B_block.vertexes.nodeat(i).value)
        )

    # this is the edge which will fail the stability check
    A_vertexes[0].add_to_image(
        Edge(A_block.vertexes.nodeat(0).value, A_block.vertexes.nodeat(1).value)
    )

    assert not check_block_stability(
        [vertex for vertex in A_block.vertexes],
        [vertex for vertex in B_block.vertexes],
    )
