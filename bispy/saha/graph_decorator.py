import networkx as nx
from bispy.utilities.graph_entities import (
    _Vertex,
    _Edge,
    _Count,
    _QBlock,
)
from typing import List, Tuple
from bispy.utilities.rank_computation import (
    compute_rank,
)
from bispy.dovier_piazza_policriti.graph_decorator import (
    build_vertexes_image,
    compute_counterimage_finishing_time_list
)


def to_normal_graph(
    graph: nx.Graph, initial_partition: List[Tuple[int]]
) -> List[_Vertex]:
    if initial_partition is None:
        initial_partition = [tuple(i for i in range(len(graph.nodes)))]

    # instantiate QBlocks and Vertexes, put Vertexes into QBlocks and set their
    # initial block id
    vertexes = []
    qblocks = []
    for idx, block in enumerate(initial_partition):
        qblock = _QBlock([], None)
        qblocks.append(qblock)
        for vx in block:
            new_vertex = _Vertex(label=vx)
            vertexes.append(new_vertex)
            qblock.append_vertex(new_vertex)
            new_vertex.initial_partition_block_id = idx

    vertexes.sort(key=lambda vx: vx.label)

    # holds the references to Count objects to assign to the edges (this is OK
    # because we can consider |V| = O(|E|))
    # count(x) = count(x,V) = |V \cap E({x})| = |E({x})|
    vertex_count = [None for _ in graph.nodes]

    # build the counterimage. the image will be constructed using the order
    # imposed by the rank algorithm
    for edge in graph.edges:
        # create an instance of my class Edge
        my_edge = _Edge(vertexes[edge[0]], vertexes[edge[1]])

        # if this is the first outgoing edge for the vertex edge[0], we need to
        # create a new Count instance
        if not vertex_count[edge[0]]:
            # in this case None represents the intitial XBlock, namely the
            # whole V
            vertex_count[edge[0]] = _Count(my_edge.source)

        my_edge.count = vertex_count[edge[0]]
        my_edge.count.value += 1

        # the edge will be added to the image in build_vertexes_image
        # my_edge.source.add_to_image(my_edge)
        my_edge.destination.add_to_counterimage(my_edge)

    return (vertexes, qblocks)


def prepare_nx_graph(
    graph: nx.Graph, initial_partition: List[Tuple[int]] = None
) -> List[_Vertex]:
    """Prepare the input graph for the algorithm. Computes the rank for each
    node, and then converts the graph to a usable representation.

    Args:
        graph (nx.Graph): The input graph
        initial_partition(List[Tuple[int]]): The initial partition

    Returns:
        List[_Vertex]: A convenient representation of the given graph (contains
            only nodes and edges).
        int          : The maximum rank in the graph.
    """

    vertexes, qblocks = to_normal_graph(graph, initial_partition)

    finishing_time_list = compute_counterimage_finishing_time_list(vertexes)
    build_vertexes_image(finishing_time_list)

    # sets ranks
    compute_rank(vertexes)

    return (vertexes, qblocks)


def prepare_internal_graph(vertexes, initial_partition):
    if initial_partition is not None:
        # set Vertexes initial block id
        for idx, block in enumerate(initial_partition):
            for vx in block:
                vertexes[vx].initial_partition_block_id = idx
                # also delete the image, since we're going to call
                # build_vertexes_image next
                vertexes[vx].image = []
    else:
        for vx in vertexes:
            vx.initial_partition_block_id = None
            # also delete the image, since we're going to call
            # build_vertexes_image next
            vertexes[vx].image = []

    # set count reference
    for vertex in vertexes:
        count = _Count(vertex)
        for edge in vertex.image:
            edge.count = count
            edge.count.value += 1

    finishing_time_list = compute_counterimage_finishing_time_list(vertexes)
    build_vertexes_image(finishing_time_list)

    # sets ranks
    compute_rank(vertexes)
