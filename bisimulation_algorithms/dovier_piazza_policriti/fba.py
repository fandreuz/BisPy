import networkx as nx
from typing import Iterable, List, Tuple
from itertools import islice

from .graph_entities import _Block, _Vertex
from .graph_decorator import to_normal_graph, prepare_graph
from bisimulation_algorithms import paige_tarjan


""" def collapse(block: Iterable[_Vertex]) -> _Vertex:
    # prevent index exception
    if len(block) > 0:
        keep_node = list(block)[0]

        # skip the first node
        for vertex in islice(block, start=1):
            vertex.collapsed_to = keep_node

        return keep_node """


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
                vertex.block.aux_block = _Block(vertex.block.rank)
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

            # exclude nodes whose rank is not correct
            image_rank_i = filter(
                lambda image_vertex: image_vertex.rank == rank, vertex.image
            )
            # add edges going out from vertex to the subgraph
            subgraph.add_edges_from(
                (vertex.label, image_vertex.label)
                for image_vertex in image_rank_i
            )

    return subgraph


def create_initial_partition(vertexes: List[_Vertex]) -> List[List[_Block]]:
    # find the maximum rank in the graph
    max_rank = max(map(lambda vertex: vertex.rank, vertexes))

    # initialize the initial partition. the first index is for -infty
    # partition contains is a list of lists, each sub-list contains the
    # sub-blocks of nodes at the i-th rank
    if max_rank != float("-inf"):
        partition = [[_Block(i - 1)] for i in range(max_rank + 2)]
    else:
        # there's a single possible rank, -infty
        partition = [[_Block(float("-inf"))]]

    # populate the blocks of the partition according to the ranks
    for vertex in vertexes:
        # put this node in the (only) list at partition_idx in partition
        # (there's only one block for each rank at the moment in the partition)
        partition[rank_to_partition_idx(vertex.rank)][0].append_vertex(vertex)

    return partition


def fba(graph: nx.Graph) -> List[Tuple]:
    """Apply the FBA algorithm to the given graph. The graph is modified in
    order to obtain the maximum bisimulation contraction.

    Args:
        graph (nx.Graph): The input graph.
    """

    vertexes = prepare_graph(graph)
    partition = create_initial_partition(vertexes)

    # collapse B_{-infty}
    if len(partition[0]) > 0:
        # there's only one block in partition[0] (B_{-infty}) at the moment,
        # namely partition[0][0].
        # survivor_node = collapse(partition[0][0])

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

        # collapse all the blocks in B_i
        # for rscp_block in rscp:
        #    collapse(rscp_block)

        # update the partition
        for collapsed_block in partition[partition_idx]:
            split_upper_ranks(partition, collapsed_block)

    rscp = []

    for rank in partition:
        for block in rank:
            if block.vertexes.size > 0:
                rscp.append(
                    tuple(map(lambda vertex: vertex.label, block.vertexes))
                )

    return rscp
