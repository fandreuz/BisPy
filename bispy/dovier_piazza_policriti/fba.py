import networkx as nx
from typing import Iterable, List, Tuple, Dict, Union
from itertools import islice
from llist import dllist
from bispy.utilities.graph_entities import (
    _QBlock as _Block,
    _Vertex,
    _XBlock
)
from bispy.utilities.graph_decorator import decorate_nx_graph
from bispy.paige_tarjan.pta import pta
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

    Returns:
        A tuple whose first element is the single vertex which survived the
        collapse, and the second is the list of collapsed vertexes.
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
        partition.append_at_rank(block=mod_block.split_helper_block,
            rank=mod_block.split_helper_block.rank)
        mod_block.split_helper_block = None


def fba(
    graph: nx.Graph,
) -> Tuple[RankedPartition, List[List[_Vertex]]]:
    """Apply the FBA algorithm on the given integer directed graph.

    :param graph: An integer directed graph, such that the labels of its nodes
        form an integer interval starting from zero, without holes.

    Returns:
        A tuple such that the first item is the partition at the end of the
        algorithm, and the second is a list which maps a survivor nodes (which
        are the only nodes left after the collapse of a block) to the
        list of nodes collapsed to that survivor node.
    """
    vertexes, _ = decorate_nx_graph(graph)
    partition = RankedPartition(vertexes)

    # maps each survivor node to a list of nodes collapsed into it
    collapse_map = [None for _ in range(len(graph.nodes))]

    # collapse B_{-infty}
    if len(partition[0]) > 0:
        # there's only one block in partition[0] (B_{-infty}) at the moment,
        # namely partition[0][0].
        survivor_vertex, collapsed_vertexes = collapse(partition[0][0])

        if survivor_vertex is not None:
            # update the collapsed nodes map
            collapse_map[survivor_vertex.label] = collapsed_vertexes

            # update the partition
            split_upper_ranks(partition, partition[0][0])

    # loop over the ranks
    for partition_idx in range(1, len(partition)):
        # OPTIMIZATION: if at the current rank we only have blocks of single
        # vertexes, skip this step.
        if any(map(lambda block: block.size > 1, partition[partition_idx])):
            current_label = 0
            for block in partition[partition_idx]:
                for vertex in block.vertexes:
                    # scale vertex
                    vertex.scale_label(current_label)
                    current_label += 1

                    # exclude nodes having the wrong rank from the image and
                    # counterimage of the vertex. from now they're gone
                    # forever.
                    vertex.restrict_to_subgraph()

            # apply PTA to the subgraph at the current examined rank
            # CAREFUL: if you debug here, you'll see that there are some
            # "duplicate" nodes (nodes with the same label in different blocks
            # of the partition). this happens becaus of the SCALING (which is
            # used to pass a normal graph to PTA)
            rscp = pta(partition[partition_idx])

            # clear the partition at the current rank
            partition.clear_index(partition_idx)

            # insert the new blocks in the partition at the current rank, and
            # collapse each block.
            for block in rscp:
                block_vertexes = []
                for scaled_vertex in block.vertexes:
                    scaled_vertex.back_to_original_label()
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


def rscp(
    graph: nx.Graph,
    is_integer_graph: bool = False,
) -> List[Tuple]:
    """Obtain the RSCP of the given graph with the FBA algorithm.

    Args:
        graph (nx.Graph): The input graph.
        is_integer_graph (bool, optional): If True, the graph is already
            integer (needed for the algorithm). Defaults to False.

    Returns:
        List[Tuple]: The RSCP of the graph as a list of tuples.
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

    collapsed_partition, collapse_map = fba(integer_graph)

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


def bisimulation_contraction(
    graph: nx.Graph,
    is_integer_graph: bool = False,
) -> List:
    """Compute the bisimulation contraction of the graph with the FBA
    algorithm.

    Args:
        graph (nx.Graph): The input graph.
        is_integer_graph (bool, optional): If True, the graph is already
            integer (needed for the algorithm). Defaults to False.

    Returns:
        List: The bisimulation contraction as a list of survivor nodes.
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

    collapsed_partition, _ = fba(integer_graph)

    # convert to external representation (List[int])
    collapsed_graph_nodes = []
    for rank in collapsed_partition:
        for block in rank:
            if block.size > 0:
                # we want to have a tuple to recall that each vertex represents
                # a whole block
                collapsed_graph_nodes.append(
                    (block.vertexes.first.value.label,)
                )

    if original_graph_is_integer:
        return collapsed_graph_nodes
    else:
        return back_to_original(collapsed_graph_nodes, node_to_idx)
