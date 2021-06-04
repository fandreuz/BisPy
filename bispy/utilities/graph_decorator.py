import networkx as nx
from bispy.utilities.graph_entities import (
    _Vertex,
    _Edge,
    _Count,
    _QBlock,
    _XBlock,
)
from typing import List, Tuple
from bispy.utilities.rank_computation import compute_rank as func_compute_rank

_BLACK = 10
_GRAY = 11
_WHITE = 12

# this is a FUNDAMENTAL part of the PTA algorithm: we need a stable initial
# partition with respect to the set V, but a partition where leafs and
# non-leafs are in the same block can't be stable
def preprocess_initial_partition(
    vertexes: List[_Vertex], initial_partition: List[tuple]
) -> List[tuple]:
    """Splits each block A of the initial Q partition in the intersection of A
    and E^{-1}(V) and A - E^{-1}(V). The result is a partition where each block
    contains zero or all leafs. This procedure is fundamental for obtaining a
    partition stable with respect to V, which is an hypothesis that the
    algorithms needs in order to work.

    Args:
        vertexes (list[_Vertex]): The list of Vertexes which represents the
            graph.
        initial_partition (list[tuple]): The partition to be processed.

    Returns:
        list[tuple]: A partition where each block contains zero or only leafs.
    """

    new_partition = []
    for ip_block in initial_partition:
        qblock = vertexes[ip_block[0]].qblock

        leafs = []

        for vertex_idx in ip_block:
            if len(vertexes[vertex_idx].image) == 0:
                leafs.append(vertexes[vertex_idx])

        # if at least one is zero, this block is OK
        if len(leafs) == 0:
            new_partition.append(qblock)
        else:
            new_partition.extend([qblock, qblock.fast_mitosis(leafs)])

    return new_partition


def counterimage_dfs(
    current_vertex_idx: int,
    vertexes: List[_Vertex],
    finishing_list: List[_Vertex],
    colors: List[int],
):
    # mark this vertex as "visiting"
    colors[current_vertex_idx] = _GRAY
    # visit the counterimage of the current vertex
    for edge in vertexes[current_vertex_idx].counterimage:
        counterimage_vertex = edge.source

        # if the vertex isn't white, a visit is occurring, or has already
        # occurred.
        if colors[counterimage_vertex.label] == _WHITE:
            counterimage_dfs(
                current_vertex_idx=counterimage_vertex.label,
                vertexes=vertexes,
                finishing_list=finishing_list,
                colors=colors,
            )
    # this vertex visit is over: add the vertex to the ordered list of
    # finished vertexes
    finishing_list.append(vertexes[current_vertex_idx])
    # mark this vertex as "visited"
    colors[current_vertex_idx] = _BLACK


def compute_counterimage_finishing_time_list(
    vertexes: List[_Vertex],
) -> List[_Vertex]:
    counterimage_dfs_colors = [_WHITE for _ in range(len(vertexes))]
    counterimage_finishing_list = []
    # perform counterimage DFS
    for idx in range(len(vertexes)):
        if counterimage_dfs_colors[idx] == _WHITE:
            counterimage_dfs(
                current_vertex_idx=idx,
                vertexes=vertexes,
                finishing_list=counterimage_finishing_list,
                colors=counterimage_dfs_colors,
            )
    return counterimage_finishing_list


def as_bispy_graph(
    graph: nx.Graph,
    initial_partition: List[Tuple[int]],
    build_image,
    set_count,
    set_xblock,
) -> Tuple[List[_Vertex], List[_QBlock], _XBlock]:
    # instantiate QBlocks and Vertexes, put Vertexes into QBlocks and set their
    # initial block id
    vertexes = [None for _ in graph.nodes]
    qblocks = []

    initial_x_block = _XBlock() if set_xblock else None

    for idx, block in enumerate(initial_partition):
        qblock = _QBlock([], initial_x_block)
        qblocks.append(qblock)
        for vx in block:
            new_vertex = _Vertex(label=vx)
            vertexes[vx] = new_vertex
            qblock.append_vertex(new_vertex)
            new_vertex.initial_partition_block_id = idx

    if set_count:
        # holds the references to Count objects to assign to the edges.
        # count(x) = count(x,V) = |V \cap E({x})| = |E({x})|
        vertex_count = [None for _ in graph.nodes]
    else:
        vertex_count = None

    # build the counterimage. the image will be constructed using the order
    # imposed by the rank algorithm
    for edge in graph.edges:
        # create an instance of my class Edge
        my_edge = _Edge(vertexes[edge[0]], vertexes[edge[1]])

        if set_count:
            # if this is the first outgoing edge for the vertex edge[0], we
            # need to create a new Count instance
            if not vertex_count[edge[0]]:
                # in this case None represents the intitial XBlock, namely the
                # whole V
                vertex_count[edge[0]] = _Count(my_edge.source)

            my_edge.count = vertex_count[edge[0]]
            my_edge.count.value += 1

        if build_image:
            my_edge.source.add_to_image(my_edge)
        my_edge.destination.add_to_counterimage(my_edge)

    if set_xblock:
        return (vertexes, qblocks, initial_x_block)
    else:
        return (vertexes, qblocks)


# this re-arranges the image of each vertex in a convenient order for further
# visits
def build_vertexes_image(finishing_time_list: List[_Vertex]):
    # use the standard vertex ordering
    vertex_count = [None for _ in range(len(finishing_time_list))]

    visited_vertexes = []
    for time_list_idx in range(len(finishing_time_list) - 1, -1, -1):
        vertex = finishing_time_list[time_list_idx]

        # use the counterimage of the current vertex to update the images of
        # the nodes in the counterimage of the current vertex.
        for edge in vertex.counterimage:
            # we don't want to duplicate an already existent image, therefore
            # we reset the image of each vertex we visit
            if not edge.source.visited:
                edge.source.visit()
                edge.source.image = []
                visited_vertexes.append(edge.source)

            edge.source.add_to_image(edge)

    # unvisit vertexes
    for visited_vx in visited_vertexes:
        visited_vx.release()


def decorate_nx_graph(
    graph: nx.Graph,
    initial_partition: List[Tuple[int]] = None,
    set_count=True,
    topological_sorted_images=True,
    compute_rank=True,
    set_xblock=False,
    preprocess=False,
) -> Tuple[List[_Vertex], List[_QBlock]]:
    if initial_partition is None:
        initial_partition = [tuple(i for i in range(len(graph.nodes)))]

    tp = as_bispy_graph(
        graph,
        initial_partition,
        set_count=set_count,
        build_image=(not topological_sorted_images),
        set_xblock=set_xblock,
    )

    qpartition = decorate_bispy_graph(
        tp[0],
        # we have already done everything about initial_partition data into
        # vertexes
        set_initial_partition_data=False,
        initial_partition=initial_partition,
        set_count=False,
        topological_sorted_images=topological_sorted_images,
        compute_rank=compute_rank,
        preprocess=preprocess,
    )

    if qpartition is not None:
        if len(tp) == 3:
            return (tp[0], qpartition, tp[2])
        else:
            return (tp[0], qpartition)
    else:
        return tp


def decorate_bispy_graph(
    vertexes,
    initial_partition=None,
    set_initial_partition_data=False,
    set_count=True,
    topological_sorted_images=True,
    compute_rank=True,
    preprocess=False,
):
    # if initial_partition is False we do not loop over vertexes to set
    # the ID of initial partition (saves time)
    if set_initial_partition_data:
        if initial_partition is not None:
            # set Vertexes initial block id
            for idx, block in enumerate(initial_partition):
                for vx in block:
                    vertexes[vx].initial_partition_block_id = idx
        else:
            for vx in vertexes:
                vx.initial_partition_block_id = None

    if initial_partition is None:
        initial_partition = [tuple(v.label for v in vertexes)]

    if set_count:
        # set count reference
        for vertex in vertexes:
            count = _Count(vertex)
            for edge in vertex.image:
                edge.count = count
                edge.count.value += 1

    if topological_sorted_images:
        finishing_time_list = compute_counterimage_finishing_time_list(
            vertexes
        )
        build_vertexes_image(finishing_time_list)

    if compute_rank:
        func_compute_rank(vertexes)

    if preprocess:
        return preprocess_initial_partition(vertexes, initial_partition)
