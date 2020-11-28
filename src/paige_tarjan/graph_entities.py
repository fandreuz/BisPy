from llist import dllist, dllistnode


class _Vertex:
    def __init__(self, label):
        # unique identifier of the vertex, used for debugging purposes
        self.label = label

        # the _QBlock this vertex belongs to
        self.qblock = None

        # a flag used when visiting the adjacency of a node during the split phase
        self.visited = False

        # a list of _Edges x->self
        self.counterimage = []

        # a list of _Edges self->x
        self.image = []

        # an auxiliary _Count instance used when we're preparing a new split phase. This will hold count(x,B) where B is the (former) _QBlock which will be the next splitter
        self.aux_count = None

        # an auxiliary flag which will be set to True the first time this vertex is added to a second splitter set (see the function build_second_splitter). It will be set to False as soon as possible.
        self.in_second_splitter = False

        # a reference to the unique esisting instance of dllistnode associated with this _Vertex
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


class _Edge:
    def __init__(self, source: _Vertex, destination: _Vertex):
        #  type _Vertex
        self.source = source
        self.destination = destination

        # holds the value count(source,S) = |E({source}) \cap S|
        self.count = None

    # this is only used for testing purposes
    def __hash__(self):
        return hash("{}-{}".format(self.source.label, self.destination.label))

    def __eq__(self, other):
        return (
            isinstance(other, _Edge)
            and self.source == other.source
            and self.destination == other.destination
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<{},{}>".format(self.source, self.destination)

    def __repr__(self):
        return "<{},{}>".format(self.source, self.destination)


class _QBlock:
    def __init__(self, vertexes, xblock):
        self.size = len(vertexes)
        self.vertexes = dllist(vertexes)
        self.xblock = xblock

        # an helper field which will be used during the split phase of a _QBlock
        self.split_helper_block = None

        self.dllistnode = None

    # this doesn't check if the vertex is a duplicate.
    # make sure that vertex is a proper _Vertex, not a dllistnode
    def append_vertex(self, vertex: _Vertex):
        self.size += 1
        vertex.dllistnode = self.vertexes.append(vertex)
        vertex.qblock = self

    # throws an error if the vertex isn't inside this qblock
    def remove_vertex(self, vertex: _Vertex):
        self.size -= 1
        self.vertexes.remove(vertex.dllistnode)
        vertex.qblock = None

    def initialize_split_helper_block(self):
        self.split_helper_block = _QBlock([], self.xblock)

    def reset_helper_block(self):
        self.split_helper_block = None

    def __str__(self):
        return "Q({})".format(",".join([str(vertex) for vertex in self.vertexes]))

    def __repr__(self):
        return "Q({})".format(",".join([str(vertex) for vertex in self.vertexes]))


class _XBlock:
    def __init__(self):
        self.qblocks = dllist([])

    def append_qblock(self, qblock: _QBlock):
        qblock.dllistnode = self.qblocks.append(qblock)
        qblock.xblock = self

    def remove_qblock(self, qblock: _QBlock):
        self.qblocks.remove(qblock.dllistnode)
        qblock.xblock = None

    def __str__(self):
        return "X[{}]".format(",".join([str(qblock) for qblock in self.qblocks]))

    def __repr__(self):
        return "X[{}]".format(",".join([str(qblock) for qblock in self.qblocks]))


# holds the value of count(vertex,_XBlock) = |_XBlock \cap E({vertex})|
class _Count:
    def __init__(self, vertex: _Vertex, xblock: _XBlock):
        self.vertex = vertex
        self.xblock = xblock

        self.value = 0

    def __str__(self):
        return "C{}:{}".format(self.vertex, self.label)

    def __repr__(self):
        return "C{}:{}".format(self.vertex, self.label)
