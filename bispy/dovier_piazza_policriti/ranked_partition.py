from typing import Iterable, List, Tuple, Dict, Union
from bispy.utilities.graph_entities import _QBlock as _Block, _Vertex, _XBlock


class RankedPartition:
    def __init__(self, vertexes: List[_Vertex]):
        """
        Manages a partition of nodes which are kept in separate classes
        according to their rank. Each vertex should already have a non-`None`
        `vertex.rank` field. The partition created by this constructor
        respects the constraints (if any) imposed with the attribute
        `initial_partition_block_id` in each vertex.

        This object is iterable (returns the classes of vertexes ordered
        by rank) and may be accessed with the operator `[i]` (returns the
        `i`-th class in the list). Also, the length of this object is defined
        as the number of classes of vertexes.

        :param vertexes: The list of vertexes in the partition.
        """

        self._nvertexes = len(vertexes)

        max_rank = max(vertex.rank for vertex in vertexes)
        list_positions = RankedPartition.rank_to_partition_idx(max_rank) + 1

        # a list of dicts, one dict for each rank index. in each dict there
        # are different blocks for different blocks of the labeling set
        rank_label = [{} for _ in range(list_positions)]

        for vertex in vertexes:
            rank_idx = RankedPartition.rank_to_partition_idx(vertex.rank)

            if vertex.initial_partition_block_id not in rank_label[rank_idx]:
                # we want to reuse the same xblock for all the vertexes
                # having the same rank
                if len(rank_label[rank_idx]) == 0:
                    xblock = _XBlock()
                else:
                    xblock = list(rank_label[rank_idx].values())[0].xblock

                rank_label[rank_idx][
                    vertex.initial_partition_block_id
                ] = _Block([], xblock)
            rank_label[rank_idx][
                vertex.initial_partition_block_id
            ].append_vertex(vertex)

        # we may not have leafs whith rank -inf, we create a shallow block to
        # fix the issue
        if len(rank_label[0]) == 0:
            rank_label[0][-1] = _Block([], _XBlock())

        # at this point there's no need to keep the blocks in a dictionary,
        # therefore we flatten the innermost dimension
        self._partition = [
            list(rank_idx_dict.values()) for rank_idx_dict in rank_label
        ]

    @property
    def nvertexes(self) -> int:
        """The number of vertexes in this partition."""
        return self._nvertexes

    @staticmethod
    def rank_to_partition_idx(rank: Union[int, float]) -> int:
        """Convert a rank to the corresponding index in the list of classes
        of nodes. `-inf` is the first rank, then 0, and so on.

        :param rank: The input rank.
        """

        if rank == float("-inf"):
            return 0
        else:
            return rank + 1

    def __getitem__(self, key):
        return self._partition[key]

    def append_at_rank(self, block: _Block, rank: Union[int, float]):
        """Append a new block in the class corresponding to the given rank.

        :param block: The new block.
        :param rank: The input rank.
        """

        self.append_at_index(block, RankedPartition.rank_to_partition_idx(rank))

    def append_at_index(self, block, index: int):
        """Append a new block in the `index`-th class.

        :param block: The new block.
        :param rank: The index of the class.
        """

        self._partition[index].append(block)

    def __len__(self):
        return len(self._partition)

    def clear_rank(self, rank: Union[int, float]):
        """Clear the list of blocks in the class corresponding to `rank`.

        :param block: The new block.
        :param rank: The input rank.
        """

        self.clear_index(RankedPartition.rank_to_partition_idx(rank))

    def clear_index(self, index: int):
        """Clear the list of blocks in the `index`-th class.

        :param block: The new block.
        :param rank: The index of the class.
        """

        self._partition[index].clear()

    def __iter__(self):
        return filter(lambda rank: len(rank) > 0, self._partition)

    def __repr__(self):
        def f(tp):
            idx, ls = tp
            return "{} : {}".format(idx, ls)

        return "\n".join(map(f, enumerate(self._partition)))
