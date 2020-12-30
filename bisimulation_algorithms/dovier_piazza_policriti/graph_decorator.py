import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Vertex,
)
from typing import List, Tuple
from .rank_computation import compute_rank


def to_normal_graph(graph: nx.Graph) -> List[_Vertex]:
    max_rank = float('-inf')
    vertexes = []
    for vertex in graph.nodes:
        new_vertex = _Vertex(label=vertex)
        vertexes.append(new_vertex)

    # build the image/counterimage
    for edge in graph.edges:
        vertexes[edge[1]].add_to_counterimage(vertexes[edge[0]])
        vertexes[edge[0]].add_to_image(vertexes[edge[1]])

    return vertexes


def prepare_graph(graph: nx.Graph) -> List[_Vertex]:
    """Prepare the input graph for the algorithm. Computes the rank for each
    node, and then converts the graph to a usable representation.

    Args:
        graph (nx.Graph): The input graph

    Returns:
        List[_Vertex]: A convenient representation of the given graph (contains
            only nodes and edges).
        int          : The maximum rank in the graph.
    """

    vertexes = to_normal_graph(graph)
    # sets ranks
    compute_rank(vertexes)

    return vertexes
