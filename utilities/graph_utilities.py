import itertools
from graph_entities import *

def parse_graph(graph):
    vertexes = [Vertex(idx) for idx in range(len(graph.nodes))]

    # holds the references to Count objects to assign to the edges (this is OK because we can consider |V| = O(|E|))
    # count(x) = count(x,V) = |V \cap E({x})| = |E({x})|
    vertex_count = [None for _ in graph.nodes]

    # a vertex should always refer to a ddllistnode, in order to help if fellows to be splitted (i.e. not obtain the error "dllistnode belongs to another list")
    for edge in graph.edges:
        # create an instance of my class Edge
        my_edge = Edge(vertexes[edge[0]], vertexes[edge[1]])

        # if this is the first outgoing edge for the vertex edge[0], we need to create a new Count instance
        if not vertex_count[edge[0]]:
            # in this case None represents the intitial XBlock, namely the whole V
            vertex_count[edge[0]] = Count(my_edge.source, None)

        my_edge.count = vertex_count[edge[0]]
        my_edge.count.value += 1

        my_edge.source.add_to_image(my_edge)
        my_edge.destination.add_to_counterimage(my_edge)

    return vertexes


# this is a FUNDAMENTAL part of the algorithm: we need a stable initial partition with respect to the set V, but a partition where leafs and non-leafs are in the same block can't be stable
def preprocess_initial_partition(vertexes, initial_partition):
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


def build_qpartition(vertexes, initial_partition: set) -> list[QBlock]:
    union = set()
    # check phase
    for block in initial_partition:
        old_length = len(union)
        union = union.union(block)

        if old_length + len(block) != len(union):
            raise Exception(
                "there shouldn't be overlapse within blocks of initial_partition"
            )

    if len(union) != len(vertexes):
        raise Exception(
            "initial_partition should contain every vertex in one (and only one) block"
        )
    # end

    # initially X contains only one block
    initial_x_block = XBlock()
    x_partition = [initial_x_block]

    # create the partition Q
    q_partition = []
    # create the blocks of partition Q using the initial_partition
    for block in initial_partition:
        # QBlocks are initially created empty in order to obtain a reference to dllistnode for vertexes and avoid a double visit of vertexes
        qblock = QBlock([], initial_x_block)

        # create a new QBlock from the given initial_partition, and obtain a reference to dllistobject
        initial_x_block.append_qblock(qblock)
        for idx in block:
            vertexes[idx] = vertexes[idx]

            # append this vertex to the dllist in qblock
            qblock.append_vertex(vertexes[idx])

        q_partition.append(qblock)

    return q_partition


def initialize(graph, initial_partition):
    vertexes = parse_graph(graph)
    processed_partition = preprocess_initial_partition(vertexes, initial_partition)
    return (build_qpartition(vertexes, processed_partition), vertexes)

# this is a version of is_stable_partition for "foreign" users
def foreign_is_stable_partition(graph, partition: list):
    vertexes = pta.parse_graph(graph)
    return is_stable_partition([vertexes[vertex_idx] for vertex_idx in block] for block in partition)

# check if the given partition is stable with respect to the given block, or if it's stable if the block isn't given
def is_stable_partition(partition: list[list[Vertex]]):
    for couple in itertools.combinations(partition, 2):
        if not (check_block_stability(couple[0], couple[1]) and check_block_stability(couple[1], couple[0])):
            return False
    return True

# return True if A_block \subseteq R^{-1}(B_block) or A_block \cap R^{-1}(B_block) = \emptyset
def check_block_stability(
    A_block_vertexes: list[Vertex], B_block_vertexes: list[Vertex]
):
    # if there's a vertex y in B_qblock_vertexes such that for the i-th vertex we have i->y, then is_inside_B[i] = True
    is_inside_B = []
    for vertex in A_block_vertexes:
        is_inside_B.append(False)
        for edge in vertex.image:
            if edge.destination in B_block_vertexes:
                is_inside_B[-1] = True

    # all == True if for each vertex x in A there's a vertex y such that x \in E({x}) AND y \in B
    # not any == True if the set "image of A" and B are distinct
    return all(is_inside_B) or not any(is_inside_B)
