from llist import dllist, dllistnode
from typing import List, Dict, Any, Tuple, Iterable
import networkx as nx
from bispy.utilities.graph_entities import (
    _Vertex,
    _QBlock,
    _Count,
    _XBlock,
)
from bispy.paige_tarjan.paige_tarjan import (
    extract_splitter,
    split,
    update_counts,
    build_block_counterimage,
    build_exclusive_B_counterimage,
    refine,
)
from bispy.paige_tarjan.compound_xblocks_container import (
    CompoundXBlocksContainer,
)
from bispy.saha.ranked_compound_xblocks_container import (
    RankedCompoundXBlocksContainer,
)
from bispy.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)


# returns a list of labels splitted in partitions
def pta(
    x_partition: List[_XBlock],
    q_partition: List[_QBlock],
    compound_xblocks: RankedCompoundXBlocksContainer,
) -> List[Tuple[_Vertex]]:
    """Apply the Ranked *Paige-Tarjan*'s algorithm to obtain the RSCP/maximum
    bisimulation of the given `q_partition`.

    :param x_partition: The partition :math:`X`.
    :param q_partition: The partition :math:`Q`.
    :param compound_xblocks: List of compound blocks of :math:`X` (namely
        blocks that contain more than one block of the partition  :math:`Q`).
    """

    while compound_xblocks._first_nonempty_index > 0:
        x_partition, new_qblocks = refine(compound_xblocks, x_partition)
        q_partition.extend(new_qblocks)

    return list(filter(lambda qblock: qblock.size > 0, q_partition))


def ranked_split(
    current_partition: List[_QBlock], B_qblock: _QBlock, max_rank: int
) -> List[Tuple[_Vertex]]:
    """Split the given partition using the block `B_qblock` as *splitter*, then
    use Ranked *Paige-Tarjan*'s algorithm on the resulting partition.

    :param current_partition: The current partition as a list of
        :class:`bispy.utilities.graph_entities._QBlock`.
    :param B_qblock: The block to be used as *splitter*.
    :param max_rank: The maximum rank which may be found in the graph.
    :returns: The output of Ranked *Paige-Tarjan*'s algorithm as a list of
        tuples of vertexes.
    """

    # initialize x_partition and q_partition
    x_partition = [
        # this also overwrites any information about parent xblocks for qblock
        _XBlock().append_qblock(qblock)
        for qblock in current_partition
    ]
    q_partition = current_partition

    #  perform Split(B,Q)
    B_counterimage = build_block_counterimage(B_qblock)
    new_qblocks, new_compound_xblocks, chaned_qblocks = split(B_counterimage)

    # reset aux_count
    for vx in B_counterimage:
        vx.aux_count = None

    q_partition.extend(new_qblocks)

    if max_rank == float("-inf"):
        max_rank = -1

    # note that only new compound xblock are compound xblocks
    compound_xblocks = RankedCompoundXBlocksContainer(
        new_compound_xblocks, max_rank
    )

    return pta(x_partition, q_partition, compound_xblocks)
