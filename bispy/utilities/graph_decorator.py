import networkx as nx
from bispy.utilities.graph_entities import (
    _Vertex,
    _Edge,
    _Count,
    _QBlock,
    _XBlock,
)
from typing import List, Tuple, Union
from bispy.utilities.rank_computation import compute_rank as func_compute_rank

_BLACK = 10
_GRAY = 11
_WHITE = 12


# this is a FUNDAMENTAL part of the PTA algorithm: we need a stable initial
# partition with respect to the set V, but a partition where leafs and
# non-leafs are in the same block can't be stable
def preprocess_initial_partition(
    vertexes: List[_Vertex], initial_partition: List[Tuple[int]]
) -> List[_QBlock]:
    """
    Preprocess the given partition to split blocks which contain both leafs and
    non-leafs. This is a fundamental hypothesis in order to make
    *Paige-Tarjan*'s algorithm work.

    The attribute `qblock` of each vertex must already have been initialized.

    :param vertexes: Vertexes in the graph.
    :param initial_partition: The initial partition, as a list of
        vertexes index.
    :returns: The preprocessed partition, as a list of
        :class:`bispy.utilities.graph_entities_QBlock`.
    """

    new_partition = []
    for ip_block in initial_partition:
        qblock = vertexes[ip_block[0]].qblock

        leafs = []

        for vertex_idx in ip_block:
            if vertexes[vertex_idx].qblock != qblock:
                raise ValueError("Given vertexes already preprocessed.")

            if len(vertexes[vertex_idx].image) == 0:
                leafs.append(vertexes[vertex_idx])

        # if at least one is zero, this block is OK
        if len(leafs) == 0 or len(leafs) == qblock.size:
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
    """
    Recursively visit :math:`G^{-1}` starting from the vertex in the position
    `current_vertex_idx` of the list `vertexes`. Meanwhile fill
    `finishing_list` everytime time the counterimage of a vertex is completely
    visited.

    :param current_vertex_idx: The current vertex to be visited.
    :param vertexes: List of vertexes in the graph.
    :param finishing_list: List of vertexes in order of increasing finishing
        time. Must be passed (as an empty list) upon the first call of the
        function. The list will be filled when the function returns.
    :param colors: List of color (one for each vertex) maintained by the
        algorithm to prevent visiting the same vertex more than once. Must be
        passed by the user (all values **must** be `_WHITE`) upon the
        first call of the function.
    """

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
    """
    Compute the finishing time of each vertex of :math:`G` for a DFS
    of :math:`G^{-1}`.

    :param vertexes: Vertexes of :math:`G`.
    """

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
) -> Tuple[List[_Vertex], List[_QBlock]]:
    """
    Create the *BisPy* representation of the given graph. There are several
    options to enable/disable depending on which algorithm in *BisPy* you
    plan to use.

    :param graph: The graph.
    :param initial_partition: The initial partition (or labeling set) imposed
        on vertexes of the graph. Used to divide nodes in blocks.
    :param build_image: If `True`, we compute the image of each vertex.
    :param set_count: If `True`, we set the attribute `count` of each vertex
        to an appropriate instance of
        :class:`bispy.utilities.graph_entities._Count`.
    :param set_xblock: If `True` we set the attribute `xblock` of each block
        of the partition to an instance of
        :class:`bispy.utilities.graph_entities._XBlock` (the same for each
        block). If `False`, we set the attribute to `None`.
    :returns: A tuple whose items are:

        0. List of vertexes in the graph;
        1. List of blocks in the initial partition.

        Both the items are in *BisPy* representation.
    """

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

    return (vertexes, qblocks)


# this re-arranges the image of each vertex in a convenient order for further
# visits
def build_vertexes_image(finishing_time_list: List[_Vertex]):
    """
    Build the image of each vertex in the graph in a convenient order to
    facilitate further computations (like the *rank*). Vertexes in the
    constructed image are arranged in inverse order of finishing time for a DFS
    on :math:`G^{-1}`.

    :param finishing_time_list: Vertexes of :math:`G` in order of increasing
        finishing time for a DFS on :math:`G^{-1}`.
    """

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
    set_count: bool = True,
    topological_sorted_images: bool = True,
    compute_rank: bool = True,
    set_xblock: bool = True,
    preprocess: bool = True,
) -> Tuple[List[_Vertex], List[_QBlock]]:
    """
    Create the *BisPy* representation of the given graph.

    :param graph: The graph, in *NetworkX* representation.
    :param initial_partition: The initial partition, or labeling set, imposed
        on the nodes of the graph. Defaults to `None`, in which case the
        trivial labeling set is considered (one block which contains all the
        nodes).
    :param set_count: If `True`, we set the attribute `count` of each vertex
        to an appropriate instance of
        :class:`bispy.utilities.graph_entities._Count`. If `False`, the
        attribute is set to `None`. Defaults to `True`.
    :param topological_sorted_images: If `True`, the image of each vertex
        is computed using the function :func:`build_vertexes_image`. If
        `False`, the image is computed without any particular precautions.
        Defaults to `True`.
    :param compute_rank: If `True`, the function computes the *rank* of each
        vertex. May be useless for some algorithms, like *Paige-Tarjan*'s,
        in which case performance can be slightly improved by setting this
        parameter to `False`. Defaults to `True`.
    :param set_xblock: If `True` we set the attribute `xblock` of each block
        of the partition to an instance of
        :class:`bispy.utilities.graph_entities._XBlock` (the same for each
        block). If `False`, we set the attribute to `None`. Defaults to `True`.
    :param preprocess: Preprocess the initial partition to split blocks which
        contain both leafs and non-leafs. Fundamental for *Paige-Tarjan*'s
        algorithm, may be disabled for other algorithms.
    :returns: A tuple whose items are:

        0. List of vertexes of the graph;
        1. List of blocks of the initial partition.

        Both items are in *BisPy* representation.
    """

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
        return (tp[0], qpartition)
    else:
        return tp


def decorate_bispy_graph(
    vertexes: List[_Vertex],
    initial_partition: List[Tuple[int]] = None,
    set_initial_partition_data: bool = False,
    set_count: bool = True,
    topological_sorted_images: bool = True,
    compute_rank: bool = True,
    preprocess: bool = True,
) -> Union[None, Tuple[List[_Vertex], List[_QBlock]]]:
    """
    Update the *BisPy* representation of the given graph with more information.

    :param vertexes: The vertexes of the graph, in *BisPy* representation.
    :param initial_partition: The initial partition, or labeling set, imposed
        on the nodes of the graph. Defaults to `None`, in which case the
        trivial labeling set is considered (one block which contains all the
        nodes).
    :param set_initial_partition_data: If `True`, for each vertex we set the
        attribute `initial_partition_block_id` to remember the block of the
        initial partition to which that vertex belongs. May be used by some
        algorithms (like *Saha*, in :func:`bispy.saha.saha.merge_condition`).
    :param set_count: If `True`, we set the attribute `count` of each vertex
        to an appropriate instance of
        :class:`bispy.utilities.graph_entities._Count`. If `False`, the
        attribute is set to `None`. Defaults to `True`.
    :param topological_sorted_images: If `True`, the image of each vertex
        is computed using the function :func:`build_vertexes_image`. If
        `False`, the image is computed without any particular precautions.
        Defaults to `True`.
    :param compute_rank: If `True`, the function computes the *rank* of each
        vertex. May be useless for some algorithms, like *Paige-Tarjan*'s,
        in which case performance can be slightly improved by setting this
        parameter to `False`. Defaults to `True`.
    :param preprocess: Preprocess the initial partition to split blocks which
        contain both leafs and non-leafs. Fundamental for *Paige-Tarjan*'s
        algorithm, may be disabled for other algorithms.
    :returns: `None` if `preprocess` is `False`; otherwise a tuple whose items
        are:

        0. List of vertexes of the graph;
        1. List of blocks of the initial partition.

        Both items are in *BisPy* representation.
    """

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


def to_tuple_list(qblocks: List[_QBlock]) -> List[Tuple]:
    """Convert the given partition (represented by a list of
    :class:`bispy.utilities.graph_entities._QBlock`) to a list of tuples. The
    blocks of the resulting partition contain the labels of the vertexes
    in the corresponding blocks of `qblocks`.

    :param qblocks: A partition.
    """
    return [
        tuple(map(lambda vertex: vertex.label, block.vertexes))
        for block in qblocks
    ]
