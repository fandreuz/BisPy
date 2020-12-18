import networkx as nx
from .graph_entities import _Vertex, _Block
from typing import List


def to_normal_graph(graph: nx.Graph) -> List[_Vertex]:
    vertexes = [_Vertex(label=node, rank=graph.nodes[node]['rank']) for node in graph.nodes]

    # build the image/counterimage
    for edge in graph.edges:
        vertexes[edge[0]].append_to_image(vertexes[edge[1]])
        vertexes[edge[1]].append_to_counterimage(vertexes[edge[0]])

    return vertexes
