from llist import dllist, dllistnode
from typing import List, Dict, Any, Tuple, Iterable
import networkx as nx

from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _QBlock,
    _Count,
    _XBlock,
)
from bisimulation_algorithms.paige_tarjan.graph_decorator import initialize
from bisimulation_algorithms.paige_tarjan.pta import (
    extract_splitter,
    split,
    update_counts,
)

from bisimulation_algorithms.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)


def append_new_compound_xblocks(
    new_compound_xblocks: List[_XBlock], compound_xblocks: List[List[_XBlock]]
) -> int:
    """Put the new compound blocks into the proper place of the list.

    Args:
        new_compound_xblocks (List[_XBlock]): New compound blocks.
        compound_xblocks (List[List[_XBlock]]): List of compound blocks in
        increasing order of rank.

    Returns:
        int: The index of the first new compound block.
    """

    min_index = 100000000

    for new_compound_xblock in new_compound_xblocks:
        first_qblock = new_compound_xblock.qblocks.first
        rank_index = (
            0
            if first_qblock.rank() == float("-inf")
            else first_qblock.rank() + 1
        )
        compound_xblocks[rank_index].append(new_compound_xblock)

        # update the minimum index
        min_index = min(min_index, rank_index)

    return min_index


# construct a list of the nodes in the counterimage of qblock to be used in the
# split-phase.
# this also updates count(x,qblock) = |qblock \cap E({x})| (because qblock is
# going to become a new xblock).
# remember to reset the value of aux_count after the refinement
def build_block_counterimage(B_qblock: _QBlock) -> List[_Vertex]:
    """Given a block B of Q, construct a list of vertexes x such that x->y and
    y is in B. This function also sets vertex.aux_count and increases it by one
    for each visited vertex in order to find the value |B cap E({vertex})| for
    each vertex, where A is the relation '->' of the graph.

    Args:
        B_qblock (_QBlock): A block of B.

    Returns:
        list[_Vertex]: A list of vertexes x such that x->y and y is in B (the
        order doesn't matter).
    """

    qblock_counterimage = []

    for vertex in B_qblock.vertexes:
        for edge in vertex.counterimage:
            if edge.source.allow_visit:
                counterimage_vertex = edge.source

                # this vertex should be added to the counterimage only if necessary
                # (avoid duplicates)
                if not counterimage_vertex.visited:
                    qblock_counterimage.append(counterimage_vertex)
                    # remember to release this vertex
                    counterimage_vertex.visit()

                # if this is the first time we found a destination in qblock for
                # whom this node is a source, create a new instance of Count.
                # remember to set it to None
                if not counterimage_vertex.aux_count:
                    counterimage_vertex.aux_count = _Count(counterimage_vertex)
                counterimage_vertex.aux_count.value += 1

    for vertex in qblock_counterimage:
        # release this vertex so that it can be visited again in a next
        # splitting phase
        vertex.release()

    return qblock_counterimage


# compute the set E^{-1}(B) - E^{-1}(S-B) where S is the _XBlock which
# contained the _QBlock B.
# in order to get the right result, you need to run the method
# build_splitter_counterimage before, which sets aux_count.
def build_exclusive_B_counterimage(
    B_qblock_vertexes: List[_Vertex],
) -> List[_Vertex]:
    """Given a block B of Q which has just been extracted from a compound
    block S of x, generate the exclusive counterimage of B, namely
    E^{-1}(B) - E^{-1}(S-B), where E is the relation '->' of the graph. It's
    fundamental that this function is called after build_block_counterimage,
    since it uses the aux_count values set by that function.

    Args:
        B_qblock_vertexes (list[_Vertex]): A block B extracted from a block S
        of X.

    Returns:
        list[_Vertex]: The vertexes in E^{-1}(B) - E^{-1}(S-B).
    """

    splitter_counterimage = []

    for vertex in B_qblock_vertexes:
        for edge in vertex.counterimage:
            if edge.source.allow_visit and not edge.source.in_second_splitter:
                # determine count(vertex,B) = |B \cap E({vertex})|
                count_B = edge.source.aux_count

                # determine count(vertex,S) = |S \cap E({vertex})|
                count_S = edge.count

                if count_B.value == count_S.value:
                    splitter_counterimage.append(edge.source)
                    edge.source.added_to_second_splitter()

    for vertex in splitter_counterimage:
        vertex.clear_second_splitter_flag()

    return splitter_counterimage


def refine(
    compound_xblocks: List[List[_XBlock]],
    xblocks: List[_XBlock],
    first_nonempty_compound_rankindex: int,
):
    """Perform a refinement step, given the current X partition and the
    compound blocks of X.

    Args:
        compound_xblocks (List[List[_XBlock]]): A list of list of compound
        blocks of X, namely those that contain more than one block of Q,
        sorted by increasing rank.
        xblocks (List[_XBlock]): The current X partition.
        first_nonempty_compound_rankindex: The index of the first non-empty
        item (which is a list) in the list of compound blocks ordered for
        increasing rank.

    Returns:
        tuple: A tuple containing the new X partition (resulting from the
        replacement of a block S with B, S-B) and the new blocks of Q which
        have been generated from the two split phases.
    """

    # refinement step (following the steps at page 10 of "Three partition
    # refinement algorithms")

    new_qblocks = []

    # step 1 (select a refining block B)
    S_compound_xblock = compound_xblocks[
        first_nonempty_compound_rankindex
    ].pop()

    # select the right qblock from this compound xblock
    # note that the dllistonodes in this list will most likely be outdated
    # after the first split
    B_qblock = extract_splitter(S_compound_xblock)
    B_qblock_vertexes = [vertex for vertex in B_qblock.vertexes]

    # step 2 (update X)
    # if S_compound_xblock is still compund, put it back in compound_xblocks
    if len(S_compound_xblock.qblocks) > 1:
        compound_xblocks[first_nonempty_compound_rankindex].append(
            S_compound_xblock
        )

    # add the extracted qblock to xblocks
    B_xblock = _XBlock()
    B_xblock.append_qblock(B_qblock)

    xblocks.append(B_xblock)

    # step 3 (compute E^{-1}(B))
    B_counterimage = build_block_counterimage(B_qblock)

    # step 4 (refine Q with respect to B)
    new_qblocks_from_split1, new_compound_xblocks = split(B_counterimage)
    new_qblocks.extend(new_qblocks_from_split1)
    append_new_compound_xblocks(new_compound_xblocks, compound_xblocks)

    # step 5 (compute E^{-1}(B) - E^{-1}(S-B))

    # note that, since we are employing the strategy proposed in the paper,
    # we don't even need to pass the XBLock S
    second_splitter_counterimage = build_exclusive_B_counterimage(
        B_qblock_vertexes
    )

    # step 6
    new_qblocks_from_split2, new_compound_xblocks = split(
        second_splitter_counterimage
    )
    new_qblocks.extend(new_qblocks_from_split2)

    # step 7
    update_counts(B_qblock_vertexes)

    # reset aux_count
    # we only care about the vertexes in B_counterimage since we only set
    # aux_count for those vertexes x such that |E({x}) \cap B_qblock| > 0
    for vertex in B_counterimage:
        vertex.aux_count = None

    return (xblocks, new_qblocks, new_compound_xblocks)


# returns a list of labels splitted in partitions
def pta(
    x_partition: List[_XBlock],
    compound_xblocks: List[List[_XBlock]],
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

    # compound blocks are ordered for increasing rank. each position is a list
    # of compound xblocks. we're interested in the first one (for rank)
    first_nonempty_compound_rankindex = -1
    for i, compound_blocks_at_rank in enumerate(compound_xblocks):
        if len(compound_blocks_at_rank) > 0:
            first_nonempty_compound_rankindex = i
            break

    while first_nonempty_compound_rankindex > 0:
        x_partition, new_qblocks, new_compound_xblocks = refine(
            compound_xblocks=compound_xblocks,
            xblocks=x_partition,
            first_nonempty_compound_rankindex=first_nonempty_compound_rankindex
        )
        q_partition.extend(new_qblocks)

        min_index = append_new_compound_xblocks(
            new_compound_xblocks, compound_xblocks
        )

        # we can use this index again
        if min_index < first_nonempty_compound_rankindex:
            first_nonempty_compound_rankindex = min_index
        else:
            old_first_nonempty_compound_rankindex = (
                first_nonempty_compound_rankindex
            )

            first_nonempty_compound_rankindex = -1

            for i in range(
                old_first_nonempty_compound_rankindex, len(compound_xblocks)
            ):
                if len(compound_xblocks[i]) > 0:
                    first_nonempty_compound_rankindex = i
                    break

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
    new_qblocks, new_compound_xblocks = split(B_counterimage)

    q_partition.extend(new_qblocks)

    # note that only new compound xblock are compound xblocks
    compound_xblocks = [[] for _ in range(max_rank + 2)]
    for compound_xblock in new_compound_xblocks:
        rank = compound_xblock.qblocks.first.value.vertexes.first.value.rank
        if rank == float("-inf"):
            compound_xblocks[0].append(compound_xblock)
        else:
            compound_xblocks[rank + 1].append(compound_xblock)

    pta(x_partition, compound_xblocks, q_partition)
