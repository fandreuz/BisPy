import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Vertex,
    _Block,
)
from bisimulation_algorithms.paige_tarjan.graph_entities import _Edge, _Count
from typing import List, Tuple


def add_edge(
    source: _Vertex, destination: _Vertex, partition: List[_Block]
) -> _Edge:
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
    partition: List[List[_Block]], label1: int, label2: int
) -> Tuple[_Vertex, _Vertex]:
    source_vertex = None
    destination_vertex = None

    for rank in partition:
        for block in rank:
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


def update_rscp(
    old_rscp: List[List[_Block]],
    new_edge: Tuple[int, int],
    initial_partition: List[Tuple[int]],
):
    """ source_vertex, destination_vertex = find_vertexes_and_blocks(old_rscp)

    # if the new edge connects two blocks A,B such that A => B before the edge
    # is added we don't need to do anything
    if check_old_blocks_relation(
        old_rscp, (source_vertex, destination_vertex)
    ):
        return old_rscp

    # update the graph representation """
    pass
