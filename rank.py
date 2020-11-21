import networkx as nx

WHITE = 10
GRAY = 11
BLACK = 12


def dfs_wf_visit(graph, current_node):
    if graph.nodes[current_node]["color"] == BLACK:
        return

    graph.nodes[current_node]["color"] = GRAY

    for destination in graph.adj[current_node]:
        if not graph.nodes[destination]["wf"]:
            graph.nodes[current_node]["wf"] = False
        elif graph.nodes[destination]["color"] == GRAY:
            graph.nodes[current_node]["wf"] = False
            graph.nodes[destination]["wf"] = False
        elif graph.nodes[destination]["color"] == WHITE:
            dfs_wf_visit(graph, destination)
            # se la chiamata ricorsiva scopre che destination è nwf, anche current_node è nwf
            if not graph.nodes[destination]["wf"]:
                graph.nodes[current_node]["wf"] = False

    graph.nodes[current_node]["color"] = BLACK


def well_founded_nodes(graph):
    for node in graph.nodes:
        graph.nodes[node]["wf"] = True
        graph.nodes[node]["color"] = WHITE

    for node in filter(lambda node: graph.nodes[node]["color"] == WHITE, graph.nodes):
        dfs_wf_visit(graph, node)

    for node in graph.nodes:
        del graph.nodes[node]["color"]


def dfs_rank_visit(graph_scc, current_scc):
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
                current_max, node_rank + 1 if graph_scc.nodes[node]["wf"] else node_rank
            )

        graph_scc.nodes[current_scc]["rank"] = current_max


# build an array which maps a given node to the corresponding scc
def build_map_to_scc(graph_scc, graph):
    scc_map = [frozenset() for node in graph.nodes]
    for scc in graph_scc.nodes:
        for node in scc:
            try:
                scc_map[node] = scc
            except:
                print(
                    "you are probably using a grah whose nodes are not properly numbered"
                )
    return scc_map


def prepare_scc(graph):
    well_founded_nodes(graph)

    graph_scc = nx.DiGraph()
    components = map(
        lambda scc: frozenset(scc), nx.strongly_connected_components(graph)
    )
    for scc in components:
        graph_scc.add_node(scc)

    # maps a given node to the corresponding scc
    scc_map = build_map_to_scc(graph_scc, graph)

    # edges
    for edge in graph.edges:
        # drop circular edges
        if scc_map[edge[0]] != scc_map[edge[1]]:
            graph_scc.add_edge(scc_map[edge[0]], scc_map[edge[1]])

    for scc in graph_scc.nodes:
        graph_scc.nodes[scc]["wf"] = True

    # wf and G-leafness
    for node in graph.nodes:
        if not graph.nodes[node]["wf"]:
            graph_scc.nodes[scc_map[node]]["wf"] = False
        elif len(graph.adj[node]) == 0:
            graph_scc.nodes[scc_map[node]]["G-leaf"] = True

    return graph_scc


def compute_rank(graph):
    graph_scc = prepare_scc(graph)

    for scc_node in filter(
        lambda node: "rank" not in graph_scc.nodes[node], graph_scc.nodes
    ):
        dfs_rank_visit(graph_scc, scc_node)

    for scc_node in graph_scc.nodes:
        for node in scc_node:
            graph.nodes[node]["rank"] = graph_scc.nodes[scc_node]["rank"]
