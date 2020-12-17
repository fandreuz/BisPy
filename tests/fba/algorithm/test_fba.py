import pytest
import dovier_piazza_policriti.fba as fba
import dovier_piazza_policriti.graph_entities as entities

@pytest.mark.parametrize(
    "rank, expected",
    zip([float('-inf'), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert fba.rank_to_partition_idx(rank) == expected

@pytest.mark.parametrize(
    "block, expected",
)
def test_build_block_counterimage(block, expected):
    assert set(fba.build_block_counterimage(block)) == set(expected)
