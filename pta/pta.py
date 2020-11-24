from llist import dllist, dllistnode


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


# check if the given partition is stable with respect to the given block, or if it's stable if the block isn't given
def is_stable_partition(q_partition: list[QBlock], qblock: QBlock = None):
    pass


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


def build_qpartition(vertexes, initial_partition: set):
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


# choose the smallest qblock of the first two
def extract_splitter(compound_block: XBlock):
    first_qblock = compound_block.qblocks.first
    if first_qblock.value.size <= first_qblock.next.value.size:
        compound_block.remove_qblock(first_qblock.value)
        return first_qblock.value
    else:
        qblock = first_qblock.next.value
        compound_block.remove_qblock(qblock)
        return qblock


# construct a list of the nodes in the counterimage of qblock to be used in the split-phase.
# this also updates count(x,qblock) = |qblock \cap E({x})| (because qblock is going to become a new xblock)
# remember to reset the value of aux_count after the refinement
def build_block_counterimage(B_qblock: QBlock) -> list[Vertex]:
    qblock_counterimage = []

    for vertex in B_qblock.vertexes:
        for edge in vertex.counterimage:
            counterimage_vertex = edge.source

            # this vertex should be added to the counterimage only if necessary (avoid duplicates)
            if not counterimage_vertex.visited:
                qblock_counterimage.append(counterimage_vertex)
                # remember to release this vertex
                counterimage_vertex.visit()

            # if this is the first time we found a destination in qblock for whom this node is a source, create a new instance of Count
            # remember to set it to None
            if not counterimage_vertex.aux_count:
                counterimage_vertex.aux_count = Count(counterimage_vertex, B_qblock)
            counterimage_vertex.aux_count.value += 1

    for vertex in qblock_counterimage:
        # release this vertex so that it can be visited again in a next splitting phase
        vertex.release()

    return qblock_counterimage


# compute the set E^{-1}(B) - E^{-1}(S-B) where S is the XBlock which contained the QBlock B.
# in order to get the right result, you need to run the method build_splitter_counterimage before, which sets aux_count
def build_second_splitter_counterimage(
    B_qblock_vertexes: list[Vertex],
) -> list[Vertex]:
    splitter_counterimage = []

    for vertex in B_qblock_vertexes:
        for edge in vertex.counterimage:
            if not edge.source.in_second_splitter:
                # determine count(vertex,B) = |B \cap E({vertex})|
                count_B = edge.source.aux_count

                # determine count(vertex,S) = |S \cap E({vertex})|
                count_S = edge.count

                if count_B.value == count_S.value:
                    splitter_counterimage.append(edge.source)
                    edge.source.added_to_second_splitter()

    for vertex in splitter_counterimage:
        vertex.clear_second_splitter_flag()

    return splitter_counterimage


# perform a Split with respect to B_qblock
def split(B_counterimage: list[Vertex]):
    # keep track of the qblocks modified during step 4
    changed_qblocks = []

    for vertex in B_counterimage:
        # determine the qblock to which vertex belongs to
        qblock = vertex.qblock

        # remove vertex from this qblock, and place it in the "parallel" qblock
        qblock.remove_vertex(vertex)

        # if this is the first time a vertex is splitted from this qblock, create the helper qblock
        if not qblock.split_helper_block:
            changed_qblocks.append(qblock)
            qblock.initialize_split_helper_block()

        new_qblock = qblock.split_helper_block

        # put the vertex in the new qblock
        new_qblock.append_vertex(vertex)

    new_qblocks = []
    for qblock in changed_qblocks:
        helper_qblock = qblock.split_helper_block
        qblock.reset_helper_block()

        # add the new qblock to the same xblock to which the old qblock belongs, and obtain its ddllistnode
        qblock.xblock.append_qblock(helper_qblock)
        new_qblocks.append(helper_qblock)

        # if the old qblock has been made empty by the split (Q - E^{-1}(B) = \emptysey), remove it from the xblock
        if qblock.size == 0:
            qblock.xblock.remove_qblock(qblock)

    return new_qblocks

def update_counts(B_block_vertexes: list[Vertex]):
    for vertex in B_block_vertexes:
        for edge in vertex.counterimage:
            edge.count.value -= 1

            # if count(x,S) becomes zero, we point edge.count to count(x,B)
            if edge.count.value == 0:
                edge.count = edge.source.aux_count


# be careful: you should only work with llist in order to get O(1) deletion from x/qblocks
def refine(compound_xblocks, xblocks):
    # refinement step (following the steps at page 10 of "Three partition refinement algorithms")

    new_qblocks = []

    # step 1 (select a refining block B)
    # extract a random compound xblock
    S_compound_xblock = compound_xblocks.pop()
    # select the right qblock from this compound xblock
    # note that the dllistonodes in this list will most likely be outdated after the first split
    B_qblock = extract_splitter(S_compound_xblock)
    B_qblock_vertexes = [vertex for vertex in B_qblock.vertexes]

    # step 2 (update X)
    # if S_compound_xblock is still compund, put it back in compound_xblocks
    if len(S_compound_xblock.qblocks) > 1:
        compound_xblocks.append(S_compound_xblock)

    # add the extracted qblock to xblocks
    B_xblock = XBlock()
    B_xblock.append_qblock(B_qblock)

    xblocks.append(B_xblock)

    # step 3 (compute E^{-1}(B))
    B_counterimage = build_block_counterimage(B_qblock)

    # step 4 (refine Q with respect to B)
    new_qblocks.extend(split(B_counterimage))

    # step 5 (compute E^{-1}(B) - E^{-1}(S-B))

    # note that, since we are employing the strategy proposed in the paper, we don't even need to pass the XBLock S
    second_splitter_counterimage = build_second_splitter_counterimage(B_qblock_vertexes)

    # step 6
    new_qblocks.extend(split(second_splitter_counterimage))

    # step 7
    update_counts(B_counterimage)

    # reset aux_count
    # we only care about the vertexes in B_counterimage since we only set aux_count for those vertexes x such that |E({x}) \cap B_qblock| > 0
    for vertex in B_counterimage:
        vertex.aux_count = None

    return (xblocks, new_qblocks)

# returns a list of labels splitted in partitions
def pta(q_partition: list[QBlock]):
    x_partition = [q_partition[0].xblock]
    compound_xblocks = [x_partition[0]]

    while len(compound_xblocks) > 0:
        x_partition, new_qblocks = refine(compound_xblocks, x_partition)
        q_partition.extend(new_qblocks)

    return [tuple(map(lambda vertex: vertex.label, qblock.vertexes)) for qblock in filter(lambda qblock: qblock.size > 0, q_partition)]

# TODO: rimpiazza set con list perchè set controlla i duplicati ==> add non è O(1)
