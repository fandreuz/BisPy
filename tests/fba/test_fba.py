import pytest
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    rank_to_partition_idx,
    build_block_counterimage,
    prepare_graph,
    create_initial_partition,
    split_upper_ranks,
    fba,
    rscp as fba_rscp,
    bisimulation_contraction as fba_contraction,
)
from .fba_test_cases import graphs, block_counterimaged_block, fba_correctness_graphs
import networkx as nx
from tests.pta.rscp_utilities import check_block_stability
from tests.pta.pta_test_cases import graph_partition_rscp_tuples
from bisimulation_algorithms.paige_tarjan.pta import (
    rscp as paige_tarjan,
)
from operator import attrgetter, or_
from functools import reduce
from bisimulation_algorithms.utilities.graph_entities import (
    _QBlock as _Block,
)


@pytest.mark.parametrize(
    "rank, expected", zip([float("-inf"), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert rank_to_partition_idx(rank) == expected
@pytest.mark.parametrize(
    "graph, counterimaged_block_indexes",
    zip(
        graphs,
        block_counterimaged_block,
    ),
)
def test_build_block_counterimage(graph, counterimaged_block_indexes):
    vertexes = prepare_graph(graph)
    counterimaged_block = _Block(
        map(lambda idx: vertexes[idx], counterimaged_block_indexes), None
    )

    my_counterimage_as_labels = list(
        map(attrgetter("label"), build_block_counterimage(counterimaged_block))
    )

    for edge in graph.edges:
        if edge[1] in counterimaged_block_indexes:
            assert edge[0] in my_counterimage_as_labels
    for counterimage_vertex in my_counterimage_as_labels:
        assert reduce(
            or_,
            [
                vertex in graph.adj[counterimage_vertex]
                for vertex in counterimaged_block_indexes
            ],
        )


@pytest.mark.parametrize(
    "graph",
    graphs,
)
def test_prepare_graph_vertexes(graph):
    vertexes = prepare_graph(graph)

    # same length
    assert len(vertexes) == len(graph.nodes)

    # counterimage
    my_counterimage = [
        [
            counterimage_edge.source.label
            for counterimage_edge in vertex.counterimage
        ]
        for vertex in vertexes
    ]
    for edge in graph.edges:
        assert edge[0] in my_counterimage[edge[1]]
    for idx, vertex_counterimage in enumerate(my_counterimage):
        for vx in vertex_counterimage:
            assert idx in graph.adj[vx]


@pytest.mark.parametrize("graph", graphs)
def test_create_initial_partition(graph):
    vertexes = prepare_graph(graph)
    partition = create_initial_partition(vertexes)

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


@pytest.mark.parametrize("graph", graphs)
def test_split_upper_ranks(graph):
    vertexes = prepare_graph(graph)
    max_rank = max(vertex.rank for vertex in vertexes)
    partition_length = 0 if max_rank == float("-inf") else max_rank + 2

    for idx in range(partition_length):
        partition = create_initial_partition(vertexes)
        split_upper_ranks(partition, partition[idx][0])
        assert all(
            check_block_stability(
                partition[idx][0], upper_rank_block
            )
            for upper_idx in range(idx + 1, partition_length)
            for upper_rank_block in partition[upper_idx]
        )


@pytest.mark.parametrize(
    "graph",
    map(lambda tp: tp[0], graph_partition_rscp_tuples),
)
def test_fba_rscp_correctness(graph):
    assert set(frozenset(block) for block in fba_rscp(graph)) == set(
        frozenset(block) for block in paige_tarjan(graph)
    )


@pytest.mark.parametrize(
    "graph",
    map(lambda tp: tp[0], graph_partition_rscp_tuples),
)
def test_fba_collapse_correctness(graph):
    contraction = fba_contraction(graph)
    rscp = paige_tarjan(graph)
    assert all(
        any(vertex in block for block in rscp) for vertex in contraction
    )


# this is for particular cases which aren't covered in PTA tests
@pytest.mark.parametrize(
    "graph",
    fba_correctness_graphs,
)
def test_fba_correctness2(graph):
    assert set(frozenset(block) for block in fba_rscp(graph)) == set(
        frozenset(block) for block in paige_tarjan(graph)
    )
