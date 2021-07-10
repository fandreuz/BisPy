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
    CompoundXBlocksContainer,
    refine,
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
    compound_xblocks: RankedCompoundXBlocksContainer,
    q_partition: List[_QBlock],
) -> List[Tuple]:
    """Apply the Paige-Tarjan algorithm to an initial partition Q which
    contains the whole "internal" representation of a graph.

    Args:
        x_partition: a list of XBlocks
        compound_xblocks (List[List[_XBlock]]): A list of list of compound
        blocks of X, namely those that contain more than one block of Q,
        sorted by increasing rank.
        q_partition (list[_QBlock]): The initial partition represented as the Q
        partition (namely with instances of QBlock).

    Returns:
        list[_Vertex]: The RSCP of the given initial partition as a list of
        Vertex instances.
    """

    while compound_xblocks._first_nonempty_index > 0:
        x_partition, new_qblocks = refine(compound_xblocks, x_partition)
        q_partition.extend(new_qblocks)

    return list(filter(lambda qblock: qblock.size > 0, q_partition))


def ranked_split(
    current_partition: List[_QBlock], B_qblock: _QBlock, max_rank: int
):
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

    return pta(x_partition, compound_xblocks, q_partition)
