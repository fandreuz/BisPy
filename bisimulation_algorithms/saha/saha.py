import networkx as nx
from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _QBlock as _Block,
    _Edge,
    _Count,
)
from typing import List, Tuple
from .ranked_pta import ranked_split
from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
    compute_finishing_time_list,
)
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    build_vertexes_image,
)
from bisimulation_algorithms.paige_tarjan.pta import build_block_counterimage


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

    for edge in current_source.counterimage:
        # we reached the block [v], therefore this is a new SCC
        if edge.source == destination:
            for vertex in visited_vertexes:
                vertex.visited = False

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
                    min_rank,
                    max_rank,
                    visited_vertexes,
                    root_call=False,
                ):
                    return True

    # we have to clean the flag "visited" for each visited vertex
    if root_call:
        for vx in visited_vertexes:
            vx.visited = False

    return False


def exists_causal_splitter(
    block1: _Block, block2: _Block, blocks_and_counterimages: List[Tuple]
) -> bool:
    for block, counterimage in blocks_and_counterimages:
        block1_goes_to = False
        block2_goes_to = False
        for vertex in counterimage:
            if vertex.qblock == block1:
                block1_goes_to = True
            elif vertex.qblock == block2:
                block2_goes_to = True

        # one goes, the other one doesn't
        if block1_goes_to != block2_goes_to:
            return True


def merge_condition(
    block1: _Block, block2: _Block, blocks_and_counterimages: List[Tuple]
) -> bool:
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
    else:
        return True


def recursive_merge(
    block1: _Block,
    block2: _Block,
    block1_counterimage: List[_Vertex],
    block2_counterimage: List[_Vertex],
):
    block1.merge(block2)

    block1_predecessor_blocks = []
    for vertex in block1_counterimage:
        for vertex2 in block2_counterimage:
            if not (
                (vertex.qblock == block1 and vertex2.qblock == block2)
                or (vertex.qblock == block2 and vertex2.qblock == block1)
            ):
                if merge_condition(vertex.qblock, vertex2.qblock):
                    recursive_merge(vertex.qblock, vertex2.qblock)


def merge_phase(
    ublock: _Block, vblock: _Block, blocks_and_counterimages: List[Tuple]
):
    for block, counterimage in blocks_and_counterimages:
        if block == vblock:
            for vertex in counterimage:
                if merge_condition(ublock, vertex.qblock):
                    recursive_merge(ublock, vertex.qblock)


def merge_split_phase():
    pass


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
    # wf part of the graph which is "before" this vertex in the topological list
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
    initial_partition: List[Tuple[int]],
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
                # in this case u is part of the new SCC (which contains also
                # v), therefore it isn't well founded
                if check_new_scc(
                    source_vertex,
                    destination_vertex,
                    source_vertex.rank,
                    destination_vertex.rank,
                ):
                    # if you replace propagate_nwf with the right
                    # implementation you also need to update the rank of
                    # nodes in the new SCC, with the current implementation
                    # they are update by propagate_nwf
                    propagate_nwf(vertexes)
                    merge_split_phase()
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
