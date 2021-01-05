import pytest
import networkx as nx

from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
    counterimage_dfs,
    _WHITE,
)
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    prepare_graph,
)
from .rank_test_cases import noderank_dicts, graphs


@pytest.mark.parametrize("graph, node_rank_dict", zip(graphs, noderank_dicts))
def test_compute_rank(graph, node_rank_dict: dict):
    vertexes = prepare_graph(graph)
    compute_rank(vertexes)

    for idx in range(len(vertexes)):
        assert vertexes[idx].rank == node_rank_dict[idx]


def test_dfs_counterimage():
    graph = graphs[6]
    vertexes = prepare_graph(graph)

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

    node_to_finishing = dict(
        (vertex.label, idx)
        for idx, vertex in enumerate(counterimage_finishing_list)
    )

    assert node_to_finishing[4] < node_to_finishing[7]
    assert node_to_finishing[4] < node_to_finishing[2]
