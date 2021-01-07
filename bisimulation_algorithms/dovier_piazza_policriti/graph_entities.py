from typing import Iterable
from llist import dllist, dllistnode
from bisimulation_algorithms.paige_tarjan.graph_entities import (
    _Vertex as pta_Vertex,
    _QBlock as pta_Block,
    _XBlock,
    _Count
)


class _Vertex(pta_Vertex):
    """Represents a vertex of the input graph.

    Attributes:
        rank:              The rank of this vertex
    """

    def __init__(self, label: int):
        super().__init__(label)
        self.rank = None
        self.wf = True

        self.original_label = label

    def scale_label(self, scaled_label: int):
        self.label = scaled_label

    def back_to_original_label(self):
        self.label = self.original_label

    def restrict_to_subgraph(self):
        # this will be called just before calling PTA, therefore set the _Count
        # instance for each _Edge

        img = self.image
        self.image = []

        count = _Count(self)

        for edge in img:
            if edge.destination.rank == self.rank:
                self.add_to_image(edge)

                # set the count for this _Edge, and increment the counter
                edge.count = count
                count.value += 1

        counterimg = self.counterimage
        self.counterimage = []

        for edge in counterimg:
            if edge.source.rank == self.rank:
                self.add_to_counterimage(edge)


class _Block(pta_Block):
    def __init__(self, vertexes: Iterable[_Vertex], xblock: _XBlock):
        super().__init__(vertexes, xblock)

    def rank(self) -> int:
        if self.vertexes.first is not None:
            return self.vertexes.first.value.rank
        else:
            return None
