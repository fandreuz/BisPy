import networkx as nx
import dovier_piazza_policriti.graph_entities as entities
from typing import List


def to_normal_graph(graph: nx.Graph) -> List[entities._Vertex]:
    vertexes_counterimage = [[] for _ in range(graph.nodes)]
    vertexes_image = [[] for _ in range(graph.nodes)]

    # build the image/counterimage
    for edge in graph.edges:
        vertexes_image[edge[0]].append(edge[1])
        vertexes_counterimage[edge[1]].append(edge[0])

    # initialize the new representations
    return [
        entities._Vertex(
            graph.nodes[node]["rank"],
            neighborhoods=vertexes_image,
            counterimage=vertexes_counterimage[node],
        )
        for node in graph.nodes
    ]
