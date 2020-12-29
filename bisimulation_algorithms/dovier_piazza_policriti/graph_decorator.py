import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Vertex,
)
from typing import List, Tuple
from .rank import compute_rank


def to_normal_graph(graph: nx.Graph) -> Tuple[List[_Vertex], int]:
    max_rank = float('-inf')
    vertexes = []
    for vertex in graph.nodes:
        new_vertex = _Vertex(label=vertex, rank=graph.nodes[vertex]["rank"])
        max_rank = max(max_rank, new_vertex.rank)
        vertexes.append(new_vertex)

    # build the image/counterimage
    for edge in graph.edges:
        vertexes[edge[1]].append_to_counterimage(vertexes[edge[0]])

    return (vertexes, max_rank)


def prepare_graph(graph: nx.Graph) -> Tuple[List[_Vertex], int]:
    """Prepare the input graph for the algorithm. Computes the rank for each
    node, and then converts the graph to a usable representation.

    Args:
        graph (nx.Graph): The input graph

    Returns:
        List[_Vertex]: A convenient representation of the given graph (contains
            only nodes and edges).
        int          : The maximum rank in the graph.
    """

    compute_rank(graph)
    return to_normal_graph(graph)
