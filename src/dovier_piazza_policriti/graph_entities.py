from typing import Iterable


class _Vertex:
    """Represents a vertex of the input graph. The representation holds some key attributes used by the algorithm (O(1) access).

    Attributes:
        rank:          The rank of this vertex
        counterimage:  A such that A -> self
        image: A such that self -> A
        collapsed_to: If this vertex was collapsed, this is a reference to the _Vertex object it was collapsed to
    """

    def __init__(
        self, rank: int, neighborhoods: Iterable[Vertex], image: Iterable[Vertex]
    ):
        self.rank = rank
        self.counterimage = counterimage
        self.image = image

        self.collapsed_to = None
