from typing import Iterable
from llist import dllist, dllistnode
from bisimulation_algorithms.paige_tarjan.graph_entities import (
    _Vertex as pta_Vertex,
    _QBlock as pta_Block,
    _XBlock
)


class _Vertex(pta_Vertex):
    """Represents a vertex of the input graph.

    Attributes:
        rank:              The rank of this vertex
    """

    def __init__(self, label: int):
        super().__init__(label)
        self.original_label = label
        self.rank = None
        self.wf = True

    def scale_label(self, scaled_label: int):
        self.label = scaled_label

    def back_to_original_label(self):
        self.label = self.original_label

class _Block(pta_Block):
    def __init__(self, vertexes: Iterable[_Vertex], xblock: _XBlock):
        super().__init__(vertexes, xblock)

    def rank(self) -> int:
        if self.vertexes.first is not None:
            return self.vertexes.first.value.rank
        else:
            return None
