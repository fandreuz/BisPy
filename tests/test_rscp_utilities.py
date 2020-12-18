import networkx as nx
import pytest


from bisimulation_algorithms.paige_tarjan.graph_decorator import initialize
from bisimulation_algorithms.utilities.rscp_utilities import is_stable_partition, check_block_stability

def build_test_partition(graph, partition, expected):
    _, vertexes = initialize(graph, partition)
    return ([[vertexes[idx] for idx in block] for block in partition], expected)


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
    "partition, result",
    map(lambda tp: build_test_partition(*tp), graphs_partition_expected),
)
def test_check_is_stable_partition(partition, result):
    assert is_stable_partition(partition) == result


def build_test_blocks(graph, partition, expected):
    _, vertexes = initialize(graph, partition)
    return (*[[vertexes[idx] for idx in block] for block in partition][0:2], expected)


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
