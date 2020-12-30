import networkx as nx
import pytest

from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Block,
    _Vertex,
)
from tests.fba.rscp_utilities import check_block_stability
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    to_normal_graph,
)


def build_test_blocks(graph, partition, expected):
    # this is needed to avoid an error
    for node in graph.nodes:
        graph.nodes[node]["rank"] = 0
    vertexes = to_normal_graph(graph)
    return (
        _Block([vertexes[idx] for idx in partition[0]], None),
        _Block([vertexes[idx] for idx in partition[1]], None),
        expected,
    )


graphs_partition_expected = [
    (nx.DiGraph(), [(0, 1), (2,)], True),
    (nx.DiGraph(), [(0, 1), (2,), (3, 4)], True),
    (nx.DiGraph(), [(0, 1), (2,), (3,)], False),
]
# A: 0,1 B: 2, subset
graphs_partition_expected[0][0].add_edges_from([(0, 2), (1, 2), (2, 2)])
# A: 0,1 B: 2, intersection empty
graphs_partition_expected[1][0].add_edges_from([(0, 3), (1, 4), (2, 2)])
# A: 0,1 B: 2, fail
graphs_partition_expected[2][0].add_edges_from([(0, 2), (1, 3), (2, 2)])


@pytest.mark.parametrize(
    "block1, block2, result",
    map(lambda tp: build_test_blocks(*tp), graphs_partition_expected),
)
def test_check_block_stability(block1, block2, result):
    assert check_block_stability(block1, block2) == result
