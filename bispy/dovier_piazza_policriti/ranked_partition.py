from typing import Iterable, List, Tuple, Dict, Union
from bispy.utilities.graph_entities import (
    _QBlock as _Block,
    _Vertex,
    _XBlock
)

class RankedPartition:
    def __init__(self, vertexes: List[_Vertex]):
        max_rank = max(vertex.rank for vertex in vertexes)

        # initialize the initial partition. the first index is for -infty
        # partition contains is a list of lists, each sub-list contains the
        # sub-blocks of nodes at the i-th rank. there's an XBlock for each
        # rank.
        if max_rank != float("-inf"):
            self._partition = [[_Block([], _XBlock())]
                for i in range(max_rank + 2)]
        else:
            # there's a single possible rank, -infty
            self._partition = [[_Block([], _XBlock())]]

        # populate the blocks of the partition according to the ranks
        for vertex in vertexes:
            # put this node in the (only) list at partition_idx in partition
            # (there's only one block for each rank at the moment in the
            # partition)
            block = self._partition[
                RankedPartition.rank_to_partition_idx(vertex.rank)][0]
            block.append_vertex(vertex)

    @staticmethod
    def rank_to_partition_idx(rank: Union[int, float]) -> int:
        """Convert a rank to the corresponding index.

        :param rank: The input rank.
        """

        if rank == float("-inf"):
            return 0
        else:
            return rank + 1

    def __getitem__(self, key):
        return self._partition[key]

    def append_at_rank(self, block: _Block, rank: Union[int,float]):
        self.append_at_index(block, RankedPartition
            .rank_to_partition_idx(rank))

    def append_at_index(self, block, index: int):
        self._partition[index].append(block)

    def __len__(self):
        return len(self._partition)

    def clear_rank(self, rank: Union[int,float]):
        self.clear_index(RankedPartition.rank_to_partition_idx(rank))

    def clear_index(self, index: int):
        self._partition[index] = []

    def __iter__(self):
        return filter(lambda rank: len(rank) > 0, self._partition)
