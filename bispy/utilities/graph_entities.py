from llist import dllist, dllistnode
from typing import Iterable, Callable, Any, Union, List


class _Vertex:
    """BisPy representation of a vertex. Contains several data structures which
    provide :math:`O(1)` access to the :math:`E(\\textit{vertex})` and
    :math:`E^{-1}(\\textit{vertex})`, as well as attributes to store temporary
    information used among different parts of the algorithm (make sure to reset
    them when they are not needed anymore).

    :param int label: A unique integer ID which identifies this vertex.
    """

    def __init__(self, label):
        """Constructor method"""
        self._label = label
        self._qblock = None

        # the dllistobject which refers to this vertex inside the dllist inside
        # the QBlock which contains this vertex
        self._dllistnode = None

        # a property shared by many algorithms, reset it to False after usage
        self.visited = False

        # a list of `_Edge` instances from `self` to the `_Vertex` instances in
        # the image of this `_Vertex`.
        self.image = []
        # a list of `_Edge` instances from `self` to the `_Vertex` instances in
        # the counterimage of this `_Vertex`.
        self.counterimage = []

        self.aux_count = None
        self.in_second_splitter = False

        self._original_label = label

        self.initial_partition_block_id = None

        self.allow_visit = False

        self._scc = None

    @property
    def label(self):
        """The current label assigned to this :class:`_Vertex` instance. May
        change if a method like :func:`scale_label` is called."""
        return self._label

    @property
    def original_label(self):
        """The original label assigned to this :class:`_Vertex` instance.
        Does not change (ever!)."""
        return self._original_label

    @property
    def qblock(self):
        """The :class:`_QBlock` instance that this :class:`_Vertex` belongs to
        at the moment."""
        return self._qblock

    @property
    def scc(self):
        """The :class:`_SCC` instance that this :class:`_Vertex` belongs to
        at the moment."""
        return self._scc

    @scc.setter
    def scc(self, value):
        self._scc = value

    @property
    def rank(self) -> Union[int, float]:
        """The `rank` of this vertex (associated with the `rank` of the
        corresponding SCC)."""

        return self.scc.rank

    @rank.setter
    def rank(self, value):
        self.scc._rank = value

    @property
    def wf(self) -> bool:
        """`True` if this vertex is well-founded, `False` otherwise."""
        return self.scc.wf

    @wf.setter
    def wf(self, value):
        self.scc._wf = value

    def scale_label(self, scaled_label: int):
        """
        Change the label of this vertex to `scaled_label`. This is usually
        done when we want to apply an algorithm like *Paige-Tarjan* to a
        subgraph of :math:`G`, therefore we need to "scale" the vertexes
        in that subgraph in order to make the subgraph integer (for a
        reference about this topic have a look at the module
        :mod:`bispy.utilities.graph_normalization`).

        The old label is stored in :func:`original_label`, and can be
        recovered using :func:`back_to_original_label`.

        :param scaled_label: The new label.
        """
        self._label = scaled_label

    def back_to_original_label(self):
        """
        Undo the result of a call to :func:`scale_label`.
        """
        self._label = self.original_label

    # creates a subgraph which contains only vertexes of the
    # same rank of this vertex.
    def restrict_to_subgraph(self, validation: Callable[[Any], bool]):
        """
        Restrict the image and counterimage only to vertexes that satisfy the
        given validation function, and resets the value of the associated
        :class:`_Count` instanced.

        Also sets `_original_img`, `_original_counterimg`, `_original_count`,
        which can then be recovered using :func:`back_to_original_graph`.

        :param validation: A function which returns `True` when the vertex
            given as argument is accepted in the subgraph.
        :type validation: Callable[[_Vertex], bool]
        """

        # this will be called just before calling PTA, therefore set the _Count
        # instance for each _Edge

        self._original_img = self.image
        self.image = []

        self._original_count = None
        count = _Count(self)

        for edge in self._original_img:
            if validation(edge.destination):
                self.add_to_image(edge)

                if self._original_count is None:
                    self._original_count = edge.count

                # set the count for this _Edge, and increment the counter
                edge.count = count
                count.value += 1

        self._original_counterimg = self.counterimage
        self.counterimage = []

        for edge in self._original_counterimg:
            if validation(edge.source):
                self.add_to_counterimage(edge)

    def back_to_original_graph(self):
        """
        Recover the original image, counterimage and associated values
        of :class:`_Count`, must be called after a call to
        :func:`restrict_to_subgraph`.
        """

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
    """Represents an edge between two instances of :class:`_Vertex`.

    :param source: The source of the edge.
    :param destination: The destination of the edge.
    """

    def __init__(self, source: _Vertex, destination: _Vertex):
        self.source = source
        self.destination = destination
        self._count = None

    @property
    def count(self):
        """Holds the value :math:`|E({\\textit{source}}) \\cap S|`, where
        :math:`S` is the block of the partition :math:`X` that `destination`
        belongs to.
        """

        return self._count

    @count.setter
    def count(self, count):
        self._count = count

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
    """A block of the partition :math:`Q`. This is also used as a
    general-purpose block by *Dovier-Piazza-Policriti*'s and *Saha*'s
    algorithms.

    This class uses a *Doubly-Linked-List* to store the set vertexes inside
    the block, therefore we are able to remove a node in :math:`O(1)`.

    :param vertexes: Vertexes in the block.
    :param xblock: The block of :math:`X` that this block belongs to.
    :type xblock: _XBlock
    """

    def __init__(self, vertexes: List[_Vertex], xblock):
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

        self.is_new_qblock = False

    @property
    def rank(self) -> int:
        """
        The rank of all the vertexes in this block (note that in general
        one may create a :class:`_QBlock` from an arbitrary set of vertexes,
        in that case we cannot say in general that those vertexes have all
        the same rank).
        """

        if self.vertexes.first is not None:
            return self.vertexes.first.value.rank
        else:
            return None

    @property
    def xblock(self):
        """
        The block of :math:`X` this block belongs to.
        """

        if hasattr(self, "_xblock"):
            return self._xblock
        else:
            return None

    @xblock.setter
    def xblock(self, value):
        self._xblock = value

    # this doesn't check if the vertex is a duplicate.
    # make sure that vertex is a proper _Vertex, not a dllistnode
    def append_vertex(self, vertex: _Vertex):
        """
        Append a new vertex to this block. This also sets the attributes
        `vertex._dllistnode` and `vertex._qblock`, and updates the attribute
        `size`.

        :param vertex: The new vertex to be added.
        """

        vertex._dllistnode = self.vertexes.append(vertex)
        self.size = self.vertexes.size
        vertex._qblock = self

    def remove_vertex(self, vertex: _Vertex):
        """
        Remove a vertex to this block. This also resets the attribute
        `vertex._qblock`, and updates the attribute `size`.

        This function uses the attribute `vertex._dllistnode` to
        modify the Doubly-Linked-List in the attribute `vertexes` in
        :math:`O(1)`.

        :param vertex: The new vertex to be added.
        """

        self.vertexes.remove(vertex._dllistnode)
        self.size = self.vertexes.size
        vertex._qblock = None

    def initialize_split_helper_block(self):
        self.split_helper_block = _QBlock([], self.xblock)

    def reset_helper_block(self):
        self.split_helper_block = None

    def initialize_split_helper_block(self):
        self.split_helper_block = _QBlock([], self.xblock)

    def initial_partition_block_id(self):
        if self.vertexes.size > 0:
            return self.vertexes.first.value.initial_partition_block_id
        else:
            return None

    def merge(self, block2):
        """
        Add all the vertexes in `block2` to this block, and then set
        the attribute `block2.deteached` to `True`.

        :param block2: The block to be merged into `self`.
        :type block2: _QBlock
        """

        for vertex in block2.vertexes:
            self.append_vertex(vertex)
        block2.deteached = True

    def __repr__(self):
        return "Q({})".format(
            ",".join([str(vertex) for vertex in self.vertexes])
        ) + ("DET" if self.deteached else "")

    def fast_mitosis(self, extract_vertexes: List[_Vertex]):
        """Extract a subset of vertexes from this block to create a new block.

        :param extract_vertexes: The subset of vertexes to be extracted.
        :return: The new block which contains the vertexes in
            `extract_vertexes`.
        :rtype: _QBlock
        """

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
    """A block of the partition :math:`X`.

    This class uses a *Doubly-Linked-List* to store the set vertexes inside
    the block, therefore we are able to remove a block in :math:`O(1)`.
    """

    def __init__(self):
        self.qblocks = dllist([])

    @property
    def size(self):
        """The number of blocks of :math:`Q` in this block of :math:`X`."""
        return self.qblocks.size

    def append_qblock(self, qblock: _QBlock):
        """Insert a new block of :math:`Q` in this block. This also sets the
        attributes `qblock.dllistnode` and `qblock.xblock`.

        :param: The block of :math:`Q` to be inserted.
        :returns: `self`, to allow chain insertions.
        :rtype: _XBlock"""

        qblock.dllistnode = self.qblocks.append(qblock)
        qblock.xblock = self
        return self

    def remove_qblock(self, qblock: _QBlock):
        """Remove a block of :math:`Q` from this block. This also resets the
        attribute `qblock.xblock` to `None`.

        :param: The block of :math:`Q` to be removed.
        """

        self.qblocks.remove(qblock.dllistnode)
        qblock.xblock = None

    def __repr__(self):
        return "X[{}]".format(",".join(str(qblock) for qblock in self.qblocks))


# holds the value of count(vertex,_XBlock) = |_XBlock \cap E({vertex})|
class _Count:
    def __init__(self, vertex: _Vertex):
        self.vertex = vertex
        self.value = 0

    def __repr__(self):
        return "C{}:{}".format(self.vertex, self.value)


class _SCC:
    """Represents a *strongly connected component*. This is used to compute
    rank.

    :param label: A unique ID.
    """

    def __init__(self, label: int):
        self._label = label
        self._rank = float("-inf")

        self._image = {}
        self._counterimage = {}

        self._vertexes = set()

        self.visited = False

    @property
    def label(self) -> int:
        """The unique ID which represents this SCC."""
        return self._label

    @property
    def image(self):
        """The overall image of the SCC. The function :func:`compute_image`
        must be called beforehand."""

        return self._image.values()

    @property
    def counterimage(self):
        """The overall counterimage of the SCC. The function
        :func:`compute_counterimage` must be called beforehand."""

        return self._counterimage.values()

    @property
    def wf(self) -> bool:
        """`True` if the SCC is well-founded (an SCC may be well-founded if
        there is only one vertex in the component, but this is not guaranteed).
        """

        if not hasattr(self, "_wf"):
            if len(self._vertexes) > 1:
                self._wf = False
            else:
                self._wf = True
                for scc in self.image:
                    if not scc.wf:
                        self._wf = False
                        break
        return self._wf

    @property
    def rank(self) -> Union[int, float]:
        """The rank of the vertexes in this SCC."""

        return self._rank

    def add_vertex(self, vertex: _Vertex):
        """Add a new vertex to this SCC.

        :param vertex: The vertex to be added."""

        self._vertexes.add(vertex)
        vertex.scc = self

    def mark_leaf(self):
        """Mark this SCC as a leaf of the graph."""
        self._rank = 0

    def mark_scc_leaf(self):
        """Mark this SCC as a leaf of the graph of strongly connected
        components."""
        self._rank = float("-inf")

    def compute_image(self):
        """Compute the image of this SCC."""

        self._image.clear()
        for vx in self._vertexes:
            for edge in vx.image:
                # edge towards self
                if edge.destination.scc == self:
                    self._wf = False
                else:
                    # NO! there's no guarantee that the visit occurs
                    # in the right order. we can't rely on the .wf
                    # field of successors, since it may not be the truth
                    # if not edge.destination.wf:
                    #    self._wf = False
                    self._image[
                        edge.destination.scc.label
                    ] = edge.destination.scc

    def compute_counterimage(self):
        """Compute the counterimage of this SCC."""

        self._counterimage.clear()
        for vx in self._vertexes:
            for edge in vx.counterimage:
                # edge towards self, don't include
                if edge.source.scc == self:
                    continue
                else:
                    self._counterimage[edge.source.scc.label] = edge.source.scc

    def destroy(self):
        """Destroy this SCC (image, counterimage and vertexes set)."""

        self._vertexes.clear()
        self._image.clear()
        self._counterimage.clear()

    def join(self, other):
        """Merge `other` into this SCC, and destroy `other`.

        :param other: The SCC to be merged into `self`.
        :type other: _SCC
        """

        for vertex in other._vertexes:
            self.add_vertex(vertex)
        self._rank = None
        self._wf = False
        other.destroy()

    def __repr__(self):
        return "SCC({})".format(
            ",".join([str(vertex) for vertex in self._vertexes])
        )
