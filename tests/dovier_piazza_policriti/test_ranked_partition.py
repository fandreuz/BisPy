import pytest
from bispy.dovier_piazza_policriti.ranked_partition import RankedPartition
from .dovier_piazza_policriti_test_cases import graphs
from bispy.utilities.graph_decorator import decorate_nx_graph
import networkx as nx
from bispy.utilities.graph_entities import _QBlock


@pytest.mark.parametrize(
    "rank, expected", zip([float("-inf"), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert RankedPartition.rank_to_partition_idx(rank) == expected


@pytest.mark.parametrize("graph", graphs)
def test_create_initial_partition(graph):
    vertexes, _ = decorate_nx_graph(graph)
    partition = RankedPartition(vertexes)

    # at least one block per rank, except for float('-inf')
    assert all(len(partition[idx]) for idx in range(1, len(partition)))

    # right vertexes in the right place
    for idx in range(len(partition)):
        rank = float("-inf") if idx == 0 else idx - 1

        # right number of vertexes
        assert partition[idx][0].vertexes.size == [
            vertex.rank == rank for vertex in vertexes
        ].count(True)
        # right rank
        assert all(
            vertex.rank == rank for vertex in partition[idx][0].vertexes
        )


@pytest.mark.parametrize("graph", graphs)
def test_nvertexes(graph):
    vertexes, _ = decorate_nx_graph(graph)
    partition = RankedPartition(vertexes)
    assert partition.nvertexes == len(graph.nodes)


def test_get_item():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    assert partition[0] == partition._partition[0]


def test_append_at_rank():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    block = _QBlock([], None)
    partition.append_at_rank(block, 1)
    assert partition[2][-1] == block


def test_append_at_index():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    block = _QBlock([], None)
    partition.append_at_index(block, 1)
    assert partition[1][-1] == block


def test_len():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    assert len(partition) == 5


def test_scc_leaf_length():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    assert partition[0][0].size == 0


def test_clear_rank():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    partition.clear_rank(1)
    assert len(partition[2]) == 0


def test_clear_index():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    partition.clear_index(1)
    assert len(partition[1]) == 0

def test_iter():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    idx = 0
    for r in partition:
        assert r == partition._partition[idx]
        idx += 1

def test_get_item():
    vertexes, _ = decorate_nx_graph(nx.balanced_tree(2, 3))
    partition = RankedPartition(vertexes)
    assert partition[1] == partition._partition[1]
