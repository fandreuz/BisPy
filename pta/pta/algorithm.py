from llist import dllist, dllistnode

from utilities.graph_entities import *
from utilities.graph_utilities import *

# choose the smallest qblock of the first two
def extract_splitter(compound_block: XBlock):
    first_qblock = compound_block.qblocks.first
    if first_qblock.value.size <= first_qblock.next.value.size:
        compound_block.remove_qblock(first_qblock.value)
        return first_qblock.value
    else:
        qblock = first_qblock.next.value
        compound_block.remove_qblock(qblock)
        return qblock


# construct a list of the nodes in the counterimage of qblock to be used in the split-phase.
# this also updates count(x,qblock) = |qblock \cap E({x})| (because qblock is going to become a new xblock)
# remember to reset the value of aux_count after the refinement
def build_block_counterimage(B_qblock: QBlock) -> list[Vertex]:
    qblock_counterimage = []

    for vertex in B_qblock.vertexes:
        for edge in vertex.counterimage:
            counterimage_vertex = edge.source

            # this vertex should be added to the counterimage only if necessary (avoid duplicates)
            if not counterimage_vertex.visited:
                qblock_counterimage.append(counterimage_vertex)
                # remember to release this vertex
                counterimage_vertex.visit()

            # if this is the first time we found a destination in qblock for whom this node is a source, create a new instance of Count
            # remember to set it to None
            if not counterimage_vertex.aux_count:
                counterimage_vertex.aux_count = Count(counterimage_vertex, B_qblock)
            counterimage_vertex.aux_count.value += 1

    for vertex in qblock_counterimage:
        # release this vertex so that it can be visited again in a next splitting phase
        vertex.release()

    return qblock_counterimage


# compute the set E^{-1}(B) - E^{-1}(S-B) where S is the XBlock which contained the QBlock B.
# in order to get the right result, you need to run the method build_splitter_counterimage before, which sets aux_count
def build_second_splitter_counterimage(
    B_qblock_vertexes: list[Vertex],
) -> list[Vertex]:
    splitter_counterimage = []

    for vertex in B_qblock_vertexes:
        for edge in vertex.counterimage:
            if not edge.source.in_second_splitter:
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


# perform a Split with respect to B_qblock
def split(B_counterimage: list[Vertex]):
    # keep track of the qblocks modified during step 4
    changed_qblocks = []
    # if a split splits a QBlock in two non-empty QBlocks, then the XBlock which contains them is for sure compound. We need to check if it's already compound though.
    new_compound_xblocks = []

    for vertex in B_counterimage:
        # determine the qblock to which vertex belongs to
        qblock = vertex.qblock

        # remove vertex from this qblock, and place it in the "parallel" qblock
        qblock.remove_vertex(vertex)

        # if this is the first time a vertex is splitted from this qblock, create the helper qblock
        if not qblock.split_helper_block:
            changed_qblocks.append(qblock)
            qblock.initialize_split_helper_block()

        new_qblock = qblock.split_helper_block

        # put the vertex in the new qblock
        new_qblock.append_vertex(vertex)

    new_qblocks = []
    for qblock in changed_qblocks:
        helper_qblock = qblock.split_helper_block
        qblock.reset_helper_block()

        # add the new qblock to the same xblock to which the old qblock belongs, and obtain its ddllistnode
        qblock.xblock.append_qblock(helper_qblock)
        new_qblocks.append(helper_qblock)

        # if the old qblock has been made empty by the split (Q - E^{-1}(B) = \emptysey), remove it from the xblock
        if qblock.size == 0:
            qblock.xblock.remove_qblock(qblock)
        else:
            # the XBlock which contains the two splitted QBlocks is a NEW compound block only if its size is exactly two
            # NOTE: it's essential that helper_block is added to xblock only in this loop, because otherwise the size of a new compound block can't be forecasted precisely
            if qblock.xblock.qblocks.size == 2:
                new_compound_xblocks.append(qblock.xblock)

    return (new_qblocks, new_compound_xblocks)


# each edge a->b should point to |X(b) \cap E({a})| where X(b) is the XBlock b belongs to. Note that B_block is a new XBlock at the end of refine. We decrement the count for the edge because B isn't in S anymore (S was replaced with B, S-B indeed).
def update_counts(B_block_vertexes: list[Vertex]):
    for vertex in B_block_vertexes:
        # edge.destination is inside B now. We must decrement count(edge.source, S) by for each vertex y \in B such that edge.source -> y
        for edge in vertex.counterimage:
            # decrement count(x,S) since we removed B from S
            edge.count.value -= 1

            # set edge.count to count(x,B)
            edge.count = edge.source.aux_count


# be careful: you should only work with llist in order to get O(1) deletion from x/qblocks
def refine(compound_xblocks, xblocks):
    # refinement step (following the steps at page 10 of "Three partition refinement algorithms")

    new_qblocks = []

    # step 1 (select a refining block B)
    # extract a random compound xblock
    S_compound_xblock = compound_xblocks.pop()
    # select the right qblock from this compound xblock
    # note that the dllistonodes in this list will most likely be outdated after the first split
    B_qblock = extract_splitter(S_compound_xblock)
    B_qblock_vertexes = [vertex for vertex in B_qblock.vertexes]

    # step 2 (update X)
    # if S_compound_xblock is still compund, put it back in compound_xblocks
    if len(S_compound_xblock.qblocks) > 1:
        compound_xblocks.append(S_compound_xblock)

    # add the extracted qblock to xblocks
    B_xblock = XBlock()
    B_xblock.append_qblock(B_qblock)

    xblocks.append(B_xblock)

    # step 3 (compute E^{-1}(B))
    B_counterimage = build_block_counterimage(B_qblock)

    # step 4 (refine Q with respect to B)
    new_qblocks_from_split1, new_compound_xblocks = split(B_counterimage)
    new_qblocks.extend(new_qblocks_from_split1)
    compound_xblocks.extend(new_compound_xblocks)

    # step 5 (compute E^{-1}(B) - E^{-1}(S-B))

    # note that, since we are employing the strategy proposed in the paper, we don't even need to pass the XBLock S
    second_splitter_counterimage = build_second_splitter_counterimage(B_qblock_vertexes)

    # step 6
    new_qblocks_from_split2, new_compound_xblocks = split(second_splitter_counterimage)
    new_qblocks.extend(new_qblocks_from_split2)
    compound_xblocks.extend(new_compound_xblocks)

    # step 7
    update_counts(B_qblock_vertexes)

    # reset aux_count
    # we only care about the vertexes in B_counterimage since we only set aux_count for those vertexes x such that |E({x}) \cap B_qblock| > 0
    for vertex in B_counterimage:
        vertex.aux_count = None

    return (xblocks, new_qblocks)


# returns a list of labels splitted in partitions
def pta(q_partition: list[QBlock]):
    x_partition = [q_partition[0].xblock]
    compound_xblocks = [x_partition[0]]

    while len(compound_xblocks) > 0:
        x_partition, new_qblocks = refine(compound_xblocks=compound_xblocks, xblocks=x_partition)
        q_partition.extend(new_qblocks)
        pass

    return [
        tuple(map(lambda vertex: vertex.label, qblock.vertexes))
        for qblock in filter(lambda qblock: qblock.size > 0, q_partition)
    ]


def apply_pta(graph, initial_partition):
    (q_partition, _) = initialize(graph, initial_partition)
    return pta(q_partition)
