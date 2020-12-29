import pytest
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    rank_to_partition_idx,
    build_block_counterimage,
    prepare_graph,
    create_subgraph_of_rank,
    create_initial_partition,
    split_upper_ranks,
    fba,
    rscp as fba_rscp,
)
import tests.fba.algorithm.fba_test_cases as test_cases
import networkx as nx
from tests.fba.rscp_utilities import check_block_stability
from tests.pta.pta_test_cases import graph_partition_rscp_tuples
from bisimulation_algorithms.paige_tarjan.pta import (
    rscp as paige_tarjan,
)


@pytest.mark.parametrize(
    "rank, expected", zip([float("-inf"), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert rank_to_partition_idx(rank) == expected


@pytest.mark.parametrize(
    "block, expected",
    zip(
        test_cases.block_counterimage_cases,
        test_cases.block_counterimage_expected,
    ),
)
def test_build_block_counterimage(block, expected):
    assert set(build_block_counterimage(block)) == set(expected)


@pytest.mark.parametrize(
    "graph, expected",
    zip(test_cases.prepare_graph_cases, test_cases.prepare_graph_expected),
)
def test_prepare_graph(graph, expected):
    assert set(prepare_graph(graph)[0]) == set(expected)


@pytest.mark.parametrize(
    "blocks_at_rank, rank, expected_graph",
    zip(
        test_cases.create_subgraph_cases,
        test_cases.create_subgraph_cases_rank,
        test_cases.create_subgraph_expected,
    ),
)
def test_create_subgraph_of_rank(blocks_at_rank, rank, expected_graph):
    result = create_subgraph_of_rank(blocks_at_rank, rank)

    isomorphic = nx.is_isomorphic(result, expected_graph)
    same_nodes = set(result.nodes) == set(expected_graph.nodes)
    assert isomorphic and same_nodes


@pytest.mark.parametrize(
    "vertexes, expected",
    zip(
        test_cases.initial_partition_cases,
        test_cases.initial_partition_expected,
    ),
)
def test_create_initial_partition(vertexes, expected):
    partition = create_initial_partition(
        vertexes, max(map(lambda v: v.rank, vertexes))
    )

    for idx in range(len(partition)):
        # initially there's only one block per rank
        assert len(partition[idx]) == 1 or idx == 0

        assert set(
            frozenset(block.vertexes) for block in partition[idx]
        ) == set(frozenset(block) for block in expected[idx])


@pytest.mark.parametrize(
    "partition, block",
    zip(
        test_cases.split_upper_rank_partitions,
        test_cases.split_upper_rank_splitters,
    ),
)
def test_split_upper_ranks(partition, block):
    split_upper_ranks(partition, block)

    if block.rank == float("-inf"):
        block_rank_idx = 0
    else:
        block_rank_idx = block.rank + 1

    for rank in range(block_rank_idx, len(partition)):
        for block2 in partition[rank]:
            assert check_block_stability(block, block2)


@pytest.mark.parametrize(
    "graph",
    map(lambda tp: tp[0], graph_partition_rscp_tuples),
)
def test_fba_correctness(graph):
    assert set(frozenset(block) for block in fba_rscp(graph)) == set(
        frozenset(block) for block in paige_tarjan(graph)
    )
