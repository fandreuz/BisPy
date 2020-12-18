import networkx as nx

# a node which hasn't been visited yet
_WHITE = 10
# a node whose neighborood is being visited in the current recursion tree of the algorithm
_GRAY = 11
# a node which has already been visited
_BLACK = 12


def dfs_wf_visit(graph: nx.Graph, current_node: int):
    """A recursive step of the algorithm for the well-foundedness of a graph. Visits all the neighboroods of current_node (DFS) and then mark it as visited.

    Args:
        graph (nx.Graph): The graph.
        current_node (int): The node which is being visited (must be accessible with graph.nodes[current_node]).
    """

    if graph.nodes[current_node]["color"] == _BLACK:
        return

    graph.nodes[current_node]["color"] = _GRAY

    for destination in graph.adj[current_node]:
        if not graph.nodes[destination]["wf"]:
            graph.nodes[current_node]["wf"] = False
        elif graph.nodes[destination]["color"] == _GRAY:
            graph.nodes[current_node]["wf"] = False
            graph.nodes[destination]["wf"] = False
        elif graph.nodes[destination]["color"] == _WHITE:
            dfs_wf_visit(graph, destination)
            # se la chiamata ricorsiva scopre che destination è nwf, anche current_node è nwf
            if not graph.nodes[destination]["wf"]:
                graph.nodes[current_node]["wf"] = False

    graph.nodes[current_node]["color"] = _BLACK


def mark_wf_nodes(graph: nx.Graph):
    """Visit the given graph and mark the nodes "well-founded" or "not-well-founded". After the execution of this function the dictionary associated to each node in the graph will contain the key 'wf', True if the node is well-founded, False otherwise.
    If the input graph contains the entry 'color', the value will be erased.

    Args:
        graph (nx.Graph): The input graph.
    """

    # intialize the keys
    for node in graph.nodes:
        graph.nodes[node]["wf"] = True
        graph.nodes[node]["color"] = _WHITE

    for node in graph.nodes:
        if graph.nodes[node]["color"] == _WHITE:
            dfs_wf_visit(graph, node)

    # remove the key 'color'
    for node in graph.nodes:
        del graph.nodes[node]["color"]
