import networkx as nx
from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _QBlock as _Block,
    _Edge,
    _Count,
    _XBlock,
)
from typing import List, Tuple
from .ranked_pta import ranked_split, pta
from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
    compute_finishing_time_list,
)
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    build_vertexes_image,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    build_block_counterimage,
)
from itertools import product


def add_edge(source: _Vertex, destination: _Vertex) -> _Edge:
    edge = _Edge(source, destination)
    if len(source.image) > 0:
        # there's already a _Count instance for the image of this Vertex,
        # therefore we HAVE to use it.
        edge.count = source.image[0].count
    else:
        edge.count = _Count(source)

    edge.count.value += 1

    source.add_to_image(edge)
    destination.add_to_counterimage(edge)

    return edge


def find_vertexes(
    partition: List[_Block], label1: int, label2: int
) -> Tuple[_Vertex, _Vertex]:
    source_vertex = None
    destination_vertex = None

    for block in partition:
        for node in block.vertexes:
            if node.label == label1:
                source_vertex = node
            if node.label == label2:
                destination_vertex = node

    if source_vertex is None:
        raise Exception(
            """It wasn't possible to determine the source vertex the new
            edge"""
        )
    if destination_vertex is None:
        raise Exception(
            """It wasn't possible to determine the destination vertex of the
            new edge"""
        )

    return (source_vertex, destination_vertex)


def check_old_blocks_relation(source_vertex, destination_vertex) -> bool:
    """If in the old RSCP [u] => [v], the addition of the new edge doesn't
    change the RSCP.

    Args:
        old_rscp (List[Tuple[int]]): The RSCP before the addition of the edge
            (each index of the outer-most list is linked to the rank of the
            blocks in the inner-most lists).
        new_edge (Tuple[_Vertex]): A tuple representing the new edge.

    Returns:
        bool: True if [u] => [v], False otherwise
    """

    # check if v is already in u's image
    for edge in source_vertex.image:
        if edge.destination.label == destination_vertex.label:
            return True

    # in fact the outer-most for-loop loops 2 times at most
    for vertex in source_vertex.qblock.vertexes:
        # we're interested in vertexes which aren't the source vertex of the
        # new edge.
        if vertex is not source_vertex:
            for edge in vertex.image:
                if edge.destination.qblock == destination_vertex.qblock:
                    return True
            # we visited the entire image of a single block (not u) of [u], and
            # it didn't contain an edge to [v], therefore we conclude (since
            # the old partition is stable if we don't consider the new edge)
            # that an edge from [u] to [v] can't exist
            return False
    # we didn't find an edge ([u] contains only u)
    return False


def check_new_scc(
    current_source: _Vertex,
    destination: _Vertex,
    finishing_time_list,
    min_rank: int = None,
    max_rank: int = None,
    visited_vertexes: List[_Vertex] = [],
    root_call=True,
) -> bool:
    # this is a consequence of the context where this function is used, keep
    # in mind when testing!
    if min_rank is None:
        min_rank = current_source.rank
    if max_rank is None:
        max_rank = destination.rank

    if root_call:
        current_source.visited = True
        current_source.qblock.visited = True
        visited_vertexes.append(current_source)

    for edge in current_source.counterimage:
        # we reached the block [v], therefore this is a new SCC
        if edge.source == destination:
            finishing_time_list.append(destination)
            destination.qblock.visited = True

            # the visit of the current source is over
            finishing_time_list.append(current_source)

            # clean visited vertexes
            for vertex in visited_vertexes:
                vertex.visited = False

            # we found that an SCC was created
            return True
        else:
            if (
                not edge.source.visited
                and min_rank <= edge.source.rank
                and edge.source.rank <= max_rank
            ):
                # we don't want to visit a vertex more than one time
                edge.source.visited = True
                visited_vertexes.append(edge.source)

                edge.source.qblock.visited = True

                # if at least one of the possible ramifications is True,
                # return True
                if check_new_scc(
                    edge.source,
                    destination,
                    finishing_time_list,
                    min_rank,
                    max_rank,
                    visited_vertexes,
                    root_call=False,
                ):
                    # one of the children of this vertex returned True
                    # therefore the visit of this node is over
                    finishing_time_list.append(current_source)

                    return True

    finishing_time_list.append(current_source)

    # we have to clean the flag "visited" for each visited vertex
    if root_call:
        for vx in visited_vertexes:
            vx.visited = False

    return False


def both_blocks_go_or_dont_go_to_block(
    block1: _Block, block2: _Block, block_counterimage: List[_Vertex]
) -> bool:
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
    block1: _Block, block2: _Block, check_visited: bool = False
) -> bool:
    def build_block_image(block):
        s = set()
        for v in block.vertexes:
            for edge in v.image:
                # if check_visited is true, we only want to consider
                # qblock visited in the first DFS (flag visited is true)
                if not (check_visited and edge.destination.qblock.visited):
                    s.add(id(edge.destination.qblock))
        return s

    block_image1 = build_block_image(block1)
    block_image2 = build_block_image(block2)

    return block_image1 != block_image2


def merge_condition(block1: _Block, block2: _Block) -> bool:
    if (
        block1.initial_partition_block_id()
        != block2.initial_partition_block_id()
    ):
        return False
    elif block1 == block2:
        return False
    elif block1.rank() != block2.rank():
        return False
    elif exists_causal_splitter(block1, block2):
        return False
    elif block1.deteached or block2.deteached:
        return False
    else:
        return True


def recursive_merge(block1: _Block, block2: _Block):
    block1.merge(block2)

    # construct a list of couples of blocks which needs to be verified
    verified_couples = {}

    for vx_couple in product(block1.vertexes, block2.vertexes):
        for counterimage_vx_couple in product(
            vx_couple[0].counterimage, vx_couple[1].counterimage
        ):
            b1 = counterimage_vx_couple[0].source.qblock
            b2 = counterimage_vx_couple[1].source.qblock

            if b1 == b2 or b1.deteached or b2.deteached:
                continue

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
    """If U1 => V && merge_condition(U,U1) then merge (U1,U). Then proceed
    recursively.

    Args:
        ublock (_Block):
        vblock (_Block):
    """
    for vertex in vblock.vertexes:
        for v1block in map(
            lambda edge: edge.source.qblock, vertex.counterimage
        ):
            if merge_condition(ublock, v1block):
                recursive_merge(ublock, v1block)


def merge_split_phase(qpartition, finishing_time_list, max_rank):
    # a dict of lists of blocks (the key is the initial partition ID)
    # where each couple can't be merged
    cant_merge_dict = {}

    # keep track in order to remove the 'visited' flag
    visited_vertexes = []

    # a partition containing all the touched blocks
    X = []

    def merge_split_step(vertex):
        vertex.visited = True
        visited_vertexes.append(vertex)

        for edge in vertex.image:
            if not vertex.visited:
                merge_split_phase(edge.destination)

        if not vertex.qblock.tried_merge:
            initial_partition_block_id = (
                vertex.qblock.initial_partition_block_id()
            )
            if initial_partition_block_id in cant_merge_dict:
                merged = False
                for qblock in cant_merge_dict[initial_partition_block_id]:
                    if not (
                        qblock.deteached
                        or exists_causal_splitter(
                            vertex.qblock, qblock, check_visited=True
                        )
                    ):
                        # it's preferable to deteach vertex.qblock to reduce the rubbish
                        recursive_merge(qblock, vertex.qblock)
                        merged = True
                        break
                if not merged:
                    cant_merge_dict[initial_partition_block_id].append(
                        vertex.qblock
                    )
            else:
                cant_merge_dict[initial_partition_block_id] = [vertex.qblock]
                # we only want to add to X here, since otherwise the block is merged with another one
                X.append(vertex.qblock)

            vertex.qblock.tried_merge = True

    # visit G in order of decreasing finishing times of the first DFS
    for vertex in finishing_time_list:
        # a vertex may be reached more than one time
        if not vertex.visited:
            merge_split_step(vertex)

    for vx in visited_vertexes:
        vx.visited = False

    for block in X:
        # this is needed for PTA
        block.xblock = _XBlock()
        # clean visited
        block.visited = False

        for vx in block.vertexes:
            # mark as visitable by PTA
            vx.allow_visit = True
            # remember which qblock you were in
            vx.old_qblock_id = id(vx.qblock)

    X2 = qblocks = pta(X)

    # keep track of the blocks which are the result of a split
    splitted_blocks = []

    for block in X2:
        for vx in block.vertexes:
            # clean allow_visit
            vx.allow_visit = False
            # check if changed
            if not vx.qblock.visited and vx.old_qblock_id != id(vx.qblock):
                ranked_split(None, vx.qblock, max_rank)
                vx.qblock.visited = True
                splitted_blocks.append(vx.qblock)

    # clean block.visited
    for block in splitted_blocks:
        block.visited = False


def propagate_wf(vertex: _Vertex, well_founded_topological: List[_Vertex]):
    """Recursively visit the well-founded counterimage of the given vertex and
    update the ranks. The visit is in increasing order of rank. It can be shown
    easily that this is the only way to get correct results.

    Args:
        vertex (_Vertex): The updated vertex (source of the new edge). The rank
        must already be updated.
        well_founded_topological (List[_Vertex]): List of WF vertexes of the
        graph in topological order.
    """

    # find the index of the updated vertex. we only need to update ranks of the
    # wf part of the graph which is "before" this vertex in the topological
    # list
    until_idx = None
    for idx, vx in enumerate(well_founded_topological):
        if vertex == vx:
            until_idx = idx
            break

    # O(E)
    # update the ranks
    for idx in range(until_idx - 1, -1, -1):
        mx = float("-inf")
        for edge in well_founded_topological[idx].image:
            if edge.destination.wf:
                mx = max(mx, edge.destination.rank + 1)
        well_founded_topological[idx].rank = mx

    # propagate the changes also to nwf nodes
    for idx in range(until_idx, -1, -1):
        for edge in well_founded_topological[idx].counterimage:
            if not edge.source.wf:
                propagate_nwf(edge.source)


def propagate_nwf(vertexes: List[_Vertex]):
    # temporary: use the standard algorithm for rank computation
    finishing_time_list = compute_finishing_time_list(vertexes)
    build_vertexes_image(finishing_time_list)

    # sets ranks
    compute_rank(vertexes, finishing_time_list)


def update_rscp(
    old_rscp: List[_Block],
    new_edge: Tuple[int, int],
    well_founded_topological: List[_Vertex],
    vertexes: List[_Vertex],
):
    source_vertex, destination_vertex = find_vertexes(old_rscp)

    # if the new edge connects two blocks A,B such that A => B before the edge
    # is added we don't need to do anything
    if check_old_blocks_relation(
        old_rscp, (source_vertex, destination_vertex)
    ):
        return old_rscp
    else:
        # update the graph representation
        add_edge(source_vertex, destination_vertex)

        ranked_split(old_rscp, destination_vertex.qblock)

        # u isn't well founded, v is well founded
        if not source_vertex.wf and destination_vertex.wf:
            # if necessary, update the rank of u and propagate the changes
            if destination_vertex.rank + 1 > source_vertex.rank:
                source_vertex.rank = destination_vertex.rank + 1
                propagate_nwf(vertexes)
            merge_phase(source_vertex.qblock, destination_vertex.qblock)
        else:
            # in this case we don't need to update the rank
            if source_vertex.rank > destination_vertex.rank:
                merge_phase(source_vertex.qblock, destination_vertex.qblock)
            else:
                # we want to save the finishing time list
                finishing_time_list = []

                # in this case u is part of the new SCC (which contains also
                # v), therefore it isn't well founded
                if check_new_scc(
                    source_vertex,
                    destination_vertex,
                    finishing_time_list,
                    source_vertex.rank,
                    destination_vertex.rank,
                ):
                    # if you replace propagate_nwf with the right
                    # implementation you also need to update the rank of
                    # nodes in the new SCC, with the current implementation
                    # they are update by propagate_nwf
                    propagate_nwf(vertexes)
                    merge_split_phase(finishing_time_list)
                else:
                    if source_vertex.wf:
                        if destination_vertex.wf:
                            # we already know that u.rank <= v.rank
                            source_vertex.rank = destination_vertex.rank + 1
                            topological_sorted_wf = None
                            propagate_wf(source_vertex, None)
                        # u becomes non-well-founded
                        else:
                            if source_vertex.rank < destination_vertex.rank:
                                source_vertex.rank = destination_vertex.rank
                                propagate_nwf(vertexes)
                    else:
                        if source_vertex.rank < destination_vertex.rank:
                            source_vertex.rank = destination_vertex.rank
                            propagate_nwf(vertexes)

                    merge_phase(
                        source_vertex.qblock, destination_vertex.qblock
                    )
