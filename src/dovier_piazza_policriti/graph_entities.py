from typing import Iterable

class Vertex:
    """Represents a vertex of the input graph. The representation holds some key attributes used by the algorithm (O(1) access).

    Attributes:
        rank:          The rank of this vertex
        counterimage:  A such that A -> self
        neighborhoods: A such that self -> A
    """

    def __init__(self, rank: int, neighborhoods: Iterable[Vertex], counterimage: Iterable[Vertex]):
        self.rank = rank
        self.counterimage = counterimage
        self.neighborhoods = neighborhoods
