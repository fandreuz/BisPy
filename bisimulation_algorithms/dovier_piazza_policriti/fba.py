import networkx as nx
from typing import Iterable, List, Tuple, Dict
from itertools import islice
from llist import dllist

from .graph_entities import _Block, _Vertex
from .graph_decorator import to_normal_graph, prepare_graph
from bisimulation_algorithms.paige_tarjan.pta import pta

from bisimulation_algorithms.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)

from bisimulation_algorithms.paige_tarjan.graph_entities import _XBlock


def create_initial_partition(
    vertexes: List[_Vertex], max_rank: int
) -> List[List[_Block]]:
    """Create a partition where vertexes are in different blocks if their rank
    is not equal.

    Args:
        vertexes (List[_Vertex]): The list of vertexes.
        max_rank (int): The maximum rank which appears in vertexes.

    Returns:
        List[List[_Block]]: The initial partition.
    """

    # initialize the initial partition. the first index is for -infty
    # partition contains is a list of lists, each sub-list contains the
    # sub-blocks of nodes at the i-th rank
    if max_rank != float("-inf"):
        partition = [[_Block([], _XBlock())] for i in range(max_rank + 2)]
    else:
        # there's a single possible rank, -infty
        partition = [[_Block([], _XBlock())]]

    # populate the blocks of the partition according to the ranks
    for vertex in vertexes:
        # put this node in the (only) list at partition_idx in partition
        # (there's only one block for each rank at the moment in the partition)
        partition[rank_to_partition_idx(vertex.rank)][0].append_vertex(vertex)

    return partition


def rank_to_partition_idx(rank: int) -> int:
    """Convert the rank of a block/vertex to its index in the list
    which represents a partition.

    Args:
        rank (int): The input rank (int or float('-inf'))

    Returns:
        int: The index in the partition.
    """

    if rank == float("-inf"):
        return 0
    else:
        return rank + 1


def collapse(block: _Block) -> Tuple[_Vertex, List[_Vertex]]:
    """Collapse the given block in a single vertex chosen randomly from the
    vertexes of the block.

    Args:
        block (_Block):    The block to collapse.

    Returns:
        _Vertex      : The vertex which survived to the collapse.
        List[_Vertex]: The list of collapsed vertexes.
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
    """Given a block B, construct the counterimage of the block.

    Args:
        block (_Block): A block.

    Returns:
        list[_Vertex]: A list of vertexes x such that x->y and y is in the
        given block.
    """

    block_counterimage = []

    for vertex in block.vertexes:
        for counterimage_vertex in vertex.counterimage:
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


def split_upper_ranks(partition: List[List[_Block]], block: _Block):
    """Update the blocks whose rank is greater than block.rank, in order to
    make the partition stable with respect to the block.

    Args:
        partition (List[List[_Block]]): The current partition.
        block (_Block): The splitter block.
    """

    block_counterimage = build_block_counterimage(block)

    modified_blocks = []

    for vertex in block_counterimage:
        # if this is an upper-rank node with respect to the collapsed block, we
        # can split it from its block
        if vertex.rank > block.rank():
            # if needed, create the aux block to help during the splitting
            # phase
            if vertex.qblock.split_helper_block is None:
                vertex.qblock.split_helper_block = _Block(
                    [], vertex.qblock.xblock
                )
                modified_blocks.append(vertex.qblock)

            new_vertex_block = vertex.qblock.split_helper_block

            # remove the vertex in the counterimage from its current block
            vertex.qblock.remove_vertex(vertex)
            # put the vertex in the counterimage in the aux block
            new_vertex_block.append_vertex(vertex)

    # insert the new blocks in the partition, and then reset aux block for each
    # modified block.
    for block in modified_blocks:
        # we use the rank of aux block because we're sure it's not None
        partition[
            rank_to_partition_idx(block.split_helper_block.rank())
        ].append(block.split_helper_block)
        block.split_helper_block = None


def fba(
    graph: nx.Graph,
) -> Tuple[List[List[_Block]], List[List[_Vertex]]]:
    """Apply the FBA algorithm on the given integer directed graph.

    Args:
        graph (nx.Graph): An integer directed graph.

    Returns:
        List[List[_Block]   : The partition at the end of the algorithm.
        List[List[_Vertex]] : A list which maps survivor nodes to the list of
            nodes collapsed to that survivor node.
    """

    vertexes = prepare_graph(graph)
    max_rank = max(vertex.rank for vertex in vertexes)
    partition = create_initial_partition(vertexes, max_rank)

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
        # PTA wants an interval without holes starting from zero, therefore we
        # need to scale
        scaled_idx_to_vertex = []
        for block in partition[partition_idx]:
            for vertex in block.vertexes:
                vertex.scale_label(len(scaled_idx_to_vertex))
                scaled_idx_to_vertex.append(vertex)

        # apply PTA to the subgraph at the current examined rank
        rscp = pta(partition[partition_idx])

        # clear the partition at the current rank
        partition[partition_idx] = []

        # insert the new blocks in the partition at the current rank, and
        # collapse each block.
        for block in rscp:
            block_vertexes = []
            for scaled_vertex_idx in block:
                vertex = scaled_idx_to_vertex[scaled_vertex_idx]
                vertex.back_to_original_label()
                block_vertexes.append(vertex)

            # we can set XBlock to None because PTA won't be called again on
            # these blocks
            internal_block = _Block(block_vertexes, None)

            survivor_vertex, collapsed_vertexes = collapse(internal_block)

            if survivor_vertex is not None:
                # update the collapsed nodes map
                collapse_map[survivor_vertex.label] = collapsed_vertexes
                # add the new block to the partition
                partition[partition_idx].append(internal_block)
                # update the upper ranks with respect to this block
                split_upper_ranks(partition, internal_block)

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
                collapsed_graph_nodes.append(block.vertexes.first.value.label)

    if original_graph_is_integer:
        return collapsed_graph_nodes
    else:
        return back_to_original(collapsed_graph_nodes, node_to_idx)
