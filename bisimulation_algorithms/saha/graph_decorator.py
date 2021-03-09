import networkx as nx
from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _Edge,
    _Count,
    _QBlock
)
from typing import List, Tuple
from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
    compute_finishing_time_list,
)


def to_normal_graph(
    graph: nx.Graph, initial_partition: List[Tuple[int]]
) -> List[_Vertex]:
    if initial_partition is None:
        initial_partition = [tuple(i for i in range(len(graph.nodes)))]

    # map vertex to its qblock and initial partition idx
    vertex_to_qblock = [None for _ in graph.nodes]

    for idx,block in enumerate(initial_partition):
        qblock = _QBlock([], None)
        for vx in block:
            vertex_to_qblock[vx] = (qblock,idx)

    vertexes = []
    for vertex in graph.nodes:
        new_vertex = _Vertex(label=vertex)
        vertexes.append(new_vertex)
        qblock, idx = vertex_to_qblock[vertex]
        qblock.append_vertex(new_vertex)
        new_vertex.initial_partition_block_id = idx

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

        my_edge.source.add_to_image(my_edge)
        my_edge.destination.add_to_counterimage(my_edge)

    return vertexes


def build_vertexes_image(finishing_time_list: List[_Vertex]):
    # use the standard vertex ordering
    vertex_count = [None for _ in range(len(finishing_time_list))]

    for time_list_idx in range(len(finishing_time_list) - 1, -1, -1):
        vertex = finishing_time_list[time_list_idx]

        # use the counterimage of the current vertex to update the images of
        # the nodes in the counterimage of the current vertex.
        for edge in vertex.counterimage:
            edge.source.add_to_image(edge)


def prepare_graph(
    graph: nx.Graph, initial_partition: List[Tuple[int]]=None
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

    vertexes = to_normal_graph(graph, initial_partition)

    finishing_time_list = compute_finishing_time_list(vertexes)
    build_vertexes_image(finishing_time_list)

    # sets ranks
    compute_rank(vertexes, finishing_time_list)

    return vertexes
