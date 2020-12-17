import pytest
import dovier_piazza_policriti.fba as fba
import dovier_piazza_policriti.graph_entities as entities
import tests.fba.algorithm.fba_test_cases as test_cases

@pytest.mark.parametrize(
    "rank, expected",
    zip([float('-inf'), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert fba.rank_to_partition_idx(rank) == expected

@pytest.mark.parametrize(
    "block, expected",
    zip(test_cases.block_counterimage_cases, test_cases.block_counterimage_expected)
)
def test_build_block_counterimage(block, expected):
    assert set(fba.build_block_counterimage(block)) == set(expected)

@pytest.mark.parametrize(
    "graph, expected",
    zip(test_cases.prepare_graph_cases, test_cases.prepare_graph_expected)
)
def test_prepare_graph(graph, expected):
    assert set(fba.prepare_graph(graph)) == set(expected)
