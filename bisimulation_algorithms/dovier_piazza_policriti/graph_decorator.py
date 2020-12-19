import networkx as nx
import dovier_piazza_policriti.graph_entities as entities
from typing import List


def to_normal_graph(graph: nx.Graph) -> List[entities._Vertex]:
    vertexes = [entities._Vertex(label=node, rank=graph.nodes[node]['rank']) for node in graph.nodes]

    # build the image/counterimage
    for edge in graph.edges:
        vertexes[edge[0]].append_to_image(vertexes[edge[1]])
        vertexes[edge[1]].append_to_counterimage(vertexes[edge[0]])

    return vertexes
