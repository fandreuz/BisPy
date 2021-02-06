import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Vertex,
    _Block,
)
from bisimulation_algorithms.paige_tarjan.graph_entities import _Edge, _Count
from typing import List, Tuple
from .ranked_pta import ranked_split
from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
    compute_finishing_time_list,
)
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    build_vertexes_image,
)


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


def find_new_scc(
    vertexes: List[_Vertex], source: _Vertex, destination: _Vertex
) -> List[_Vertex]:
    return True


def merge_phase(ublock: _Block, vblock: _Block):
    pass


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
                # determine if a new SCC is formed due to the addition of the
                # new edge
                new_scc = find_new_scc()

                # in this case u is part of the new SCC (which contains also
                # v), therefore it isn't well founded
                if new_scc is not None:
                    for vertex in new_scc:
                        vertex.wf = False
                        # each vertex of the SCC has the same rank
                        vertex.rank = destination_vertex.rank
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
