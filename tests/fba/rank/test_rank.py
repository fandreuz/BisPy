import pytest
import networkx as nx

from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import (
    compute_rank,
)
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import prepare_graph
from .rank_test_cases import noderank_dicts, graphs


@pytest.mark.parametrize("graph, node_rank_dict", zip(graphs, noderank_dicts))
def test_compute_rank(graph, node_rank_dict: dict):
    print(graph.edges)
    vertexes = prepare_graph(graph)
    compute_rank(vertexes)

    for idx in range(len(vertexes)):
        assert vertexes[idx].rank == node_rank_dict[idx]
