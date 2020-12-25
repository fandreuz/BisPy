import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Vertex,
)
from typing import List
from .rank import compute_rank


def to_normal_graph(graph: nx.Graph) -> List[_Vertex]:
    vertexes = [
        _Vertex(label=node, rank=graph.nodes[node]["rank"])
        for node in graph.nodes
    ]

    # build the image/counterimage
    for edge in graph.edges:
        vertexes[edge[1]].append_to_counterimage(vertexes[edge[0]])

    return vertexes


def prepare_graph(graph: nx.Graph) -> List[_Vertex]:
    """Prepare the input graph for the algorithm. Computes the rank for each
    node, and then converts the graph to a usable representation.

    Args:
        graph (nx.Graph): The input graph

    Returns:
        List[_Vertex]: A convenient representation of the given graph (contains
        only nodes and edges).
    """

    compute_rank(graph)
    return to_normal_graph(graph)
