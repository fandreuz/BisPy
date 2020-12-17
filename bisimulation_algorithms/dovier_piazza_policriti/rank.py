import networkx as nx
from typing import List

from .well_foundedness import mark_wf_nodes


def dfs_rank_visit(graph_scc: nx.Graph, current_scc: int):
    """A recursive step of the DFS visit. For a given SCC node, set its rank,
    and when needed visit its neighborhood. After the execution of this
    function the dictionary associated with each node in graph_scc will contain
    the key 'rank'.
    -infty = float('-inf')

    Args:
        graph_scc (nx.Graph): The SCC contraction of a graph.
        current_scc (int): The SCC node which is being visited.
    """

    # current_scc contains only a leaf of graph
    if graph_scc.nodes[current_scc].get("G-leaf"):
        graph_scc.nodes[current_scc]["rank"] = 0
    # current_scc is a leaf of graph_scc
    elif len(graph_scc.adj[current_scc]) == 0:
        graph_scc.nodes[current_scc]["rank"] = float("-inf")
    else:
        current_max = float("-inf")

        for node in graph_scc.adj[current_scc]:
            if "rank" not in graph_scc.nodes[node]:
                dfs_rank_visit(graph_scc, node)

            node_rank = graph_scc.nodes[node]["rank"]

            current_max = max(
                current_max,
                node_rank + 1 if graph_scc.nodes[node]["wf"] else node_rank,
            )

        graph_scc.nodes[current_scc]["rank"] = current_max


def build_map_to_scc(graph_scc: nx.Graph, graph: nx.Graph) -> List[frozenset]:
    """Construct a list of ints such that output[node] = [node], where [node]
    is the SCC node belongs to, and node is a vertex of the input graph.

    Args:
        graph_scc (nx.Graph): The SCC contraction of the given graph.
        graph (nx.Graph): The input graph.

    Returns:
        list[int]: The SCC map of the input graph.
    """

    scc_map = [None for node in graph.nodes]

    for scc in graph_scc.nodes:
        for node in scc:
            try:
                scc_map[node] = scc
            except Exception:
                print(
                    """you are probably using a grah whose nodes are not
                    properly numbered"""
                )
    return scc_map


def prepare_scc(graph: nx.Graph) -> nx.DiGraph:
    """Construct the SCC contraction of the given graph. The output graph comes
    with some useful info to compute the rank:
        1. well-foundedness of a SCC (key: 'wf');
        2. G-leafness of a SCC (the SCC contains only a single node which is a
            leaf of G) (key: 'G-leaf').
    This function calls mark_wf_nodes on the given graph instance.

    Args:
        graph (nx.Graph): The input graph.

    Returns:
        nx.DiGraph: The SCC contraction of the input graph.
    """

    mark_wf_nodes(graph)

    # this is the graph whose nodes are the SCC of the input graph
    graph_scc = nx.DiGraph()
    components = map(
        lambda scc: frozenset(scc), nx.strongly_connected_components(graph)
    )
    for scc in components:
        graph_scc.add_node(scc)

    # maps a given node to the corresponding SCC, so that [n] = scc_map[n],
    # where [n] is the SCC of n.
    scc_map = build_map_to_scc(graph_scc, graph)

    # add the edges to graph_scc
    for edge in graph.edges:
        # drop self loops in graph_scc
        if scc_map[edge[0]] != scc_map[edge[1]]:
            graph_scc.add_edge(scc_map[edge[0]], scc_map[edge[1]])

    # initialize the well-foundedness value for each scc to true
    for scc in graph_scc.nodes:
        graph_scc.nodes[scc]["wf"] = True

    # set wf and G-leafness. G-leafness is True if the SCC contains a single
    # node, which is a leaf of G.
    for node in graph.nodes:
        if not graph.nodes[node]["wf"]:
            graph_scc.nodes[scc_map[node]]["wf"] = False
        elif len(graph.adj[node]) == 0:
            graph_scc.nodes[scc_map[node]]["G-leaf"] = True

    return graph_scc


def compute_rank(graph: nx.Graph):
    """Compute the rank for each node of the given graph.

    Args:
        graph (nx.Graph): The input graph.
    """

    graph_scc = prepare_scc(graph)

    for scc in graph_scc.nodes:
        if "rank" not in graph_scc.nodes[scc]:
            dfs_rank_visit(graph_scc, scc)

    # propagate the value of the rank of the whole SCC to the single vertexes
    for scc_node in graph_scc.nodes:
        for node in scc_node:
            graph.nodes[node]["rank"] = graph_scc.nodes[scc_node]["rank"]

def find_max_rank(graph: nx.Graph) -> int:
    max_rank = float('-inf')
    for node in graph.nodes:
        max_rank = max(max_rank, graph.nodes[node]['rank'])
    return max_rank
