from typing import Iterable
from llist import dllist, dllistnode

class _Vertex:
    """Represents a vertex of the input graph. The representation holds some key attributes used by the algorithm (O(1) access).

    Attributes:
        rank:          The rank of this vertex
        counterimage:  A such that A -> self
        image: A such that self -> A
        collapsed_to: If this vertex was collapsed, this is a reference to the _Vertex object it was collapsed to
    """

    def __init__(
        self, rank: int
    ):
        self.rank = rank
        self.counterimage = []
        self.image = []

        self.collapsed_to = None
        self.block = None
        self.dllistnode = None

    def append_to_image(self, vertex: _Vertex):
        self.image.append(vertex)

    def append_to_counterimage(self, vertex: _Vertex):
        self.counterimage.append(vertex)

class _Block:
    def __init__(self, rank: int, vertexes = []):
        self.vertexes = dllist(vertexes)
        self.aux_block = None

        self.visited = False

        self.rank = rank

    def visit(self):
        self.visited = True

    def release(self):
        self.visited = False

    def size(self) -> int:
        return len(self.vertexes)

    def append_vertex(self, vertex: _Vertex):
        vertex.block = self
        vertex.dllistnode = self.vertexes.append(vertex)

    def remove_vertex(self, vertex: _Vertex):
        vertex.block = None
        self.vertexes.remove(vertex.dllistnode)
