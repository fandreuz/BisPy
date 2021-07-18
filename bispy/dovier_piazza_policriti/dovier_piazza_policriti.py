import networkx as nx
from typing import Iterable, List, Tuple, Dict, Union
from itertools import islice
from llist import dllist
from bispy.utilities.graph_entities import _QBlock as _Block, _Vertex, _XBlock
from bispy.utilities.graph_decorator import decorate_nx_graph
from bispy.paige_tarjan.paige_tarjan import paige_tarjan_qblocks
from bispy.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)
from bispy.utilities.graph_entities import _XBlock
from bispy.dovier_piazza_policriti.ranked_partition import RankedPartition


def collapse(block: _Block) -> Tuple[_Vertex, List[_Vertex]]:
    """Collapse the given block to a single vertex chosen randomly from the
    vertexes of the block.

    :param block: The block to collapse.
    :returns: A tuple whose first element is the single vertex which survived
        the collapse, and the second is the list of collapsed vertexes.
    """

    if block.vertexes.size > 0:
        # "randomly" select a survivor node
        survivor_node = block.vertexes.first.value

        collapsed_nodes = []

        vertex = block.vertexes.first.next
        # set all the other nodes to collapsed
        while vertex is not None:
            collapsed_nodes.append(vertex.value)

            # append the counterimage of vertex to survivor_node
            survivor_node.counterimage.extend(vertex.value.counterimage)

            # acquire a pointer to the next vertex in the list
            next_vertex = vertex.next
            # remove the current vertex from the block
            block.vertexes.remove(vertex)
            # point vertex to the next vertex to be collapsed
            vertex = next_vertex

        return (survivor_node, collapsed_nodes)
    else:
        return (None, None)


def build_block_counterimage(block: _Block) -> List[_Vertex]:
    """Given a block B, construct its counterimage with respect to the binary
    relation :math:`E` (edges of the graph).

    :param block: The block for which we intend to build the counterimage.
    """

    block_counterimage = []

    for vertex in block.vertexes:
        for edge in vertex.counterimage:
            counterimage_vertex = edge.source

            # this vertex should be added to the counterimage only if necessary
            # (avoid duplicates)
            if not counterimage_vertex.visited:
                block_counterimage.append(counterimage_vertex)
                # remember to release this vertex
                counterimage_vertex.visit()

    for vertex in block_counterimage:
        # release this vertex so that it can be visited again in a next
        # splitting phase
        vertex.release()

    return block_counterimage


def split_upper_ranks(partition: RankedPartition, block: _Block):
    """Split the blocks whose `rank` is **greater** than `block.rank` using
    `block` as *splitter*.

    :param partition: The current partition.
    :param block: The splitter block.
    """

    block_counterimage = build_block_counterimage(block)

    modified_blocks = []

    for vertex in block_counterimage:
        # if this is an upper-rank node with respect to the collapsed block, we
        # need to split. the split is not needed if the block is a singoletto.
        if vertex.rank > block.rank and not (
            vertex.qblock.split_helper_block is None
            and vertex.qblock.size <= 1
        ):
            # if needed, create the aux block to help during the splitting
            # phase
            if vertex.qblock.split_helper_block is None:
                vertex.qblock.initialize_split_helper_block()
                modified_blocks.append(vertex.qblock)

            new_vertex_block = vertex.qblock.split_helper_block

            # remove the vertex in the counterimage from its current block
            vertex.qblock.remove_vertex(vertex)
            # put the vertex in the counterimage in the aux block
            new_vertex_block.append_vertex(vertex)

    # insert the new blocks in the partition, and then reset aux block for each
    # modified block.
    for mod_block in modified_blocks:
        # we use the rank of aux block because we're sure it's not None
        partition.append_at_rank(
            block=mod_block.split_helper_block,
            rank=mod_block.split_helper_block.rank,
        )
        mod_block.split_helper_block = None


def dovier_piazza_policriti_partition(
    partition: RankedPartition,
) -> Tuple[RankedPartition, List[List[_Vertex]]]:
    """Apply *Dovier-Piazza-Policriti*'s algorithm to the given ranked
    partition.

    :param partition: A ranked partition (:math:`P` in the paper).
    :returns: A tuple such that the first item is the partition at the end of
        the algorithm (which at this point is made of blocks of size 1
        containing only the vertexes which survived the collapse), and the
        second is a list which maps a survivor nodes to the list of nodes
        collapsed to that survivor node.
    """

    # maps each survivor node to a list of nodes collapsed into it
    collapse_map = [None for _ in range(partition.nvertexes)]

    # loop over the ranks
    for partition_idx in range(len(partition)):
        if len(partition[partition_idx]) == 1:
            if len(partition[partition_idx][0].vertexes):
                block = partition[partition_idx][0]
                survivor_vertex, collapsed_vertexes = collapse(block)
                if survivor_vertex is not None:
                    # update the collapsed nodes map
                    collapse_map[survivor_vertex.label] = collapsed_vertexes
                    # update the partition
                    split_upper_ranks(partition, block)
        # OPTIMIZATION: if at the current rank we only have blocks of single
        # vertexes, skip this step.
        elif any(map(lambda block: block.size > 1, partition[partition_idx])):
            current_label = 0
            for block in partition[partition_idx]:
                for vertex in block.vertexes:
                    # scale vertex
                    vertex.scale_label(current_label)
                    current_label += 1

                    # exclude nodes having the wrong rank from the image and
                    # counterimage of the vertex. from now they're gone
                    # forever.
                    vertex.restrict_to_subgraph(
                        validation=lambda vx: vx.rank == vertex.rank
                    )

            # apply PTA to the subgraph at the current examined rank
            # CAREFUL: if you debug here, you'll see that there are some
            # "duplicate" nodes (nodes with the same label in different blocks
            # of the partition). this happens becaus of the SCALING (which is
            # used to pass a normal graph to PTA)
            rscp = paige_tarjan_qblocks(partition[partition_idx])

            # clear the partition at the current rank
            partition.clear_index(partition_idx)

            # insert the new blocks in the partition at the current rank, and
            # collapse each block.
            for block in rscp:
                block_vertexes = []
                for scaled_vertex in block.vertexes:
                    scaled_vertex.back_to_original_label()
                    scaled_vertex.back_to_original_graph()
                    block_vertexes.append(scaled_vertex)

                # we can set XBlock to None because PTA won't be called again
                # on these blocks
                internal_block = _Block(block_vertexes, None)

                survivor_vertex, collapsed_vertexes = collapse(internal_block)

                if survivor_vertex is not None:
                    # update the collapsed nodes map
                    collapse_map[survivor_vertex.label] = collapsed_vertexes
                    # add the new block to the partition
                    partition.append_at_index(internal_block, partition_idx)
                    # update the upper ranks with respect to this block
                    split_upper_ranks(partition, internal_block)
        else:
            for block in partition[partition_idx]:
                # update the upper ranks with respect to this block
                split_upper_ranks(partition, block)

    return (partition, collapse_map)


def dovier_piazza_policriti(
    graph: nx.Graph,
    initial_partition: List[Tuple[int]] = None,
    is_integer_graph: bool = False,
) -> List[Tuple]:
    """Compute the RSCP/maximum bisimulation of the given graph using
    *Dovier-Piazza-Policriti*'s algorithm.

    Example:
        >>> graph = networkx.balanced_tree(2,3)
        >>> dovier_piazza_policriti(graph)
        [(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6), (1, 2), (0,)]

    This function works with integer graph (nodes are integers starting from
    0 and form an interval without holes). If the given graph is non-integer
    it is converted to an isomorphic integer graph automatically (unless
    `is_integer_graph` is `True`) and then re-converted to its original form
    after the end of the computation. For this reason nodes of `graph` **must**
    be hashable objects.

    .. warning::
        Using a non integer graph and setting `is_integer_graph` to `True`
        will probably make the function fail with an exception, or, even worse,
        return a wrong output.

    :param graph: The input graph.
    :param initial_partition: The initial partition (or labeling set). Defaults
        to `None`, in which case the trivial labeling set (one block which
        contains all the nodes) is used.
    :param is_integer_graph: If `True`, we do not check if the given graph is
        integer (saves time). If `is_integer_graph` is `True` but the graph
        is not integer the output may be wrong. Defaults to False.
    :returns: The RSCP/maximum bisimulation of the given labeling set as a
        list of tuples, each of which contains bisimilar nodes.
    """

    if not isinstance(graph, nx.DiGraph):
        raise Exception("graph should be a directed graph (nx.DiGraph)")

    # if True, the input graph is already an integer graph
    original_graph_is_integer = is_integer_graph or check_normal_integer_graph(
        graph
    )

    if not original_graph_is_integer:
        # convert the graph to an "integer" graph
        integer_graph, node_to_idx = convert_to_integer_graph(graph)
    else:
        integer_graph = graph

    vertexes, _ = decorate_nx_graph(integer_graph, initial_partition)
    partition = RankedPartition(vertexes)

    tp = dovier_piazza_policriti_partition(partition)
    collapsed_partition, collapse_map = tp

    # from the collapsed partition obtained from FBA, build the RSCP (external
    # representation, List[Tuple[int]])
    rscp = []
    for rank in collapsed_partition:
        for block in rank:
            if block.vertexes.size > 0:
                block_survivor_node = block.vertexes.first.value
                block_vertexes = [block_survivor_node.label]

                if collapse_map[block_survivor_node.label] is not None:
                    block_vertexes.extend(
                        map(
                            lambda vertex: vertex.label,
                            collapse_map[block_survivor_node.label],
                        )
                    )

                rscp.append(tuple(block_vertexes))

    if original_graph_is_integer:
        return rscp
    else:
        return back_to_original(rscp, node_to_idx)
