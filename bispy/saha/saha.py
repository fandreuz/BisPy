import networkx as nx
from bispy.utilities.graph_entities import (
    _Vertex,
    _QBlock as _Block,
    _Edge,
    _Count,
    _XBlock,
    _SCC,
)
from typing import List, Tuple, Set, Dict, Union
from .ranked_pta import ranked_split
from bispy.paige_tarjan.paige_tarjan import paige_tarjan_qblocks
from bispy.dovier_piazza_policriti.dovier_piazza_policriti import (
    build_block_counterimage,
)
from itertools import product, chain, combinations
from bispy.utilities.kosaraju import kosaraju
from bispy.utilities.rank_computation import (
    scc_finishing_time_list,
)
from operator import attrgetter


def add_edge(source: _Vertex, destination: _Vertex) -> _Edge:
    """Add a new edge to the graph (this is the internal *BisPy*
    representation, therefore the original graph is left untouched).

    This function also sets the `count` attribute for the new edge, creating
    a new instance of :class:`bispy.utilities.graph_entities._Count` if the
    source of the edge was a sink previously, and getting the instance
    from the first edge in the image otherwise.

    :param source: The source of the new edge.
    :param destination: The source of the new edge.
    """

    edge = _Edge(source, destination)
    if len(source.image) > 0:
        # there's already a _Count instance for the image of this Vertex,
        # therefore we HAVE to use it.
        edge.count = source.image[0].count
    else:
        # the source was a sink previously
        edge.count = _Count(source)

    edge.count.value += 1

    source.add_to_image(edge)
    destination.add_to_counterimage(edge)

    return edge


def is_in_image(ublock: _Block, vblock: _Block) -> bool:
    """Check if `vblock` is in the image of `ublock`. This is used **before**
    adding a new edge, because if the destination vertex is already in the
    image of the source vertex we do not need to change the partition to
    reach the maximum bisimulation.

    .. warning::
        `ublock` and `vblock` **must** be members of a **stable** partition,
        otherwise this function returns a wrong output.

    :param ublock: The block for which we check the image.
    :param vblock: The block that we look for in the image of `ublock`.

    :return: `True` if `vblock` belongs to the image of `ublock`, `False`
        otherwise.
    """

    # since we assume that the given blocks are members of an RSCP, we only
    # need to verify if a single vertex of ublock has an edge towards vblock
    vertex = ublock.vertexes.first.value
    return any(
        map(
            lambda block: block == vblock,
            map(lambda edge: edge.destination.qblock, vertex.image),
        )
    )


def check_new_scc(
    current_source: _Vertex,
    destination: _Vertex,
    finishing_time_list: List[_Vertex] = None,
    # min_rank: int = None,
    # max_rank: int = None,
    visited_vertexes: List[_Vertex] = None,
    root_call=True,
) -> bool:
    """Check if a new *strongly connected component* has been created after
    the addition of a new edge. This is meant to be a *recursive* method,
    therefore the new edge is not always :math:`\\langle`
    `current_source, destination` :math:`\\rangle`.

    This method visits :math:`G^{-1}` recursively (with a DFS strategy)
    starting from `current_source` until it finds the `destination` vertex, in
    which case a new SCC is recognized.

    Meanwhile it also sets the flag `visited` for each visited vertex to
    prevent visiting the same node twice. At the end of the execution the
    root call **cleans** the flag `visited` for each vertex by exploring each
    vertex in the list `visited_vertexes`, which is passed automatically from
    the root call to all its children.

    It also sets the flag `visited` for each visited
    :class:`bispy.utilities.graph_entities._QBlock`. This information is used
    in other parts of the algorithm.

    :param current_source: The current starting point for the DFS of
        :math:`G^{-1}`.
    :param destination: The destination vertex of the new edge.
    :param finishing_time_list: An empty list which will be filled with
        the vertexes ordered by finishing time (first are those for which the
        exploaration of the image ended earlier). This feature is disabled if
        this argument is `None`.
    :param visited_vertexes: An empty list which will be filled with
        the vertexes visited during the execution. You do not need to pass a
        non-`None` value since the root call takes care of the necessary
        cleanup which occurs after the execution of the function.
    :param root_call: `True` if this instance of the function is the root call.
        Passing any value other than `True` (from a user perspective) is going
        to end with an exception.

    :return: `True` if a new *strongly connected component* has been created,
        `False` otherwise.
    """
    # TODO: check
    # this is a consequence of the context where this function is used, keep
    # in mind when testing!
    # if min_rank is None:
    #    min_rank = current_source.rank
    # if max_rank is None:
    #    max_rank = destination.rank

    if root_call:
        current_source.visited = True
        current_source.qblock.visited = True

        visited_vertexes = []
        visited_vertexes.append(current_source)

    flag_scc_found = False

    for edge in current_source.counterimage:
        # we reached the block [v], therefore this is a new SCC
        if edge.source == destination:
            flag_scc_found = True

        if (
            not edge.source.visited
            # and min_rank <= edge.source.rank
            # and edge.source.rank <= max_rank
        ):
            # we don't want to visit a vertex more than one time
            edge.source.visited = True
            visited_vertexes.append(edge.source)

            edge.source.qblock.visited = True

            # if at least one of the possible ramifications is True,
            # return True
            flag_scc_found = (
                check_new_scc(
                    edge.source,
                    destination,
                    finishing_time_list,
                    # min_rank,
                    # max_rank,
                    visited_vertexes,
                    root_call=False,
                )
                or flag_scc_found
            )

    if finishing_time_list is not None:
        finishing_time_list.append(current_source)

    # we have to clean the flag "visited" for each visited vertex
    if root_call:
        for vx in visited_vertexes:
            vx.visited = False

    return flag_scc_found


def both_blocks_go_or_dont_go_to_block(
    block1: _Block, block2: _Block, block_counterimage: List[_Vertex]
) -> bool:
    """Check if both `block1` and `block2` have a non-empty intersection with
    the set of vertexes `block_counterimage`.

    Usually the parameter
    `block_counterimage` contains the counterimage of a block, therefore this
    method may be stated like "find if both `block1` and `block2` go to
    the third block, or if both blocks do not go to that block".

    :param block1: A block.
    :param block2: A block.
    :param block_counterimage: A set of vertexes.
    :return: `True` if
        :math:`\\delta(|\\textit{block1} \\cap \\textit{block_counterimage}|)`
        is equal to
        :math:`\\delta(|\\textit{block2} \\cap \\textit{block_counterimage}|)`.
    """

    block1_goes = False
    block2_goes = False

    for vertex in block_counterimage:
        if vertex.qblock == block1:
            block1_goes = True
            # the situation changed: CHECK!
            if block2_goes:
                return True
        elif vertex.qblock == block2:
            block2_goes = True
            # the situation changed: CHECK!
            if block1_goes:
                return True

    return block1_goes == block2_goes


def exists_causal_splitter(
    block1: _Block, block2: _Block, check_visited
) -> bool:
    """Check if there is a *causal splitter* for blocks `block1` and `block2`.
    A causal splitter is a block :math:`C` such that

    .. math::

        \\textit{block1} \\cap E^{-1}(C) \\neq \\emptyset \\land
        \\textit{block2} \\cap E^{-1}(C) = \\emptyset

    or viceversa.

    The existence of a *causal splitter* prevents two blocks from being
    joined.

    :param block1: A block.
    :param block2: A block.
    :param check_visited: If `True`, we only consider vertexes in blocks
        which have been visited during the first DFS (namely that which
        was performed to search for a new SCC). If `False`, each block is
        a plausible *causal splitter*.
    :return: `True` if there is a *causal splitter* for the two blocks,
        `False` otherwise.
    """

    def plausible_causal_splitters(block, the_other_block):
        s = set()
        for v in block.vertexes:
            for edge in v.image:
                current_block = edge.destination.qblock
                # if check_visited is true, we only want to consider
                # qblock visited in the first DFS (flag visited is true)
                if not (check_visited and current_block.visited):
                    # causal splitter HAVE TO be blocks such that we KNOW they
                    # are in the new rscp of G' (the updated graph)
                    if (
                        current_block.rank < block.rank
                        or current_block == the_other_block
                    ):
                        s.add(id(edge.destination.qblock))
        return s

    block_image1 = plausible_causal_splitters(block1, block2)
    block_image2 = plausible_causal_splitters(block2, block1)

    return block_image1 != block_image2


def merge_condition(
    block1: _Block, block2: _Block, check_visited: bool = False
) -> bool:
    """Check all the condition which may prevent the union of two blocks,
    returns `True` if the blocks can be joined. Some conditions are redundant,
    we check first those which are almost instantaneous to verify since this
    method is going to be called frequently.

    The conditions:

    1. Same labeling set/initial partition;
    2. The two blocks are not the same block;
    3. Same rank;
    4. One of the blocks was deteached from the partition previously (therefore
        it is most likely empty at this points);
    5. There is not a *causal splitter* for the two blocks.

    :param block1: A block.
    :param block2: A block.
    :param check_visited: See the documentation of
        :func:`exists_causal_splitter`.
    """
    if (
        block1.initial_partition_block_id()
        != block2.initial_partition_block_id()
    ):
        return False
    elif block1 == block2:
        return False
    elif block1.rank != block2.rank:
        return False
    elif block1.deteached or block2.deteached:
        return False
    elif exists_causal_splitter(block1, block2, check_visited):
        return False
    else:
        return True


def recursive_merge(block1: _Block, block2: _Block):
    """Merge `block1`, `block2` (put the vertexes of `block2` into
    `block1`), deteach `block2` from the partition, and check recursively if
    we can also merge some couples of predecessors of `block1` and `block2`
    (namely couple of blocks :math:`C,D` such that

    .. math::

        C \\implies \\textit{block1} \\land D \\implies \\textit{block2}

    where the relation ":math:`\\implies`" means that there is at least one
    vertex of the rightmost block which is a child of the leftmost block).

    If such at couple exists, the method recursively merges those two blocks,
    for each couple for which :func:`merge_condition` is `True`.

    :param block1: A block.
    :param block2: A block.
    """

    vertexes1 = list(block1.vertexes)
    vertexes2 = list(block2.vertexes)

    block1.merge(block2)

    # construct a list of couples of blocks which needs to be verified
    verified_couples = {}

    for vx1, vx2 in product(vertexes1, vertexes2):
        for edge1, edge2 in product(vx1.counterimage, vx2.counterimage):
            b1 = edge1.source.qblock
            b2 = edge2.source.qblock

            if (
                not (id(b1), id(b2)) in verified_couples
                or (id(b2), id(b1)) in verified_couples
            ):
                verified_couples[id(b1), id(b2)] = True
                if merge_condition(b1, b2):
                    recursive_merge(b1, b2)


def merge_phase(
    ublock: _Block,
    vblock: _Block,
):
    """We check if there is a block :math:`U1` such that before the addition
    of the new edge :math:`\\langle u,v \\rangle` there was a
    *causal splitter* for the couple :math:`([u],U1)`, and for which
    :func:`merge_condition` now returns `True` on that couple.

    In that case we merge the two blocks using :func:`recursive_merge`.

    :param ublock: The block of the partition in which resides the source
        of the new edge.
    :param vblock: The block of the partition in which resides the destination
        of the new edge.
    """
    for vertex in vblock.vertexes:
        for edge in vertex.counterimage:
            u1block = edge.source.qblock
            if merge_condition(ublock, u1block):
                recursive_merge(ublock, u1block)


def merge_step(vertex, X, visited_vertexes, cant_merge_dict):
    vertex.visited = True
    visited_vertexes.append(vertex)

    # try to merge this block
    if not vertex.qblock.tried_merge:
        initial_partition_block_id = vertex.qblock.initial_partition_block_id()
        # if there are blocks which can't be merged with each other in the
        # dict, we try to merge this with one of them
        if initial_partition_block_id in cant_merge_dict:
            merged = False
            # loop over blocks in the dict
            for qblock in cant_merge_dict[initial_partition_block_id]:
                if merge_condition(vertex.qblock, qblock, check_visited=True):
                    # it's preferable to deteach vertex.qblock instead of
                    # qblock in order to reduce the rubbish
                    recursive_merge(qblock, vertex.qblock)
                    merged = True
                    break
            if not merged:
                # if this blocks wasn't merged with anyone, add this block to
                # the dict
                cant_merge_dict[initial_partition_block_id].append(
                    vertex.qblock
                )
                # no merge, therefore we append the block to X
                X.append(vertex.qblock)
        else:
            # this is the first block for this initial label
            cant_merge_dict[initial_partition_block_id] = [vertex.qblock]
            # the block is the first of its initial_partition_block_id,
            # therefore we can put it into X
            X.append(vertex.qblock)

        vertex.qblock.tried_merge = True

    for edge in vertex.image:
        if not edge.destination.visited:
            merge_step(edge.destination, X, visited_vertexes, cant_merge_dict)


def preprocess_initial_partition(qblocks: List[_Block]):
    """
    Preprocess the given partition to split blocks which contain leafs and
    non-leafs.

    :param qblocks: A partition.
    """
    for block in qblocks:
        leafs = []
        non_leafs = []

        for vertex in block.vertexes:
            if len(vertex.image) == 0:
                leafs.append(vertex)
            else:
                non_leafs.append(vertex)

        # if at least one is not zero, this block needs to be splitted
        if len(leafs) * len(non_leafs) != 0:
            qblocks.append(block.fast_mitosis(leafs))


def merge_split_phase(
    qpartition: List[_Block], finishing_time_list: List[_Vertex]
) -> List[_Block]:
    """
    The function `MergeAndSplitPhase` from the paper.

    :param qpartition: The current partition.
    :param finishing_time_list: List of vertexes in the graph ordered by
        finishing time.
    :returns: The updated partition.
    """

    max_rank = float("-inf")
    for block in qpartition:
        max_rank = max(max_rank, block.rank)

    # a dict of lists of blocks (the key is the initial partition ID)
    # where each couple can't be merged
    cant_merge_dict = {}

    # keep track in order to remove the 'visited' flag
    visited_vertexes = []

    # a partition containing all the touched blocks
    X = []

    # visit G in order of decreasing finishing times of the first DFS
    for vertex in finishing_time_list:
        # a vertex may be reached more than one time
        if not vertex.visited:
            merge_step(vertex, X, visited_vertexes, cant_merge_dict)

    X = list(filter(lambda block: not block.deteached, X))

    # clear visited flag
    for vx in visited_vertexes:
        vx.visited = False

    # reset block.visited flag (was set by first DFS) and tried_merge
    for block in qpartition:
        block.visited = False
        block.tried_merge = False

    # ------------
    # Split phase
    # ------------

    # we need to scale in order to use PTA (and then scale back)
    scaled_to_nonscaled = []

    xblock = _XBlock()
    for block in X:
        # this is needed for PTA
        xblock.append_qblock(block)
        # set visited flag in order to compute the set (qpartition - X) easily
        block.visited = True

        for vx in block.vertexes:
            # mark as reachable by PTA
            vx.allow_visit = True

            # scale label in order to use PTA
            vx.scale_label(len(scaled_to_nonscaled))
            scaled_to_nonscaled.append(vx.label)

    # build the new qpartition, without the blocks in X (which may be split).
    # this is just the set qpartition - X
    new_qpartition = []
    for block in qpartition:
        if not (block.visited or block.deteached):
            new_qpartition.append(block)
        else:
            # now we can clean the flag, this block was already discarded
            block.visited = False

    for block in X:
        for vx in block.vertexes:
            vx.restrict_to_subgraph(validation=lambda v: v.allow_visit)

    # apply PTA and append the blocks to the new partition
    preprocess_initial_partition(X)
    X2 = paige_tarjan_qblocks(X)
    new_qpartition.extend(X2)

    for block in X2:
        for vx in block.vertexes:
            # restore the original image/counterimage
            vx.back_to_original_graph()
            # clean allow_visit
            vx.allow_visit = False
            # restore original label
            vx.back_to_original_label()

    # select the blocks which are the result of a split
    # split, and clean block.visited
    for block in filter(attrgetter("is_new_qblock"), X2):
        # split
        new_qpartition = ranked_split(new_qpartition, block, max_rank)
        # clean
        block.is_new_qblock = False

    return new_qpartition


def propagate_nwf(scc: _SCC, scc_finishing_time: List[_SCC]):
    """Compute the updated *rank* of the given SCC, and propagate the change to
    its counterimage in the order given by the finishing time of a visit
    on the graph of strongly connected components of :math:`G`.

    :param scc: The SCC for which we want to update the rank.
    :param scc_finishing_time: A list of SCCs ordered by finishing time
        of a DFS on the graph of strongly connected components of :math:`G`.
    """
    # TODO: è una DFS sul grafico delle SCC, o sul suo inverso?

    if not scc.visited:
        scc.visited = True

        scc.compute_image()
        scc.compute_counterimage()

        if len(scc._image) == 0:
            if len(scc._vertexes) == 0:
                scc.mark_leaf()
            else:
                scc.mark_scc_leaf()
        else:
            mx = float("-inf")
            # at this point we can rely on the flag wf since the visit
            # occurs in the right order
            for image_scc in scc.image:
                if image_scc.wf is False:
                    scc._wf = False

                r = image_scc.rank
                mx = max(mx, r + 1 if image_scc.wf else r)
            scc._rank = mx

        # since we store rank and wf into SCCs, there's no need to propagate
        # the new rank to members of the SCC

        for sf in scc_finishing_time:
            if sf.label in scc._counterimage:
                propagate_nwf(sf, scc_finishing_time)


def propagate_wf(
    vertex: _Vertex,
    well_founded_topological: List[_Vertex],
    scc_finishing_time: List[_SCC],
):
    """Recursively visit the well-founded counterimage of the given vertex and
    update the *rank*. The visit is in increasing order of rank (this is needed
    in order to obtain the correct result).

    :param vertex: The vertex to whose counterimage we intend to propagate the
        change of the *rank*. The *rank* of this argument must already be
        updated, since it is left untouched after the execution.
    :param well_founded_topological: List of well founded vertexes of the
        **whole** graph in topological order.
    """

    for vx in well_founded_topological:
        mx = vx.rank
        for edge in vx.image:
            if edge.destination.wf:
                mx = max(mx, edge.destination.rank + 1)
        vx.rank = mx

    # propagate the changes also to nwf nodes
    for vx in well_founded_topological:
        for edge in vx.counterimage:
            if not edge.source.wf:
                propagate_nwf(edge.source.scc, scc_finishing_time)


def build_well_founded_topological_list(
    partition: List[_Block], source: _Vertex, max_rank: int
) -> List[_Vertex]:
    """
    Build a list of all the vertexes in the graph sorted in increasing order
    of *rank*.

    We ignore all the nodes which do not have *rank* = :math:`-\\infty` and
    have rank lower that the rank of the source vertex of the new edge.

    :param partition: A partition of the graph from which we obtain the
        instances of :class:`bispy.utilities.graph_entities._Vertex`. All the
        nodes in the same block **must** have the same *rank*.
    :param source: The source vertex of the new edge.
    :param max_rank: The maximum rank of a vertex in this graph, used to create
        a list of the appropriate size.
    """

    if source.rank == float("-inf"):
        source_position = 0
    else:
        source_position = source.rank + 1

    if max_rank == float("-inf"):
        buckets = [None]
    else:
        buckets = [None for _ in range(max_rank + 2 - source_position)]

    for block in partition:
        if block.rank == float("-inf"):
            idx = 0
        elif block.rank >= source.rank:
            idx = block.rank + 1 - source_position
        else:
            # we ignore blocks of rank lower than the rank of the source
            continue

        if buckets[idx] is None:
            buckets[idx] = []

        for vx in block.vertexes:
            if vx.wf:
                buckets[idx].append(vx)

    wft = []
    for rank_list in buckets:
        if rank_list is not None:
            wft.extend(rank_list)
    return wft

    """ dict_by_rank = {}
    well_founded_topological = []
    for block in old_rscp:
        if block.rank in dict_by_rank:
            ls = dict_by_rank[block.rank]
        else:
            ls = []
            dict_by_rank[block.rank] = ls
        for vertex in block.vertexes:
            if vertex.wf:
                ls.append(vertex)
    for _, ls in dict_by_rank.items():
        well_founded_topological.extend(ls)
    return well_founded_topological """


def filter_deteached(blocks: List[_Block]) -> List[_Block]:
    """
    Remove deteached blocks (blocks such that the attribute
    `deteached` is `True`) from the given list.

    :param blocks: A list of blocks.
    """
    return list(filter(lambda block: not block.deteached, blocks))


def saha(
    old_rscp: List[_Block],
    vertexes: List[_Vertex],
    new_edge: Union[Tuple[_Vertex, _Vertex], Tuple[int, int]],
) -> List[_Block]:
    """
    Update the given RSCP/maximum bisimulation after the addition of the given
    **new** edge using *Saha*'s incremental algorithm.

    The edge must not be already in the *BisPy* representation
    of the graph (namely in the image/counterimage of the instances
    of :class:`bispy.utilities.graph_entities._Vertex` in blocks of
    `old_rscp`).

    :param old_rscp: The old RSCP/maximum bisimulation which we wish to update.
    :param vertexes: List of vertexes in the graph.
    :new_edge: The new edge to be added to the graph (as a tuple of two
        :class:`bispy.utilities.graph_entities._Vertex` instances, or two
        ints which represent the indexes of the nodes which characterize the
        edge). The first item represents the **source** of the edge, the second
        represents the **destination**.
    :returns: The updated RSCP/maximum bisimulation. Also *rank* is updated for
        each vertex.
    """

    if isinstance(new_edge[0], int) and isinstance(new_edge[1], int):
        source_vertex = vertexes[new_edge[0]]
        destination_vertex = vertexes[new_edge[1]]
    elif isinstance(new_edge[0], _Vertex) and isinstance(new_edge[1], _Vertex):
        source_vertex, destination_vertex = new_edge
    else:
        raise ValueError("You must pass integers or Vertex instances!")

    # if the new edge connects two blocks A,B such that A => B before the edge
    # is added we don't need to do anything
    if is_in_image(source_vertex.qblock, destination_vertex.qblock):
        add_edge(source_vertex, destination_vertex)
        return old_rscp

    max_rank = max(map(lambda block: block.rank, old_rscp))

    well_founded_topological = build_well_founded_topological_list(
        old_rscp, vertexes[new_edge[0]], max_rank
    )

    sccs_dict = {}
    for vx in vertexes:
        sccs_dict[vx.scc.label] = vx.scc
    sccs = list(sccs_dict.values())

    for scc in sccs:
        scc.compute_image()

    scc_finishing_time = scc_finishing_time_list(sccs)

    # update immediately the wf flag
    if not destination_vertex.wf:
        source_vertex.wf = False

    # update the graph representation
    add_edge(source_vertex, destination_vertex)

    qpartition = ranked_split(old_rscp, destination_vertex.qblock, max_rank)

    # u isn't well founded, v is well founded
    if not source_vertex.wf and destination_vertex.wf:
        # if necessary, update the rank of u and propagate the changes
        if destination_vertex.rank + 1 > source_vertex.rank:
            source_vertex.rank = destination_vertex.rank + 1

            # source_vertex doesn't become nwf
            propagate_nwf(source_vertex.scc, scc_finishing_time)

        merge_phase(source_vertex.qblock, destination_vertex.qblock)
        return filter_deteached(qpartition)
    else:
        # in this case we don't need to update the rank
        if source_vertex.rank > destination_vertex.rank:
            merge_phase(source_vertex.qblock, destination_vertex.qblock)
            return filter_deteached(qpartition)
        else:
            # we want to save the finishing time list
            finishing_time_list = []

            # in this case u is part of the new SCC (which contains also
            # v), therefore it isn't well founded
            if check_new_scc(
                source_vertex,
                destination_vertex,
                finishing_time_list,
            ):
                sccs = kosaraju(source_vertex, return_sccs=True)
                for scc in sccs:
                    scc.compute_image()
                    scc.compute_counterimage()

                scc_finishing_time = scc_finishing_time_list(sccs)

                propagate_nwf(source_vertex.scc, scc_finishing_time)
                return merge_split_phase(qpartition, finishing_time_list)
            else:
                if source_vertex.wf:
                    if destination_vertex.wf:
                        # we already know that u.rank <= v.rank
                        source_vertex.rank = destination_vertex.rank + 1
                        topological_sorted_wf = None
                        propagate_wf(
                            source_vertex,
                            well_founded_topological,
                            scc_finishing_time,
                        )
                    # u becomes non-well-founded
                    else:
                        if source_vertex.rank < destination_vertex.rank:
                            source_vertex.rank = destination_vertex.rank

                            propagate_nwf(
                                source_vertex.scc, scc_finishing_time
                            )
                else:
                    if source_vertex.rank < destination_vertex.rank:
                        source_vertex.rank = destination_vertex.rank

                        # we don't need to update the nwf list since
                        # source_vertex was already nwf

                        propagate_nwf(source_vertex.scc, scc_finishing_time)

                merge_phase(source_vertex.qblock, destination_vertex.qblock)
                return filter_deteached(qpartition)
