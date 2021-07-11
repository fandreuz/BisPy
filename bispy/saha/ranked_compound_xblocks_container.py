from bispy.paige_tarjan.paige_tarjan import CompoundXBlocksContainer
from bispy.utilities.graph_entities import _XBlock
import sys


class RankedCompoundXBlocksContainer(CompoundXBlocksContainer):
    def __init__(self, compound_xblocks, max_rank):
        self._xblocks = [[] for _ in range(max_rank + 2)]

        first_nonempty_index = sys.maxsize
        if len(compound_xblocks) == 0:
            first_nonempty_index = -1

        for compound_xblock in compound_xblocks:
            rank = (
                compound_xblock.qblocks.first.value.vertexes.first.value.rank
            )
            if rank == float("-inf"):
                self._xblocks[0].append(compound_xblock)
                first_nonempty_index = 0
            else:
                self._xblocks[rank + 1].append(compound_xblock)
                first_nonempty_index = min(rank + 1, first_nonempty_index)
        self._first_nonempty_index = first_nonempty_index

    def update_first_nonempty_index(self):
        # we start checking from the last known value of _first_nonempty_index
        for idx, rank_list in enumerate(
            # fmt: off
            self._xblocks[self._first_nonempty_index + 1:]
            # fmt: on
        ):
            if len(rank_list) > 0:
                self._first_nonempty_index = (
                    idx + self._first_nonempty_index + 1
                )
                return
        # if we get here, there are no more compound xblocks
        self._first_nonempty_index = -1

    def append_at_rank(self, xblock, rank):
        rank_index = 0 if rank == float("-inf") else rank + 1
        self._xblocks[rank_index].append(xblock)
        self._first_nonempty_index = min(
            self._first_nonempty_index, rank_index
        )

    def append(self, xblock):
        self.append_at_rank(xblock, xblock.qblocks.first.value.rank)

    def extend(self, new_compound_xblocks):
        for xblock in new_compound_xblocks:
            first_qblock_rank = xblock.qblocks.first.value.rank
            self.append_at_rank(xblock, first_qblock_rank)

    def pop(self):
        xblock = self._xblocks[self._first_nonempty_index].pop()
        if len(self._xblocks[self._first_nonempty_index]) == 0:
            self.update_first_nonempty_index()
        return xblock

    def __iter__(self):
        return self._xblocks

    def __getitem__(self, key):
        return self._xblocks[key]
