# TODO: improve performance
def collapse(graph, nodes):
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
