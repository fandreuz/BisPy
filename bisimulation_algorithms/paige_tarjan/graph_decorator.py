import itertools
import networkx as nx
from typing import List, Tuple

from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _Edge,
    _XBlock,
    _QBlock,
    _Count,
    compute_initial_partition_block_id
)


def prepare_graph_abstraction(graph: nx.Graph) -> List[_Vertex]:
    """Acquires an input graph, and outputs a representation of that graph
    which can be used by the algorithm. This function computes the image and
    counterimage for each _Vertex, and creates the needed instances of _Edge.
    Vertexes are indexed and labeled following their order in the given
    graph.nodes entity.

    Args:
        graph ([nx.Graph]): The input graph.

    Returns:
        list[_Vertex]: A list of _Vertexes which represents the input graph.
    """

    vertexes = [_Vertex(idx) for idx in range(len(graph.nodes))]

    # holds the references to Count objects to assign to the edges (this is OK
    # because we can consider |V| = O(|E|))
    # count(x) = count(x,V) = |V \cap E({x})| = |E({x})|
    vertex_count = [None for _ in graph.nodes]

    # a vertex should always refer to a ddllistnode, in order to help if
    # fellows to be splitted (i.e. not obtain the error "dllistnode belongs to
    # another list")
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


def build_qpartition(
    vertexes: List[_Vertex], initial_partition: List[Tuple[int]]
) -> List[_QBlock]:
    """Constructs the initial Q partition given the list of Vertexes and the
    initial_partition. This function fails if the length of the initial
    partition is not equal to the number of vertexes in the list.

    Args:
        vertexes (list[_Vertex]): The list of Vertexes which represents the
            graph.
        initial_partition (list[Tuple[int]]): The initial partition as a list
            of vertex indexes partitioned in tuples.

    Returns:
        list[_QBlock]: The initial partition Q as a list of QBlocks.
    """

    union = set()
    # check number of vertexes and initial partition
    for block in initial_partition:
        old_length = len(union)
        union = union.union(block)

        if old_length + len(block) != len(union):
            raise Exception(
                """there shouldn't be overlapse within blocks of
                    initial_partition"""
            )

    if len(union) < len(vertexes):
        raise Exception("""initial_partition contains duplicate vertexes""")

    if len(union) < len(vertexes):
        raise Exception(
            """initial_partition contains more vertexes than expected"""
        )
    # end

    # initially X contains only one block
    initial_x_block = _XBlock()
    x_partition = [initial_x_block]

    # create the partition Q
    q_partition = []
    # create the blocks of partition Q using the initial_partition
    for block in initial_partition:
        # _QBlocks are initially created empty in order to obtain a reference
        # to dllistnode for vertexes and avoid a double visit of vertexes
        qblock = _QBlock([], initial_x_block)

        for idx in block:
            vertexes[idx] = vertexes[idx]

            # append this vertex to the dllist in qblock
            qblock.append_vertex(vertexes[idx])

        q_partition.append(qblock)

    return q_partition


# this is a FUNDAMENTAL part of the algorithm: we need a stable initial
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
    for block in initial_partition:
        leafs = []
        non_leafs = []

        for vertex_idx in block:
            if len(vertexes[vertex_idx].image) == 0:
                leafs.append(vertex_idx)
            else:
                non_leafs.append(vertex_idx)

        # if at least one is zero, this block is OK
        if len(leafs) * len(non_leafs) == 0:
            new_partition.append(block)
        else:
            new_partition.extend([leafs, non_leafs])

    return new_partition


def initialize(
    graph: nx.Graph, initial_partition: List[Tuple]
) -> (List[_QBlock], List[_Vertex]):
    """Packs the needed processing for a graph (prepare_graph_abstraction,
    preprocess_initial_partition, build_qpartition).

    Args:
        graph (nx.Graph, initial_partition): The input graph.
        list ([type]): The initial partition as a list of vertex indexes
            partitioned in tuples.

    Returns:
        tuple: a tuple whose first item is a list of QBlocks, and whose second
            item is the list of Vertexes which represents the graph.
    """

    vertexes = prepare_graph_abstraction(graph)

    if initial_partition is not None:
        vertex_to_id = [None for _ in graph.nodes]

        for block in initial_partition:
            block_id = compute_initial_partition_block_id(block)
            for vertex in block:
                vertex_to_id[vertex] = block_id

        for vertex in vertexes:
            vertex.initial_partition_block_id = vertex_to_id[vertex.label]

    processed_partition = preprocess_initial_partition(
        vertexes, initial_partition
    )
    return (build_qpartition(vertexes, processed_partition), vertexes)
