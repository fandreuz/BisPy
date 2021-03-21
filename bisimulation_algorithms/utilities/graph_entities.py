from llist import dllist, dllistnode
from typing import Iterable


def compute_initial_partition_block_id(vertex_labels: Iterable[int]):
    id = 0
    for label in vertex_labels:
        id += pow(2, label)
    return id


class _Vertex:
    """The internal representation of the vertex of a graph. This is used by
    the algorithm to hold all the needed data structure, in order to access
    them in O(1).

    Attributes:
        label                   The unique identifier of this vertex.
        qblock                  The QBlock instance this vertex belongs to.
        visited                 A flag used in the algorithm to mark vertexes
            which it has already visited.
        counterimage            A list of _Edge instances such that
            edge.destination = self. This shouldn't be touched manually.
        image                   A list of _Edge instances such that
            edge.source = self. This shouldn't be touched manually.
        aux_count               An auxiliary _Count instance used to compute
            |B cap E({self})|.
        in_second_splitter      A flag used during the computation of the
            counterimage of blocks to avoid duplicates.
        dllistnode              A reference to the instance of dllistobject
            representing this vertex in the QBlock it belongs to.
    """

    def __init__(self, label):
        """The constructor of the class Vertex.

        Args:
            label (int): A unique label which identifies this vertex among all
            the others (usually its index in a list of vertexes).
        """

        self.label = label
        self.qblock = None
        self.dllistnode = None

        self.visited = False
        self.in_second_splitter = False

        self.counterimage = []
        self.image = []

        self.aux_count = None

        self.rank = None
        self.wf = True

        self.original_label = label

        self.initial_partition_block_id = None

        self.allow_visit = False
        self.old_qblock_id = None

    def scale_label(self, scaled_label: int):
        self.label = scaled_label

    def back_to_original_label(self):
        self.label = self.original_label

    # creates a subgraph which contains only vertexes of the
    # same rank of this vertex.
    def restrict_to_subgraph(self):
        # this will be called just before calling PTA, therefore set the _Count
        # instance for each _Edge

        img = self.image
        self.image = []

        count = _Count(self)

        for edge in img:
            if edge.destination.rank == self.rank:
                self.add_to_image(edge)

                # set the count for this _Edge, and increment the counter
                edge.count = count
                count.value += 1

        counterimg = self.counterimage
        self.counterimage = []

        for edge in counterimg:
            if edge.source.rank == self.rank:
                self.add_to_counterimage(edge)

    def restrict_to_allowed_subraph(self):
        self._original_img = self.image
        self.image = []

        self._original_count = None

        count = _Count(self)

        for edge in self._original_img:
            if edge.destination.allow_visit:
                self.add_to_image(edge)

                if self._original_count is None:
                    self._original_count = edge.count

                # set the count for this _Edge, and increment the counter
                edge.count = count
                count.value += 1

        self._original_counterimg = self.counterimage
        self.counterimage = []

        for edge in self._original_counterimg:
            if edge.source.allow_visit:
                self.add_to_counterimage(edge)

    def back_to_original_graph(self):
        self.image = self._original_img
        self.counterimage = self._original_counterimg

        for edge in self.image:
            edge.count = self._original_count

        self._original_count = None
        self._original_counterimg = None
        self._original_img = None

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

    def __repr__(self):
        return "V{}".format(self.label)


class _Edge:
    """Represents an edge between two _Vertex instances.

    Attributes:
        source                  The source _Vertex of this edge.
        destination             The destination _Vertex of this edge.
        count                   A _Count instance which holds |E({source})
            cap S|, where S is the block of X destination belongs to.
    """

    def __init__(self, source: _Vertex, destination: _Vertex):
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

    def __repr__(self):
        return "<{},{}>".format(self.source, self.destination)


class _QBlock:
    """A block of Q in the Paige-Tarjan algorithm.

    Attributes:
        size                    The number of vertexes in this block. This is
            updated automatically by append/remove_vertex.
        vertexes                A dllist which contains the vertexes in this
            block.
        xblock                  The (unique) block S of X such that
            S = A cup self, for some A.
        split_helper_block      A reference for O(1) access to a new block
            created from this block during the split phase.
        dllistnode              A reference to the dllistobject which
            represents this QBlock in xblock.
    """

    def __init__(self, vertexes, xblock):
        self.vertexes = dllist([])

        for vertex in vertexes:
            self.append_vertex(vertex)

        self.size = self.vertexes.size
        self.split_helper_block = None
        self.dllistnode = None
        self.visited = False

        if xblock is not None:
            xblock.append_qblock(self)

        self.deteached = False
        self.tried_merge = False

    # this doesn't check if the vertex is a duplicate.
    # make sure that vertex is a proper _Vertex, not a dllistnode
    def append_vertex(self, vertex: _Vertex):
        vertex.dllistnode = self.vertexes.append(vertex)
        self.size = self.vertexes.size
        vertex.qblock = self

    # throws an error if the vertex isn't inside this qblock
    def remove_vertex(self, vertex: _Vertex):
        self.vertexes.remove(vertex.dllistnode)
        self.size = self.vertexes.size
        vertex.qblock = None

    def initialize_split_helper_block(self):
        self.split_helper_block = _QBlock([], self.xblock)

    def reset_helper_block(self):
        self.split_helper_block = None

    @property
    def rank(self) -> int:
        if self.vertexes.first is not None:
            return self.vertexes.first.value.rank
        else:
            return None

    @property
    def xblock(self):
        if hasattr(self, '_xblock'):
            return self._xblock
        else:
            return None

    @xblock.setter
    def xblock(self, value):
        self._xblock = value

    def initialize_split_helper_block(self):
        self.split_helper_block = _QBlock([], self.xblock)

    def initial_partition_block_id(self):
        if self.vertexes.size > 0:
            return self.vertexes.first.value.initial_partition_block_id
        else:
            return None

    def merge(self, block2):
        for vertex in block2.vertexes:
            self.append_vertex(vertex)
        block2.deteached = True

    def __repr__(self):
        return "Q({})".format(
            ",".join([str(vertex) for vertex in self.vertexes])
        )

    def fast_mitosis(self, extract_vertexes):
        new_block = _QBlock([], self.xblock)
        for vertex in extract_vertexes:
            self.remove_vertex(vertex)
            new_block.append_vertex(vertex)
        return new_block

    # only for testing purposes
    def _mitosis(self, vertexes1, vertexes2):
        new_block = _QBlock([], self.xblock)

        for to_remove in vertexes2:
            for vertex in self.vertexes:
                if to_remove == vertex.label:
                    self.remove_vertex(vertex)
                    new_block.append_vertex(vertex)

        return new_block


class _XBlock:
    """A block of X in the Paige-Tarjan algorithm.

    Attributes:
        qblocks                     A dllist which contains the
            blocks Q1,...,Qn such that the union of Q1,...,Qn is equal to self.
    """

    def __init__(self):
        self.qblocks = dllist([])

    def size(self):
        return self.qblocks.size

    def append_qblock(self, qblock: _QBlock):
        qblock.dllistnode = self.qblocks.append(qblock)
        qblock.xblock = self
        return self

    def remove_qblock(self, qblock: _QBlock):
        self.qblocks.remove(qblock.dllistnode)
        qblock.xblock = None

    def __repr__(self):
        return "X[{}]".format(",".join(str(qblock) for qblock in self.qblocks))


# holds the value of count(vertex,_XBlock) = |_XBlock \cap E({vertex})|
class _Count:
    """A class whcih represents a value. This is used to hold, share, and
    propagate changes in O(1) between all the interested entities (vertexes in
    the case of vertex.aux_count, edges in the case of edge.count).

    Attributes:
        vertex                    The vertex this instance is associated to,
            namely the x such that self = count(x,A).
        xblock                    The XBlock this isntance is associated to,
            namely the S such that self = count(x,S).
        value                     The current value of this instance (shared
            between all the "users" of the reference).
    """

    def __init__(self, vertex: _Vertex):
        self.vertex = vertex
        self.value = 0

    def __repr__(self):
        return "C{}:{}".format(self.vertex, self.value)
