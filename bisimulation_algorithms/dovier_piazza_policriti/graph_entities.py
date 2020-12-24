from typing import Iterable
from llist import dllist, dllistnode


class _Vertex:
    """Represents a vertex of the input graph. The representation holds some
    key attributes used by the algorithm (O(1) access).

    Attributes:
        rank:              The rank of this vertex
        counterimage:      Every A such that A -> self
        image:             Every A such that self -> A
        label:             The (integer) label of this vertex.
        block:             The block this vertex belongs to.
    """

    def __init__(self, rank: int, label: int):
        self.label = label

        self.rank = rank

        self.counterimage = []
        self.image = []

        self.block = None
        self._block_dllistnode = None

        self.visited = False

    def append_to_image(self, vertex):
        self.image.append(vertex)

    def append_to_counterimage(self, vertex):
        self.counterimage.append(vertex)

    def visit(self):
        self.visited = True

    def release(self):
        self.visited = False

    def __str__(self):
        return str(self.label)

    def __repr__(self):
        return str(self.label)

    # this is only used for testing purposes
    def __hash__(self):
        return self.label

    def __eq__(self, other):
        return isinstance(other, _Vertex) and self.label == other.label

    def __ne__(self, other):
        return not self.__eq__(other)


class _Block:
    def __init__(self, rank: int, vertexes=[]):
        self.vertexes = dllist(vertexes)
        self.aux_block = None

        self.rank = rank

    def size(self) -> int:
        return len(self.vertexes)

    def append_vertex(self, vertex: _Vertex):
        vertex.block = self
        vertex.dllistnode = self.vertexes.append(vertex)

    def remove_vertex(self, vertex: _Vertex):
        vertex.block = None
        self.vertexes.remove(vertex.dllistnode)
