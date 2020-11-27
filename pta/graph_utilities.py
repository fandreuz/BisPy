from llist import dllist, dllistnode
import itertools

class Vertex:
    def __init__(self, label):
        # unique identifier of the vertex, used for debugging purposes
        self.label = label

        # the QBlock this vertex belongs to
        self.qblock = None

        # a flag used when visiting the adjacency of a node during the split phase
        self.visited = False

        # a list of Edges x->self
        self.counterimage = []

        # a list of Edges self->x
        self.image = []

        # an auxiliary Count instance used when we're preparing a new split phase. This will hold count(x,B) where B is the (former) QBlock which will be the next splitter
        self.aux_count = None

        # an auxiliary flag which will be set to True the first time this vertex is added to a second splitter set (see the function build_second_splitter). It will be set to False as soon as possible.
        self.in_second_splitter = False

        # a reference to the unique esisting instance of dllistnode associated with this Vertex
        self.dllistnode = None

    def add_to_counterimage(self, edge):
        self.counterimage.append(edge)

    def add_to_image(self, edge):
        self.image.append(edge)

    def visit(self):
        self.visited = True

    def release(self):
        self.visited = False

    def added_to_second_splitter(self):
        self.in_second_splitter = True

    def clear_second_splitter_flag(self):
        self.in_second_splitter = False

    def __str__(self):
        return "V{}".format(self.label)

    def __repr__(self):
        return "V{}".format(self.label)


class Edge:
    def __init__(self, source: Vertex, destination: Vertex):
        #  type Vertex
        self.source = source
        self.destination = destination

        # holds the value count(source,S) = |E({source}) \cap S|
        self.count = None

    # this is only used for testing purposes
    def __hash__(self):
        return hash("{}-{}".format(self.source.label, self.destination.label))

    def __eq__(self, other):
        return (
            isinstance(other, Edge)
            and self.source == other.source
            and self.destination == other.destination
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<{},{}>".format(self.source, self.destination)

    def __repr__(self):
        return "<{},{}>".format(self.source, self.destination)


class QBlock:
    def __init__(self, vertexes, xblock):
        self.size = len(vertexes)
        self.vertexes = dllist(vertexes)
        self.xblock = xblock

        # an helper field which will be used during the split phase of a QBlock
        self.split_helper_block = None

        self.dllistnode = None

    # this doesn't check if the vertex is a duplicate.
    # make sure that vertex is a proper Vertex, not a dllistnode
    def append_vertex(self, vertex: Vertex):
        self.size += 1
        vertex.dllistnode = self.vertexes.append(vertex)
        vertex.qblock = self

    # throws an error if the vertex isn't inside this qblock
    def remove_vertex(self, vertex: Vertex):
        self.size -= 1
        self.vertexes.remove(vertex.dllistnode)
        vertex.qblock = None

    def initialize_split_helper_block(self):
        self.split_helper_block = QBlock([], self.xblock)

    def reset_helper_block(self):
        self.split_helper_block = None

    def __str__(self):
        return "Q({})".format(",".join([str(vertex) for vertex in self.vertexes]))

    def __repr__(self):
        return "Q({})".format(",".join([str(vertex) for vertex in self.vertexes]))


class XBlock:
    def __init__(self):
        self.qblocks = dllist([])

    def append_qblock(self, qblock: QBlock):
        qblock.dllistnode = self.qblocks.append(qblock)
        qblock.xblock = self

    def remove_qblock(self, qblock: QBlock):
        self.qblocks.remove(qblock.dllistnode)
        qblock.xblock = None

    def __str__(self):
        return "X[{}]".format(",".join([str(qblock) for qblock in self.qblocks]))

    def __repr__(self):
        return "X[{}]".format(",".join([str(qblock) for qblock in self.qblocks]))


# holds the value of count(vertex,XBlock) = |XBlock \cap E({vertex})|
class Count:
    def __init__(self, vertex: Vertex, xblock: XBlock):
        self.vertex = vertex
        self.xblock = xblock

        self.value = 0

    def __str__(self):
        return "C{}:{}".format(self.vertex, self.label)

    def __repr__(self):
        return "C{}:{}".format(self.vertex, self.label)


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


def initialize(graph, initial_partition):
    vertexes = parse_graph(graph)
    processed_partition = preprocess_initial_partition(vertexes, initial_partition)
    return (build_qpartition(vertexes, processed_partition), vertexes)

# this is a version of is_stable_partition for "foreign" users
def foreign_is_stable_partition(graph, partition: list):
    vertexes = parse_graph(graph)
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
