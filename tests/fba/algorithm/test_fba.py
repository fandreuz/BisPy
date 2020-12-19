import pytest
import bisimulation_algorithms.dovier_piazza_policriti.fba as fba
import bisimulation_algorithms.dovier_piazza_policriti.graph_entities as entities
import tests.fba.algorithm.fba_test_cases as test_cases
import networkx as nx


@pytest.mark.parametrize(
    "rank, expected", zip([float("-inf"), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert fba.rank_to_partition_idx(rank) == expected


@pytest.mark.parametrize(
    "block, expected",
    zip(
        test_cases.block_counterimage_cases,
        test_cases.block_counterimage_expected,
    ),
)
def test_build_block_counterimage(block, expected):
    assert set(fba.build_block_counterimage(block)) == set(expected)


@pytest.mark.parametrize(
    "graph, expected",
    zip(test_cases.prepare_graph_cases, test_cases.prepare_graph_expected),
)
def test_prepare_graph(graph, expected):
    assert set(fba.prepare_graph(graph)) == set(expected)


@pytest.mark.parametrize(
    "blocks_at_rank, rank, expected_graph",
    zip(
        test_cases.create_subgraph_cases,
        test_cases.create_subgraph_cases_rank,
        test_cases.create_subgraph_expected,
    ),
)
def test_create_subgraph_of_rank(blocks_at_rank, rank, expected_graph):
    result = fba.create_subgraph_of_rank(blocks_at_rank, rank)

    isomorphic = nx.is_isomorphic(result, expected_graph)
    same_nodes = list(result.nodes) == list(expected_graph.nodes)
    assert isomorphic and same_nodes


@pytest.mark.parametrize(
    "vertexes, expected",
    zip(
        test_cases.initial_partition_cases,
        test_cases.initial_partition_expected,
    ),
)
def test_create_initial_partition(vertexes, expected):
    partition = fba.create_initial_partition(vertexes)

    for idx in range(len(partition)):
        # initially there's only one block per rank
        assert len(partition[idx]) == 1 or idx == 0

        assert set(frozenset(block.vertexes) for block in partition[idx]) == set(frozenset(block) for block in expected[idx])
