import networkx as nx
import dovier_piazza_policriti.rank as rank
import paige_tarjan.pta_algorithm as pta
import dovier_piazza_policriti.graph_entities as entities
from typing import Iterable, List
from itertools import islice
import dovier_piazza_policriti.graph_decorator as decorator


def collapse(block: Iterable[entities._Vertex]) -> entities._Vertex:
    # prevent index exception
    if len(block) > 0:
        keep_node = list(block)[0]

        # skip the first node
        for vertex in islice(block, start=1):
            vertex.collapsed_to = keep_node

        return keep_node


def build_block_counterimage(block: entities._Block) -> List[entities._Vertex]:
    """Given a block B, construct a list of vertexes x such that x->y and y is in B.

    Args:
        block (entities._Block): A block.

    Returns:
        list[entities._Vertex]: A list of vertexes x such that x->y and y is in B (the order doesn't matter).
    """

    block_counterimage = []

    for vertex in block.vertexes:
        for counterimage_vertex in vertex.counterimage:
            # this vertex should be added to the counterimage only if necessary (avoid duplicates)
            if not counterimage_vertex.visited:
                block_counterimage.append(counterimage_vertex)
                # remember to release this vertex
                counterimage_vertex.visit()

    for vertex in block_counterimage:
        # release this vertex so that it can be visited again in a next splitting phase
        vertex.release()

    return block_counterimage


def rank_to_partition_idx(rank: int) -> int:
    """Convert the rank of a block/vertex to its expected index in the list which represents the partition of nodes.

    Args:
        rank (int): The input rank (int or float('-inf'))

    Returns:
        int: The index in the partition of a block such that block.rank = rank
    """

    if rank == float("-inf"):
        return 0
    else:
        return rank + 1


def split_upper_ranks(partition: List[List[entities._Block]], block: entities._Block):
    """Update the blocks of the partition whose rank is greater than block.rank, in order to make the partition stable with respect to block.

    Args:
        partition (List[List[entities._Block]]): The current partition.
        block (entities._Block): The block the partition has to be stable with respect to.
    """

    block_counterimage = build_block_counterimage(block)

    modified_blocks = []

    for vertex in block_counterimage:
        # if this is an upper-rank node with respect to the collapsed block, we can split it from its block
        if vertex.rank > block.rank:
            # if needed, create the aux block to help during the splitting phase
            if vertex.block.aux_block == None:
                vertex.block.aux_block = entities._Block(vertex.block.rank)
                modified_blocks.append(vertex.block)

            # remove the vertex in the counterimage from its current block
            vertex.block.remove_vertex(vertex)
            # put the vertex in the counterimage in the aux_block
            vertex.block.aux_block.insert_vertex(vertex)

    # insert the new blocks in the partition, and then reset aux_block for each modified node
    for block in modified_blocks:
        partition[rank_to_partition_idx(block.rank)].append(block.aux_block)
        block.aux_block = None


def prepare_graph(graph: nx.Graph) -> List[entities._Vertex]:
    """Prepare the input graph for the algorithm. Computes the rank for each node, and then converts the graph to a usable representation.

    Args:
        graph (nx.Graph): The input graph

    Returns:
        List[entities._Vertex]: A convenient representation of the given graph (contains only nodes and edges).
    """

    rank.compute_rank(graph)
    return decorator.to_normal_graph(graph)


def create_subgraph_of_rank(
    partition: List[List[entities._Block]], rank: int
) -> nx.Graph:
    """Creates a subgraph of nodes having the given rank, from the given partition.

    Args:
        partition (List[List[entities._Block]]): The current partition.
        rank (int): Rank of the nodes in the subgraph.

    Returns:
        nx.Graph: The subgraph.
    """

    subgraph = nx.DiGraph()

    if rank == float("-inf"):
        idx = 0
    else:
        idx = rank + 1
    blocks_rank_i = partition[idx]

    vertexes = []
    for block in blocks_rank_i:
        for vertex in block:
            image_rank_i = filter(
                lambda image_vertex: image_vertex.rank == rank, vertex.image
            )
            subgraph.add_edges_from(
                [(vertex, image_vertex) for image_vertex in image_rank_i]
            )

    subgraph.add_nodes_from(vertexes)

    return subgraph


def fba(graph: nx.Graph):
    """Apply the FBA algorithm to the given graph. The graph is modified in order to obtain the maximum bisimulation contraction.

    Args:
        graph (nx.Graph): The input graph.
    """

    vertexes = prepare_graph(graph)
    # find the maximum rank in the graph
    max_rank = max(map(lambda vertex: vertex.rank, vertexes))

    # initialize the initial partition. the first index is for -infty
    # partition contains is a list of lists, each sub-list contains the sub-blocks of nodes at the i-th rank
    if max_rank != float("-inf"):
        partition = [[entities._Block()] for _ in range(max_rank + 2)]
    else:
        # there's a single possible rank, -infty
        partition = [[entities._Block()]]

    # populate the blocks of the partition according to the ranks
    for vertex in vertexes:
        # put this node in the (only) list at partition_idx in partition (there's only one block for each rank at the moment in the partition)
        partition[rank_to_partition_idx(vertex.rank)][0].insert_vertex(vertex)

    # collapse B_{-infty}
    if len(partition[0]) > 0:
        # there's only one block in partition[0] (B_{-infty}) at the moment, namely partition[0][0]
        #survivor_node = collapse(partition[0][0])

        # update the partition
        split_upper_ranks(partition, first_rank_idx=1, collapsed_rank=float("-inf"))

    # loop over the ranks
    for i in range(1, max_rank + 2):
        # create the subgraph of rank i-1
        subgraph = create_subgraph_of_rank(partition[i], i - 1)

        # apply PTA to the subgraph at rank i
        rscp = pta.rscp(subgraph, partition[i])

        # collapse all the blocks in B_i
        #for rscp_block in rscp:
        #    collapse(rscp_block)

        # update the partition
        split_upper_ranks(partition, first_rank_idx=i + 1, collapsed_rank=i - 1)
