import pytest
from bispy.dovier_piazza_policriti.ranked_partition import RankedPartition
from .fba_test_cases import graphs
from bispy.utilities.graph_decorator import decorate_nx_graph

@pytest.mark.parametrize(
    "rank, expected", zip([float("-inf"), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert RankedPartition.rank_to_partition_idx(rank) == expected

@pytest.mark.parametrize("graph", graphs)
def test_create_initial_partition(graph):
    vertexes, _ = decorate_nx_graph(graph)
    partition = RankedPartition(vertexes)

    # at most one block per rank
    assert all(len(partition[idx]) for idx in range(len(partition)))

    # right vertexes in the right place
    for idx in range(len(partition)):
        rank = float("-inf") if idx == 0 else idx - 1
        # right number of vertexes
        assert partition[idx][0].vertexes.size == [
            vertex.rank == rank for vertex in vertexes
        ].count(True)
        # only right vertexes
        assert all(
            vertex.rank == rank for vertex in partition[idx][0].vertexes
        )
