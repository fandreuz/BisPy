import networkx as nx
from typing import Iterable, List, Tuple, Dict
from itertools import islice

from .graph_entities import _Block, _Vertex
from .graph_decorator import to_normal_graph, prepare_graph
from bisimulation_algorithms import paige_tarjan

from bisimulation_algorithms.utilities.graph_normalization import (
    check_normal_integer_graph,
    convert_to_integer_graph,
    back_to_original,
)


def collapse(block: _Block) -> Tuple[_Vertex, List[_Vertex]]:
    """Collapse the given block in a single vertex chosen randomly from the
    vertexes of the block.

    Args:
        block (_Block):    The block to collapse.

    Returns:
        Tuple[_Vertex, List[_Vertex]]: A tuple which contains the single vertex
        in the block after the collapse, and the list of collapsed vertexes.
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
    """Given a block B, construct a list of vertexes x such that x->y and y is
    in B.

    Args:
        block (_Block): A block.

    Returns:
        list[_Vertex]: A list of vertexes x such that x->y and y is in B (the
        order doesn't matter).
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


def rank_to_partition_idx(rank: int) -> int:
    """Convert the rank of a block/vertex to its expected index in the list
    which represents the partition of nodes.

    Args:
        rank (int): The input rank (int or float('-inf'))

    Returns:
        int: The index in the partition of a block such that block.rank = rank
    """

    if rank == float("-inf"):
        return 0
    else:
        return rank + 1


def split_upper_ranks(partition: List[List[_Block]], block: _Block):
    """Update the blocks of the partition whose rank is greater than
    block.rank, in order to make the partition stable with respect to block.

    Args:
        partition (List[List[_Block]]): The current partition.
        block (_Block): The block the partition has to be stable with respect
        to.
    """

    block_counterimage = build_block_counterimage(block)

    modified_blocks = []

    for vertex in block_counterimage:
        # if this is an upper-rank node with respect to the collapsed block, we
        # can split it from its block
        if vertex.rank > block.rank:
            # if needed, create the aux block to help during the splitting
            # phase
            if vertex.block.aux_block is None:
                vertex.block.aux_block = _Block(vertex.block.rank, [])
                modified_blocks.append(vertex.block)

            new_vertex_block = vertex.block.aux_block

            # remove the vertex in the counterimage from its current block
            vertex.block.remove_vertex(vertex)
            # put the vertex in the counterimage in the aux_block
            new_vertex_block.append_vertex(vertex)

    # insert the new blocks in the partition, and then reset aux_block for each
    # modified node
    for block in modified_blocks:
        partition[rank_to_partition_idx(block.rank)].append(block.aux_block)
        block.aux_block = None


def create_subgraph_of_rank(
    blocks_at_rank: List[_Block], rank: int
) -> nx.Graph:
    """Creates a subgraph of nodes having the given rank, from the given
    partition.

    Args:
        partition (List[List[_Block]]): The current partition.
        rank (int): Rank of the nodes in the subgraph.

    Returns:
        nx.Graph: The subgraph.
    """

    subgraph = nx.DiGraph()

    vertexes_at_rank = []
    for block in blocks_at_rank:
        for vertex in block.vertexes:
            # add a new block to the subgraph
            subgraph.add_node(vertex.label)

            # add the edges from the nodes whose rank is OK
            for src in vertex.counterimage:
                if src.rank == rank:
                    subgraph.add_edge(src.label, vertex.label)

    return subgraph


def create_initial_partition(vertexes: List[_Vertex]) -> List[List[_Block]]:
    # find the maximum rank in the graph
    max_rank = max(map(lambda vertex: vertex.rank, vertexes))

    # initialize the initial partition. the first index is for -infty
    # partition contains is a list of lists, each sub-list contains the
    # sub-blocks of nodes at the i-th rank
    if max_rank != float("-inf"):
        partition = [[_Block(i - 1, [])] for i in range(max_rank + 2)]
    else:
        # there's a single possible rank, -infty
        partition = [[_Block(float("-inf"), [])]]

    # populate the blocks of the partition according to the ranks
    for vertex in vertexes:
        # put this node in the (only) list at partition_idx in partition
        # (there's only one block for each rank at the moment in the partition)
        partition[rank_to_partition_idx(vertex.rank)][0].append_vertex(vertex)

    return partition


def fba(graph: nx.Graph) -> List[Tuple[int]]:
    """Apply the FBA algorithm to the given graph.

    Args:
        graph (nx.Graph): The input (integer) graph.

    Returns:
        List[Tuple[int]]: The RSCP of the graph.
    """

    vertexes = prepare_graph(graph)
    partition = create_initial_partition(vertexes)

    # maps each survivor node to a list of nodes collapsed into it
    collapse_map = {}

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
        rank = partition_idx - 1

        # create the subgraph of rank i-1
        subgraph = create_subgraph_of_rank(partition[partition_idx], rank)

        # convert FBA blocks to tuple blocks
        blocks_at_rank = [
            tuple(map(lambda vertex: vertex.label, block.vertexes))
            for block in partition[partition_idx]
        ]

        # apply PTA to the subgraph at rank i
        rscp = paige_tarjan(subgraph, blocks_at_rank)

        # clear the partition at the current rank
        partition[partition_idx] = []

        # insert the new blocks in the partition at the current rank, and
        # collapse each block.
        for block in rscp:
            internal_block = _Block(
                rank, map(lambda vertex_idx: vertexes[vertex_idx], block)
            )

            survivor_vertex, collapsed_vertexes = collapse(internal_block)

            if survivor_vertex is not None:
                # update the collapsed nodes map
                collapse_map[survivor_vertex.label] = collapsed_vertexes
                # add the new block to the partition
                partition[partition_idx].append(internal_block)
                # update the upper ranks with respect to this block
                split_upper_ranks(partition, internal_block)

    rscp = []

    # from the partition obtained from the first step, build a partition which
    # in the external representation (List[Tuple[int]])
    for rank in partition:
        for block in rank:
            if block.vertexes.size > 0:
                block_survivor_node = block.vertexes.first.value
                block_vertexes = [block_survivor_node.label]

                if block_survivor_node.label in collapse_map:
                    block_vertexes.extend(
                        map(
                            lambda vertex: vertex.label,
                            collapse_map[block_survivor_node.label],
                        )
                    )

                rscp.append(tuple(block_vertexes))

    return rscp


def rscp(
    graph: nx.Graph,
    is_integer_graph: bool = False,
) -> List[Tuple]:
    """Compute the RSCP of the given graph. This function needs to work with an
    integer graph (nodes represented by an integer), therefore it checks this
    property before starting the FBA algorithm, and creates an integer graph if
    needed. Nodes in the graph have to be hashable objects.

    Args:
        graph (nx.Graph): The input graph.
        is_integer_graph (bool, optional): If True, the function assumes that
        the graph is integer, and skips the integrality check (may be useful
        when performance is important). Defaults to False.

    Returns:
        List[Tuple]: The RSCP of the given (even non-integer) graph, with the
        given initial partition.
    """

    # if True, the input graph is already an integer graph
    original_graph_is_integer = is_integer_graph or check_normal_integer_graph(
        graph
    )

    if not original_graph_is_integer:
        # convert the graph to an "integer" graph
        integer_graph, node_to_idx = convert_to_integer_graph(graph)
    else:
        integer_graph = graph

    rscp = fba(integer_graph)

    if original_graph_is_integer:
        return rscp
    else:
        return back_to_original(rscp, node_to_idx)
