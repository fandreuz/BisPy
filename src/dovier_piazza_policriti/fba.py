import networkx as nx
import dovier_piazza_policriti.rank as rank
import paige_tarjan.pta_algorithm as pta

# TODO: improve performance
def collapse(graph, blocks: list[list]):
    if len(nodes) > 0:
        keep_node = list(nodes)[0]

        for node in nodes:
            if node == keep_node:
                pass
            else:
                incident_edges = list(filter(lambda edge: edge[1] == node or edge[0] == node, graph.edges))

                # replace edges incident to node with eges incident to keep_node
                graph.add_edges_from(map(lambda edge: (keep_node, edge[1]) if edge[0] == node else (edge[0], keep_node), incident_edges))

                graph.remove_node(node)

def split2(graph, node, partition, from_index):
    pass

def fba(graph: nx.Graph):
    """Apply the FBA algorithm to the given graph. The graph is modified in order to obtain the maximum bisimulation contraction.

    Args:
        graph (nx.Graph): The input graph.
    """

    rank.compute_rank(graph)

    # find the maximum rank
    max_rank = float('-inf')
    for node in graph.nodes:
        max_rank = max(max_rank, graph.nodes[node]['rank'])

    # initialize the initial partition. the first index is for -infty
    # partition contains is a list of lists, each sub-list contains the sub-blocks of nodes at the i-th rank
    if max_rank != float('-inf'):
        partition = [[] for _ in range(max_rank + 2)]
    else:
        # there's a single possible rank, -infty
        partition = [[]]

    # populate the blocks of the partition according to the ranks
    for node in graph.nodes:
        if graph.nodes[node]['rank'] == float('-inf'):
            # rank is -infty, therefore we put this node in the first position of the list
            partition_idx = 0
        else:
            # rank is not -infty
            partition_idx = graph.nodes[node]['rank'] + 1

        # put this node in the (only) list at partition_idx in partition (there's only one block for each rank at the moment in the partition)
        partition[partition_idx][0].add(node)

    # collapse B_{-infty}
    if len(partition[0]) > 0:
        # pass the blocks of rank -infty to collapse
        collapse(graph, partition[0])
        # extract the first node of the first list of the first index in position
        survivor_node = partition[0][0][0]
        # update the partition
        split2(graph, survivor_node, partition, 1)

    # loop over the ranks
    for i in range(1, max_rank + 2):
        pta.rscp()
        collapse(graph, partition[i])
        split2(graph, )

