from llist import dllist, dllistnode
from typing import Iterable


def compute_initial_partition_block_id(vertex_labels: Iterable[int]):
    id = 0
    for label in vertex_labels:
        id += pow(2, label)
    return id


class _Vertex:
    """The internal representation of a vertex in a graph. Contains several
    conveniente attributes/data structures to provide ~O(1) access from within
    the bisimulation algorithms.

    .. note::

       Make sure to reset temporary attributes like :attr:`visited`.

    :param int label: A unique label used to reference the vertex. It's
            preferable to use an interval of integers starting from zero
            in order to allow algorithms to be run, otherwise `` BisPy `` will
            enforce this kind of labeling beforehand.
    """

    def __init__(self, label):
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
        """The current label assigned to this instance. May change if a method
        like :func:`scale_label` is called.

        :type: int
        """
        return self._label

    @property
    def original_label(self):
        """The original label assigned to this instance. Is a constant through
        the whole life of the instance.

        :type: int
        """
        return self._original_label

    @property
    def qblock(self):
        """The :class:`._QBlock` instance that this vertex belongs to
        at the moment. Used, for instance, in `` Paige-Tarjan `` .

        :type: :class:`._QBlock`
        """
        return self._qblock

    @property
    def scc(self):
        """The :class:`._SCC` instance that this vertex belongs to at the
        moment. When set, it doesn't change unless you call `` Saha `` to
        add a new edge. It's usually set during the computation of the rank
        (check :func:`~bispy.utilities.kosaraju.kosaraju`).

        :getter: Return the SCC for this vertex.
        :setter: Set the SCC for this vertex.
        :type: :class:`._SCC`
        """
        return self._scc

    @scc.setter
    def scc(self, value):
        self._scc = value

    def scale_label(self, scaled_label):
        """Changes the value of the :func:`label`. Usually this is used to
        obtain a subgraph of the current graph to apply `` Paige-Tarjan `` .

        :param int scaled_label: The new label.
        """
        self._label = scaled_label

    def back_to_original_label(self):
        """Reset the label of this vertex to :func:`original_label`, usually
        after the job which compelled us to call :func:`scale_label` is
        completed.
        """
        self._label = self.original_label

    def restrict_to_subgraph_of_same_rank(self):
        """Modify the current graph to create a subgraph which contains only
        vertexes at the same rank of this vertex. Removes all the edges
        starting from this vertex towards nodes which don't respect this
        condition. In order to finalize the creation of the new subgraph, you
        need to call this method on all the vertexes at the interesting rank.

        .. note::

       This method destroys the graph, therefore it's not intended for an
       ``incremental'' use.
       """

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
        """Modify the current graph to create a subgraph which contains only
        ``allowed'' vertexes (the attribute :attr:`allow_visit` of the vertex
        must be True). Removes all the edges starting from this vertex towards
        nodes which don't respect this condition. In order to finalize the
        creation of the new subgraph, you need to call this method (at least)
        on all the allowed vertexes. You can recover the original graph calling
        :func:`back_to_original_graph`.
       """

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
        """
        Invert the result of :func:`restrict_to_allowed_subraph` (you need to
        call it on each :class:`._Vertex` instance on which
        :func:`restrict_to_allowed_subraph` was called).
        """
        self.image = self._original_img
        self.counterimage = self._original_counterimg

        for edge in self.image:
            edge.count = self._original_count

        self._original_count = None
        self._original_counterimg = None
        self._original_img = None

    def add_to_counterimage(self, edge):
        """
        Add a new edge to the counterimage of this vertex.

        :param edge: The new edge to be added.
        :type edge: :class:`._Edge`
        """
        self.counterimage.append(edge)

    def add_to_image(self, edge):
        """
        Add a new edge to the image of this vertex.

        :param :class:`._Edge` edge: The new edge to be added.
        """
        self.image.append(edge)

    @property
    def rank(self):
        """
        The rank associated with this vertex (refers to the rank stored in the
        subsequent :class:`._SCC` instance).

        :setter: Set the rank for this vertex and the rank of the associated
            :class:`._SCC` instance.
        :getter: Get the rank for this vertex.
        :type: int or float
        """
        return self.scc.rank

    @rank.setter
    def rank(self, value):
        self.scc._rank = value

    @property
    def wf(self):
        """
        A flag which tells whether this vertex is well founded or not (this is
        in fact the well-foundedness of the subsequent strongly connected
        component).

        :setter: Set the well-founded flag for this vertex, and for the
            associated :class:`._SCC` instance.
        :getter: Get the well-founded flag for this vertex.
        :type: bool
        """
        return self.scc.wf

    @wf.setter
    def wf(self, value):
        self.scc._wf = value

    def __repr__(self):
        return "V{}".format(self.label)


class _Edge:
    """An edge from a :class:`._Vertex` instance to a :class:`._Vertex`
    instance.

    :param source: The source of this edge.
    :type source: :class:`._Edge`
    :param destination: The destination of this edge.
    :type destination: :class:`._Edge`
    """

    def __init__(self, source, destination):
        self._source = source
        self._destination = destination

        # holds the value count(source,S) = |E({source}) \cap S|
        self.count = None

    @property
    def source(self):
        """
        The vertex from which this edge starts.

        :type: :class:`._Vertex`
        """

        return self._source

    @property
    def destination(self):
        """
        The vertex where this edge ends.

        :type: :class:`._Vertex`
        """

        return self._destination

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
    """A qblock from the `` Paige-Tarjan `` algorithm (used also in other
    algorithms because it packs some useful methods).

    :param vertexes: The vertexes that are initially in this qblock.
    :type vertexes: list(:class:`._XBlock`)
    :param xblock: The xblock that this qblock belongs to (if any).
    :type xblock: :class:`._XBlock`
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

        self.is_new_qblock = False


    def append_vertex(self, vertex):
        """
        Append a new vertex to this qblock. Doesn't check if there are
        duplicates. Also sets the attribute :attr:`_Vertex._dllistnode` to
        the value returned by `dllistnode.append`, and updates
        :attr:`size`.

        :param vertex: The vertex to be added.
        :type vertex: :class:`._Vertex`
        """

        vertex._dllistnode = self.vertexes.append(vertex)
        self.size = self.vertexes.size
        vertex._qblock = self

    # throws an error if the vertex isn't inside this qblock
    def remove_vertex(self, vertex):
        """
        Remove the given vertex from this qblock in O(1) using the attribute
        :attr:`._Vertex._dllistnode` (should have been set in
        :func:`append_vertex`). Also updates :attr:`size`, and sets to `None`
        :attr:`._Vertex._dllistnode`.

        :param vertex: The vertex to be removed.
        :type vertex: :class:`._Vertex`
        """

        self.vertexes.remove(vertex._dllistnode)
        self.size = self.vertexes.size
        vertex._qblock = None

    def initialize_split_helper_block(self):
        """
        Initializes an empty qblock to store the :class:`._Vertex` (s) extracted
        from this qblock during a split phase.
        """

        self.split_helper_block = _QBlock([], self.xblock)

    def reset_helper_block(self):
        """
        Resets the helper qblock (check :func:`initialize_split_helper_block`).
        """
        self.split_helper_block = None

    @property
    def rank(self):
        """
        The rank of this qblock. Returns the rank of the first
        :class:`._Vertex` in :attr:`vertexes`.

        :type: int or float
        """

        if self.vertexes.first is not None:
            return self.vertexes.first.value.rank
        else:
            return None

    @property
    def xblock(self):
        """
        The xblock that this qblock belongs to (or `None`).

        :type: :class:`._XBlock`
        """

        if hasattr(self, "_xblock"):
            return self._xblock
        else:
            return None

    @xblock.setter
    def xblock(self, value):
        self._xblock = value

    @property
    def initial_partition_block_id(self):
        """
        A unique ID which identifies the block of the initial partition which
        contains this whole qblock. Uses
        :attr:`_Vertex.initial_partition_block_id`.

        :type: int
        """

        if self.vertexes.size > 0:
            return self.vertexes.first.value.initial_partition_block_id
        else:
            return None

    def merge(self, block2):
        """
        Merge this qblock with another one, calling :func:`append_vertex` on
        each :class:`._Vertex` of `block2`. Finally, deteach `block2` setting
        :attr:`.deteached` to True.

        :param block2: The qblock which is going to be merged into `self`.
        :type block2: :class:`_QBlock`
        """
        for vertex in block2.vertexes:
            self.append_vertex(vertex)
        block2.deteached = True

    def __repr__(self):
        return "Q({})".format(
            ",".join([str(vertex) for vertex in self.vertexes])
        ) + ("DET" if self.deteached else "")

    def fast_mitosis(self, extract_vertexes):
        """
        Extract a new qblock from this qblock, selecting vertexes from
        `extract_vertexes`. Runs in linear time with respect to the cardinality
        of `extract_vertexes`.

        :param extract_vertexes: The vertexes to be extracted from self.
        :type extract_vertexes: list(:class:`._Vertex`)
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
    """
    An X block from the `` Paige-Tarjan '' algorithm.
    """

    def __init__(self):
        self.qblocks = dllist([])

    @property
    def size(self):
        """
        The number of :class:`._QBlock` (s) in self.

        :type: int
        """
        return self.qblocks.size

    def append_qblock(self, qblock):
        """
        Append a new qblock to this xblock. Doesn't check if there are
        duplicates. Also sets the attribute :attr:`_QBlock._dllistnode` to
        the value returned by `dllistnode.append`.

        :param qblock: The qblock to be added.
        :type qblock: :class:`._QBlock`
        """

        qblock.dllistnode = self.qblocks.append(qblock)
        qblock.xblock = self
        return self

    def remove_qblock(self, qblock):
        """
        Remove the given qblock from this xblock in O(1) using the attribute
        :attr:`._QBlock._dllistnode` (should have been set in
        :func:`append_vertex`). Sets to `None` :attr:`._QBlock._dllistnode`.

        :param qblock: The qblock to be removed.
        :type qblock: :class:`._QBlock`
        """

        self.qblocks.remove(qblock.dllistnode)
        qblock.xblock = None

    def __repr__(self):
        return "X[{}]".format(",".join(str(qblock) for qblock in self.qblocks))


# holds the value of count(vertex,_XBlock) = |_XBlock \cap E({vertex})|
class _Count:
    """A class whcih represents a value. This is used to hold, share, and
    propagate changes in O(1) between all the interested entities (vertexes in
    the case of vertex.aux_count, edges in the case of edge.count).
    """

    def __init__(self, vertex: _Vertex):
        self.vertex = vertex
        self.value = 0

    def __repr__(self):
        return "C{}:{}".format(self.vertex, self.value)


class _SCC:
    """
    Represents a Strongly Connected Component
    (https://en.wikipedia.org/wiki/Strongly_connected_component), and holds
    its image and counterimage (in the reduced set of SCCs of the graph).

    :param int label: A unique label used to identify this SCC.
    """

    def __init__(self, label: int):
        self._label = label
        self._rank = float("-inf")

        self._image = {}
        self._counterimage = {}

        self._vertexes = set()

        self.visited = False

    def add_vertex(self, vertex):
        """
        Add a new :class:`._Vertex` to this SCC.

        :param vertex: The new vertex.
        :type vertex: :class:`._Vertex`
        """

        self.vertexes.add(vertex)
        vertex.scc = self

    @property
    def wf(self):
        """
        A flag which tells whether this SCC is well founded or not. To compute,
        it visits the SCCs in :attr:`image` and checks whether or not there is
        at least one non-well-founded SCC.

        Note that this assumes that the attribute :attr:`wf` from all the SCCs
        in :attr:`image` is updated when this property is evaluated.

        :setter: Set the attribute :attr:`self.wf`.
        :getter: Get the attribute :attr:`self.wf`.
        :type: bool
        """

        if not hasattr(self, "_wf") or self._wf is None:
            if len(self.vertexes) > 1:
                self._wf = False
            else:
                self._wf = True
                for scc in self.image:
                    if not scc.wf:
                        self._wf = False
                        break
        return self._wf

    @wf.setter
    def wf(self, value):
        self._wf = value

    @property
    def rank(self):
        """
        The rank associated with this SCC (note that rank doesn't change in
        vertexes in the same SCC, due to its definition).

        :type: int or float
        """

        return self._rank

    def mark_leaf(self):
        """
        Notify that this SCC is a leaf, and change its rank accordingly.
        """

        self._rank = 0

    def mark_scc_leaf(self):
        """
        Notify that this SCC is a leaf in the reduced graph of SCCs, and change
        its rank accordingly.
        """

        self._rank = float("-inf")

    def compute_image(self):
        """
        Build the dictionary :attr:`self.image` of this SCC visiting the
        attribute :attr:`_Vertex.image` for each vertex in
        :attr:`self.vertexes`. The unique label of each SCC is used as the key
        in the dictionary.

        Updates :attr:`self.wf` only if a self-loop in the reduced SCC graph
        is detected (a vertex in :attr:`self.vertexes` is the source of an
        edge towards a vertex in :attr:`self.vertexes`).
        """

        self._image.clear()
        for vx in self.vertexes:
            for edge in vx.image:
                # edge towards self
                if edge.destination.scc == self:
                    self.wf = False
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
        """
        Build the dictionary :attr:`._SCC.counterimage` of this SCC visiting
        the attribute :attr:`_Vertex.counterimage` for each vertex in
        :attr:`._SCC.vertexes`. The unique label of each SCC is used as the key
        in the dictionary.
        """

        self._counterimage.clear()
        for vx in self.vertexes:
            for edge in vx.counterimage:
                # edge towards self, don't include
                if edge.source.scc == self:
                    continue
                else:
                    self._counterimage[edge.source.scc.label] = edge.source.scc

    @property
    def label(self):
        """
        A unique label which identifies this SCC (used as key in the
        dictionaries :attr:`._SCC.image`, :attr:`._SCC.counterimage`).
        """

        return self._label

    @property
    def vertexes(self):
        """
        The vertexes in this SCC:

        :type: set(:class:`._Vertex`)
        """

        return self._vertexes

    @property
    def image(self):
        """
        The image (in the reduced SCC graph) of this SCC:

        :type: dict(:class:`._SCC`)
        """

        return self._image.values()

    @property
    def counterimage(self):
        """
        The counterimage (in the reduced SCC graph) of this SCC:

        :type: dict(:class:`._SCC`)
        """

        return self._counterimage.values()

    def destroy(self):
        """
        Destroy this instance (clears :attr:`self.vertexes`,
        :attr:`self.counterimage`, :attr:`self.image`).
        """

        self._vertexes.clear()
        self._image.clear()
        self._counterimage.clear()

    def join(self, other):
        """
        Merge another SCC into this one by inserting its vertexes into
        :attr:`self.vertexes`. Also calls :func:`other.destroy()`, and resets
        :attr:`self.rank`, :attr:`self.wf` to communicate other SCCs that
        we need to recompute these properties, therefore it's not recommended
        to use them at the moment.

        :param other: The SCC to be merged into `self`.
        :type other: :class:`._SCC`
        """

        for vertex in other.vertexes:
            self.add_vertex(vertex)
        self.rank = None
        self.wf = False
        other.destroy()

    def __repr__(self):
        return "SCC({})".format(
            ",".join([str(vertex) for vertex in self.vertexes])
        )
