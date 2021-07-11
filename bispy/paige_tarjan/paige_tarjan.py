from llist import dllist, dllistnode
from typing import List, Dict, Any, Tuple, Iterable
import networkx as nx

from bispy.utilities.graph_entities import (
    _Vertex,
    _XBlock,
    _QBlock,
    _Count,
)
from bispy.paige_tarjan.compound_xblocks_container import (
    CompoundXBlocksContainer,
)
from bispy.utilities.graph_decorator import (
    decorate_nx_graph,
    preprocess_initial_partition,
    to_tuple_list
)
from bispy.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)


# choose the smallest qblock of the first two
def extract_splitter(compound_block: _XBlock) -> _QBlock:
    """Given a compound block in the `X` partition, extract one of the blocks
    of the partition `Q` inside (the smallest among the first two blocks in
    the list). The chosen block is removed from the compound block and
    returned.

    compound_block: A compound block in the partition `X`.
    """

    first_qblock = compound_block.qblocks.first
    if first_qblock.value.size <= first_qblock.next.value.size:
        compound_block.remove_qblock(first_qblock.value)
        return first_qblock.value
    else:
        qblock = first_qblock.next.value
        compound_block.remove_qblock(qblock)
        return qblock


# construct a list of the nodes in the counterimage of qblock to be used in the
# split-phase.
# this also updates count(x,qblock) = |qblock \cap E({x})| (because qblock is
# going to become a new xblock).
# remember to reset the value of aux_count after the refinement
def build_block_counterimage(B_qblock: _QBlock) -> List[_Vertex]:
    """Given a block :math:`B  \\in Q`, construct the :math:`E^{-1}(B)`.
    This function also sets `vertex.aux_count` and increases it by one for each
    visited vertex in order to find the value :math:`|B \\cap E({vertex})|`,
    where :math:`E` is the edge relation (:math:`\\to`) of the graph.

    :param B_qblock: A block of :math:`Q`.
    """

    qblock_counterimage = []

    for vertex in B_qblock.vertexes:
        for edge in vertex.counterimage:
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
    """Given a block :math:`B \\in Q`, generate the "exclusive counterimage" of
    :math:`B`, namely the set :math:`E^{-1}(B) - E^{-1}(S-B)`, where :math:`E`
    is the edge relation (:math:`\\to`) of the graph. It's fundamental that
    this function is called after :func:`build_block_counterimage`,
    since it uses the field `aux_count` set by that function in instances of
    :class:`bispy.utilities.graph_entities._Vertex`.

    :param B_qblock_vertexes: A block of :math:`Q` represented by the list of
        its vertexes.
    """

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
def split(
    vertexes: List[_Vertex],
) -> Tuple[List[_QBlock], List[_XBlock], List[_QBlock]]:
    """Given a list of vertexes, use them as *splitter* set for the current
    partition :math:`Q`. This function doesn't modify the partition.

    :param vertexes: A list of vertexes.
    :returns: A tuple whose items are:

        0. The new blocks of :math:`Q`;
        1. The new compound blocks of :math:`X`;
        2. The modified (but not new) blocks of :math:`Q`.
    """

    # keep track of the qblocks modified during step 4
    changed_qblocks = []
    # if a split splits a _QBlock in two non-empty _QBlocks, then the _XBlock
    # which contains them is for sure compound. We need to check if it's
    # already compound though.
    new_compound_xblocks = []

    for vertex in vertexes:
        # determine the qblock to which vertex belongs to
        qblock = vertex.qblock

        # remove vertex from this qblock, and place it in the "parallel" qblock
        qblock.remove_vertex(vertex)

        # qblock is a new qblock since we removed a _Vertex
        qblock.is_new_qblock = True

        # if this is the first time a vertex is splitted from this qblock,
        # create the helper qblock
        if not qblock.split_helper_block:
            changed_qblocks.append(qblock)
            qblock.initialize_split_helper_block()

        new_qblock = qblock.split_helper_block

        # put the vertex in the new qblock
        new_qblock.append_vertex(vertex)

    new_qblocks = []
    for qblock in changed_qblocks:
        helper_qblock = qblock.split_helper_block
        helper_qblock.is_new_qblock = True

        qblock.reset_helper_block()

        new_qblocks.append(helper_qblock)

        # if the old qblock has been made empty by the split
        # (Q - E^{-1}(B) = emptyset), remove it from the xblock
        if qblock.size == 0:
            qblock.xblock.remove_qblock(qblock)
        else:
            # the _XBlock which contains the two splitted _QBlocks is a NEW
            # compound block only if its size is exactly two
            # NOTE: it's essential that helper_block is added to xblock only in
            # this loop, because otherwise the size of a new compound block
            # can't be forecasted precisely
            if qblock.xblock.qblocks.size == 2:
                new_compound_xblocks.append(qblock.xblock)

    return (new_qblocks, new_compound_xblocks, changed_qblocks)


# each edge a->b should point to |X(b) \cap E({a})| where X(b) is the _XBlock
# b belongs to. Note that B_block is a new _XBlock at the end of refine. We
# decrement the count for the edge because B isn't in S anymore (S was replaced
# with B, S-B indeed).
def update_counts(B_block_vertexes: List[_Vertex]):
    """After a block :math:`B \\in Q` has become a (non-compound) block of
    :math:`X` on its own (it was removed from a compound block of :math:`X`) we
    need to decrease by one the quantity `count(x`, :math:`S`) (which is now
    `count(x`, :math:`S-B`)) for each vertex in :math:`E^{-1}(B)`.

    :param B_block_vertexes: A block of :math:`Q` which is also a block of
        :math:`S`, represented by its vertexes.
    """

    for vertex in B_block_vertexes:
        # edge.destination is inside B now. We must decrement
        # count(edge.source, S) by for each vertex y \in B such that
        # edge.source -> y
        for edge in vertex.counterimage:
            # decrement count(x,S) since we removed B from S
            edge.count.value -= 1

            # set edge.count to count(x,B)
            edge.count = edge.source.aux_count


def refine(
    compound_xblocks: CompoundXBlocksContainer, xblocks: List[_XBlock]
) -> Tuple[List[_XBlock], List[_QBlock]]:
    """Perform a refinement step of the *Paige-Tarjan* algorithm.

    :param compound_xblocks: Compound blocks in the partition :math:`X`. This
        parameter expects an object of type
        :class:`bispy.paige_tarjan.compound_xblocks_container
        .CompoundXBlocksContainer`, but it is possible to subclass this class
        in order to support a different ordering of compound blocks.

        .. seealso:: modules :py:mod:`bispy.saha.ranked_pta`

    :param xblocks: The partition :math:`X`.
    :returns: A tuple whose items are:

        0. The new partition :math:`X`;
        1. The new blocks of :math:`Q` generated by the two *split* phases;
    """

    # refinement step (following the steps at page 10 of "Three partition
    # refinement algorithms")

    new_qblocks = []

    # step 1 (select a refining block B)
    # extract a random compound xblock
    S_compound_xblock = compound_xblocks.pop()
    # select the right qblock from this compound xblock
    # note that the dllistonodes in this list will most likely be outdated
    # after the first split
    B_qblock = extract_splitter(S_compound_xblock)
    B_qblock_vertexes = [vertex for vertex in B_qblock.vertexes]

    # step 2 (update X)
    # if S_compound_xblock is still compund, put it back in compound_xblocks
    if len(S_compound_xblock.qblocks) > 1:
        compound_xblocks.append(S_compound_xblock)

    # add the extracted qblock to xblocks
    B_xblock = _XBlock()
    B_xblock.append_qblock(B_qblock)

    xblocks.append(B_xblock)

    # step 3 (compute E^{-1}(B))
    B_counterimage = build_block_counterimage(B_qblock)

    # step 4 (refine Q with respect to B)
    new_qblocks_from_split1, new_compound_xblocks, _ = split(B_counterimage)
    new_qblocks.extend(new_qblocks_from_split1)
    compound_xblocks.extend(new_compound_xblocks)

    # step 5 (compute E^{-1}(B) - E^{-1}(S-B))

    # note that, since we are employing the strategy proposed in the paper,
    # we don't even need to pass the XBlock S
    second_splitter_counterimage = build_exclusive_B_counterimage(
        B_qblock_vertexes
    )

    # step 6
    new_qblocks_from_split2, new_compound_xblocks, _ = split(
        second_splitter_counterimage
    )
    new_qblocks.extend(new_qblocks_from_split2)
    compound_xblocks.extend(new_compound_xblocks)

    # step 7
    update_counts(B_qblock_vertexes)

    # reset aux_count
    # we only care about the vertexes in B_counterimage since we only set
    # aux_count for those vertexes x such that |E({x}) \cap B_qblock| > 0
    for vertex in B_counterimage:
        vertex.aux_count = None

    return (xblocks, new_qblocks)


# returns a list of labels splitted in partitions
def paige_tarjan_qblocks(q_partition: List[_QBlock]) -> List[_QBlock]:
    """Apply the *Paige-Tarjan* algorithm to the partition :math:`Q`, which
        is considered a labeling set (namely two vertexes in different
        blocks of the initial partition cannot be bisimilar).

    :param q_partition: The initial partition (labeling set).
    :returns: The RSCP/maximum bisimulation of the given labeling set.
    """
    # initially, there's only one block in the partition X, the one which
    # contains each block in Q
    x_partition = [q_partition[0].xblock]
    # if there's more than one block of Q in the (single) block in X, we can
    # add it to compound_blocks
    if len(x_partition[0].qblocks) > 1:
        compound_xblocks = CompoundXBlocksContainer([x_partition[0]])
    else:
        compound_xblocks = CompoundXBlocksContainer([])

    while len(compound_xblocks) > 0:
        x_partition, new_qblocks = refine(
            compound_xblocks=compound_xblocks, xblocks=x_partition
        )
        q_partition.extend(new_qblocks)

    return [
        qblock
        for qblock in filter(lambda qblock: qblock.size > 0, q_partition)
    ]


def paige_tarjan(
    graph: nx.Graph,
    initial_partition: Iterable[Iterable[int]] = None,
    is_integer_graph: bool = False,
) -> List[Tuple]:
    """Compute the RSCP/maximum bisimulation of the given graph using
    *Paige-Tarjan*'s algorithm, with the given initial partition
    (or *labeling set*, two vertexes in different blocks of the initial
    partition cannot be bisimilar).

        >>> graph = networkx.balanced_tree(2,3)
        >>> paige_tarjan(graph)
        [(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6), (1, 2), (0,)]

    This function works with integer graph (nodes are integers starting from
    0 and form an interval without holes). If the given graph is non-integer
    it is converted to an isomorphic integer graph automatically (unless
    `is_integer_graph` is `True`) and then re-converted to its original form
    after the end of the computation. For this reason nodes of `graph` **must**
    be hashable objects.

    .. warning::
        Using a non integer graph and setting `is_integer_graph` to `True`
        will probably make the function fail with an exception, or, even worse,
        return a wrong output.

    :param graph: The input graph.
    :param initial_partition: The initial partition (or labeling set). Defaults
        to `None`, in which case the trivial labeling set (one block which
        contains all the nodes) is used.
    :param is_integer_graph: If `True`, the function assumes that
        the graph is integer, and skips the integer check (may slightly
        improve performance). Defaults to `False`.
    :returns: The RSCP/maximum bisimulation of the given labeling set as a
        list of tuples, each of which contains bisimilar nodes.
    """

    if not isinstance(graph, nx.DiGraph):
        raise Exception("graph should be a directed graph (nx.DiGraph)")

    # if True, the input graph is already an integer graph
    original_graph_is_integer = is_integer_graph or check_normal_integer_graph(
        graph
    )

    # if initial_partition is None, then it's the trivial partition
    if initial_partition is None:
        # only list(graph.nodes) isn't OK
        initial_partition = [list(graph.nodes)]

    if not original_graph_is_integer:
        # convert the graph to an "integer" graph
        integer_graph, node_to_idx = convert_to_integer_graph(graph)

        # convert the initial partition to a integer partition
        integer_initial_partition = [
            [node_to_idx[old_node] for old_node in block]
            for block in initial_partition
        ]
    else:
        integer_graph = graph
        integer_initial_partition = initial_partition

    vertexes, q_partition = decorate_nx_graph(
        integer_graph,
        integer_initial_partition,
        topological_sorted_images=False,
        compute_rank=False,
    )
    xblock = q_partition[0].xblock

    rscp = paige_tarjan_qblocks(q_partition)
    integer_rscp = to_tuple_list(rscp)

    if original_graph_is_integer:
        return integer_rscp
    else:
        return back_to_original(integer_rscp, node_to_idx)
