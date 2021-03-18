import networkx as nx
from bisimulation_algorithms.utilities.graph_entities import _Edge, _Vertex
from typing import List, Tuple
from .rank_computation import compute_rank, compute_finishing_time_list


def to_normal_graph(graph: nx.Graph) -> List[_Vertex]:
    max_rank = float("-inf")
    vertexes = []
    for vertex in graph.nodes:
        new_vertex = _Vertex(label=vertex)
        vertexes.append(new_vertex)

    # build the counterimage. the image will be constructed using the order
    # imposed by the rank algorithm
    for edge in graph.edges:
        edge = _Edge(vertexes[edge[0]], vertexes[edge[1]])
        vertexes[edge.destination.label].add_to_counterimage(edge)

    return vertexes


# this re-arranges the image of each vertex in a convenient order for further
# visits
def build_vertexes_image(finishing_time_list: List[_Vertex]):
    # use the standard vertex ordering
    vertex_count = [None for _ in range(len(finishing_time_list))]

    for time_list_idx in range(len(finishing_time_list) - 1, -1, -1):
        vertex = finishing_time_list[time_list_idx]

        # use the counterimage of the current vertex to update the images of
        # the nodes in the counterimage of the current vertex.
        for edge in vertex.counterimage:
            edge.source.add_to_image(edge)


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

    finishing_time_list = compute_finishing_time_list(vertexes)
    build_vertexes_image(finishing_time_list)

    # sets ranks
    compute_rank(vertexes, finishing_time_list)

    return vertexes
