from llist import dllist, dllistnode


class Edge:
    def __init__(self, source: dllistnode, destination: dllistnode):
        self.source = source
        self.destination = destination

        # holds the value count(source,S) = |E({source}) \cap S|
        self.count = None

    # this is only used for testing purposes
    def __hash__(self):
        return hash(
            "{}-{}".format(self.source.value.label, self.destination.value.label)
        )

    def __eq__(self, other):
        return (
            isinstance(other, Edge)
            and self.source == other.source
            and self.destination == other.destination
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<{}, {}>".format(self.source, self.destination)

    def __repr__(self):
        return "<{}, {}>".format(self.source, self.destination)


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

    def add_to_counterimage(self, edge: Edge):
        self.counterimage.append(edge)

    def add_to_image(self, edge: Edge):
        self.image.append(edge)

    def visit(self):
        self.visited = True

    def release(self):
        self.visited = False

    def __str__(self):
        return "V{}".format(self.label)

    def __repr__(self):
        return "V{}".format(self.label)


# holds the value of count(vertex,XBlock) = |XBlock \cap E({vertex})|
class Count:
    def __init__(self, vertex: Vertex, xblock):
        self.vertex = vertex
        self.xblock = xblock

        self.value = 0


class QBlock:
    def __init__(self, vertexes, xblock):
        self.size = len(vertexes)
        self.vertexes = dllist(vertexes)
        self.xblock = xblock

        # an helper field which will be used during the split phase of a QBlock
        self.split_helper_block = None

    # this doesn't check if the vertex is a duplicate.
    # make sure that vertex is a proper Vertex, not a dllistnode
    def append_vertex(self, vertex: Vertex):
        self.size += 1
        return self.vertexes.append(vertex)

    # throws an error if the vertex isn't inside this qblock
    def remove_vertex(self, vertex_dllistnode):
        self.size -= 1
        return self.vertexes.remove(vertex_dllistnode)

    def initialize_split_helper_block(self):
        self.split_helper_block = QBlock([], self.xblock)

    def reset_helper_block(self):
        self.split_helper_block = None

    def __str__(self):
        return "({})".format(",".join([str(vertex) for vertex in self.vertexes]))

    def __repr__(self):
        return "({})".format(",".join([str(vertex) for vertex in self.vertexes]))


class XBlock:
    def __init__(self, label):
        self.label = label
        self.qblocks = dllist([])

    # make sure that qblock isn't a ddllistnode
    def append_qblock(self, qblock):
        return self.qblocks.append(qblock)

    # make sure that qblock is a ddllistnode
    def remove_qblock(self, qblock):
        return self.qblocks.remove(qblock)

    def __str__(self):
        return "[{}]".format(",".join([str(qblock) for qblock in self.qblocks]))

    def __repr__(self):
        return "[{}]".format(",".join([str(qblock) for qblock in self.qblocks]))


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
            if edge.destination.value in B_block_vertexes:
                is_inside_B[-1] = True

    # all == True if for each vertex x in A there's a vertex y such that x \in E({x}) AND y \in B
    # not any == True if the set "image of A" and B are distinct
    return all(is_inside_B) or not any(is_inside_B)


# this also returns a list of dllistobject representing the vertexes in the graph
def parse_graph(graph, initial_partition):
    union = set()
    # check phase
    for block in initial_partition:
        old_length = len(union)
        union = union.union(block)

        if old_length + len(block) != len(union):
            raise Exception(
                "there shouldn't be overlapse within blocks of initial_partition"
            )

    if len(union) != len(graph.nodes):
        raise Exception(
            "initial_partition should contain every vertex in one (and only one) block"
        )
    # end

    # create a list of ddllistnode to be filled later. for each Vertex there's only one record of type ddllistnode
    vertexes_ddllistnode = [None for _ in range(len(graph.nodes))]

    # initially X contains only one block
    initial_x_block = XBlock(0)
    x_partition = [initial_x_block]

    # create the partition Q
    q_partition = []
    # create the blocks of partition Q using the initial_partition
    for block in initial_partition:
        # QBlocks are initially created empty in order to obtain a reference to dllistnode for vertexes and avoid a double visit of vertexes
        qblock = QBlock([], initial_x_block)

        # create a new QBlock from the given initial_partition, and obtain a reference to dllistobject
        qblock_ddllistnode = initial_x_block.append_qblock(qblock)
        for idx in block:
            vertex = Vertex(idx)
            vertex.qblock = qblock_ddllistnode

            # append this vertex to the dllist in qblock, and obtain a UNIQUE reference to ddllistnode for this vertex
            vertexes_ddllistnode[idx] = qblock.append_vertex(vertex)

        q_partition.append(qblock)

    # holds the references to Count objects to assign to the edges (this is OK because we can consider |V| = O(|E|))
    # count(x) = count(x,V) = |V \cap E({x})| = |E({x})|
    vertex_count = [None for _ in graph.nodes]

    # a vertex should always refer to a ddllistnode, in order to help if fellows to be splitted (i.e. not obtain the error "dllistnode belongs to another list")
    for edge in graph.edges:
        # create an instance of my class Edge
        my_edge = Edge(vertexes_ddllistnode[edge[0]], vertexes_ddllistnode[edge[1]])

        # if this is the first outgoing edge for the vertex edge[0], we need to create a new Count instance
        if not vertex_count[edge[0]]:
            vertex_count[edge[0]] = Count(my_edge.source.value, initial_x_block)

        my_edge.count = vertex_count[edge[0]]
        my_edge.count.value += 1

        my_edge.source.value.add_to_image(my_edge)
        my_edge.destination.value.add_to_counterimage(my_edge)

    return (q_partition, vertexes_ddllistnode)


# choose the smallest qblock of the first two
def extract_splitter(compound_block: XBlock):
    first_qblock = compound_block.qblocks.first
    if first_qblock.value.size <= first_qblock.next.value.size:
        return compound_block.qblocks.popleft()
    else:
        return compound_block.qblocks.remove(first_qblock.next)


# construct a list of the nodes in the counterimage of qblock to be used in the split-phase.
# this also updates count(x,qblock) = |qblock \cap E({x})| (because qblock is going to become a new xblock)
# remember to reset the value of aux_count after the refinement
def build_block_counterimage(B_qblock: QBlock):
    qblock_counterimage = []

    for vertex in B_qblock.vertexes:
        for edge in vertex.counterimage:
            counterimage_vertex = edge.source

            # this vertex should be added to the counterimage only if necessary (avoid duplicates)
            if not counterimage_vertex.value.visited:
                qblock_counterimage.append(counterimage_vertex)
                # remember to release this vertex
                counterimage_vertex.value.visit()

            # if this is the first time we found a destination in qblock for whom this node is a source, create a new instance of Count
            # remember to set it to None
            if not counterimage_vertex.value.aux_count:
                counterimage_vertex.value.aux_count = Count(
                    counterimage_vertex.value, B_qblock
                )
            counterimage_vertex.value.aux_count.value += 1

    for vertex in qblock_counterimage:
        # release this vertex so that it can be visited again in a next splitting phase
        vertex.value.release()

    return qblock_counterimage


# compute the set E^{-1}(B) - E^{-1}(S-B) where S is the XBlock which contained the QBlock B.
def build_second_splitter(B_qblock_vertexes: list[Vertex], S_XBlock: XBlock):
    splitter = []

    for vertex in B_qblock_vertexes:
        for edge in vertex.counterimage:
            # determine count(vertex,B) = |B \cap E({vertex})|
            count_B = vertex.aux_count

            # determine count(vertex,S) = |S \cap E({vertex})|
            count_S = edge.count

            if count_B.value == count_S.value:
                splitter.append(vertex)
                break

    return splitter


# perform a Split with respect to B_qblock
def split(B_counterimage: list[dllistnode]):
    # keep track of the qblocks modified during step 4
    changed_qblocks = []

    for vertex in B_counterimage:
        # determine the qblock to which vertex belongs to
        qblock_ddllistnode = vertex.value.qblock
        # for easier access, preserve a reference to the "plain" QBlock object
        qblock_value = qblock_ddllistnode.value

        # remove vertex from this qblock, and place it in the "parallel" qblock
        vertex_value = qblock_value.remove_vertex(vertex)

        # if this is the first time a vertex is splitted from this qblock, create the helper qblock
        if not qblock_value.split_helper_block:
            changed_qblocks.append(qblock_ddllistnode)
            qblock_value.initialize_split_helper_block()

        # put the vertex in the new qblock and obtain a reference to the new ddllistnode
        vertex_ddllistnode = qblock_value.split_helper_block.append_vertex(vertex_value)

    for qblock_ddllistnode in changed_qblocks:
        qblock_value = qblock_ddllistnode.value

        helper_block = qblock_value.split_helper_block
        qblock_value.reset_helper_block()

        # add the new qblock to the same xblock to which the old qblock belongs, and obtain its ddllistnode
        helper_qblock_ddllistnode = qblock_value.xblock.qblocks.append(helper_block)

        # update the qblock attribute for its vertexes
        for vertex in helper_block.vertexes:
            vertex_value.qblock = helper_qblock_ddllistnode

        # if the old qblock has been made empty by the split (Q - E^{-1}(B) = \emptysey), remove it from the xblock
        if qblock_value.size == 0:
            qblock_value.xblock.qblocks.remove(qblock_ddllistnode)


# be careful: you should only work with llist in order to get O(1) deletion from x/qblocks
def refine(compound_xblocks, xblocks):
    # refinement step (following the steps at page 10 of "Three partition refinement algorithms")

    # step 1 (select a refining block B)
    # extract a random compound xblock
    S_compound_xblock = compound_xblocks.pop()
    # select the right qblock from this compound xblock
    B_qblock = extract_splitter(S_compound_xblock)

    # step 2 (update X)
    # if compound_xblock is still compund, put it back in compound_xblocks
    if len(S_compound_xblock.qblocks) > 1:
        compound_xblocks.append(S_compound_xblock)

    # add the extracted qblock to xblocks
    B_xblock = XBlock(len(xblocks))
    B_xblock.append_qblock(B_qblock)

    xblocks.append(B_xblock)

    # step 3 (compute E^{-1}(B))

    # keep a copy of the vertexes in B_qblock, since it can be modifed by split
    B_vertexes_copy = list(map(lambda dllistnode: dllistnode, B_qblock.vertexes))

    B_counterimage = build_block_counterimage(B_qblock)

    # step 4 (refine Q with respect to B)
    split(B_counterimage)

    # step 5 (compute E^{-1}(B) - E^{-1}(S-B))

    # note that, since we are employing the strategy proposed in the paper, we don't even need to pass the XBLock S
    second_splitter = build_second_splitter(B_vertexes_copy)

    # step 6

    # reset aux_count
    # we only care about the vertexes in B_counterimage since we only set aux_count for those vertexes x such that |E({x}) \cap B_qblock| > 0
    for vertex_dllistobject in B_counterimage:
        vertex_dllistobject.value.aux_count = None


def pta(q_partition):
    compound_xblocks = set()
    xblocks = set()


# TODO: rimpiazza set con list perchè set controlla i duplicati ==> add non è O(1)
