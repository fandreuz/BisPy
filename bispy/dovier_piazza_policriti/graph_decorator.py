import networkx as nx
from bispy.utilities.graph_entities import _Edge, _Vertex
from typing import List, Tuple
from bispy.utilities.rank_computation import (
    compute_rank,
)

_BLACK = 10
_GRAY = 11
_WHITE = 12


def counterimage_dfs(
    current_vertex_idx: int,
    vertexes: List[_Vertex],
    finishing_list: List[_Vertex],
    colors: List[int],
):
    # mark this vertex as "visiting"
    colors[current_vertex_idx] = _GRAY
    # visit the counterimage of the current vertex
    for edge in vertexes[current_vertex_idx].counterimage:
        counterimage_vertex = edge.source

        # if the vertex isn't white, a visit is occurring, or has already
        # occurred.
        if colors[counterimage_vertex.label] == _WHITE:
            counterimage_dfs(
                current_vertex_idx=counterimage_vertex.label,
                vertexes=vertexes,
                finishing_list=finishing_list,
                colors=colors,
            )
    # this vertex visit is over: add the vertex to the ordered list of
    # finished vertexes
    finishing_list.append(vertexes[current_vertex_idx])
    # mark this vertex as "visited"
    colors[current_vertex_idx] = _BLACK


def compute_counterimage_finishing_time_list(
    vertexes: List[_Vertex],
) -> List[_Vertex]:
    counterimage_dfs_colors = [_WHITE for _ in range(len(vertexes))]
    counterimage_finishing_list = []
    # perform counterimage DFS
    for idx in range(len(vertexes)):
        if counterimage_dfs_colors[idx] == _WHITE:
            counterimage_dfs(
                current_vertex_idx=idx,
                vertexes=vertexes,
                finishing_list=counterimage_finishing_list,
                colors=counterimage_dfs_colors,
            )
    return counterimage_finishing_list


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

    finishing_time_list = compute_counterimage_finishing_time_list(vertexes)
    build_vertexes_image(finishing_time_list)

    # sets ranks
    compute_rank(vertexes)

    return vertexes
