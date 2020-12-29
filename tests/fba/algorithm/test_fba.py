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
from operator import attrgetter, or_
from functools import reduce
from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import (
    _Block,
)


@pytest.mark.parametrize(
    "rank, expected", zip([float("-inf"), *(range(5))], range(6))
)
def test_rank_to_partition_idx(rank, expected):
    assert rank_to_partition_idx(rank) == expected


@pytest.mark.parametrize(
    "graph, counterimaged_block_indexes",
    zip(
        test_cases.graphs,
        test_cases.block_counterimaged_block,
    ),
)
def test_build_block_counterimage(graph, counterimaged_block_indexes):
    vertexes, _ = prepare_graph(graph)
    counterimaged_block = _Block(
        map(lambda idx: vertexes[idx], counterimaged_block_indexes)
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
    test_cases.graphs,
)
def test_prepare_graph_max_rank(graph):
    _, max_rank = prepare_graph(graph)
    assert max_rank == max(
        map(lambda node: graph.nodes[node]["rank"], graph.nodes)
    )


@pytest.mark.parametrize(
    "graph",
    test_cases.graphs,
)
def test_prepare_graph_vertexes(graph):
    vertexes, _ = prepare_graph(graph)

    # same length
    assert len(vertexes) == len(graph.nodes)

    # same rank
    assert all(
        map(
            lambda idx: vertexes[idx].rank == graph.nodes[idx]["rank"],
            range(len(vertexes)),
        )
    )

    # counterimage
    my_counterimage = [
        map(attrgetter("label"), vertex.counterimage) for vertex in vertexes
    ]
    for edge in graph.edges:
        assert edge[0] in my_counterimage[edge[1]]
    for idx, vertex_counterimage in enumerate(my_counterimage):
        for vx in vertex_counterimage:
            assert vx in graph.adj[idx]


@pytest.mark.parametrize("graph", test_cases.graphs)
def test_create_subgraph_of_rank(graph):
    vertexes, max_rank = prepare_graph(graph)
    partition = create_initial_partition(vertexes, max_rank)
    for idx in range(len(partition)):
        rank = float("-inf") if idx == 0 else idx - 1
        # split the single block at rank "rank" in many blocks
        blocks_at_rank = [
            _Block([vertex]) for vertex in partition[idx][0].vertexes
        ]

        my_subgraph = create_subgraph_of_rank(blocks_at_rank, rank)

        # only nodes of rank "rank"
        assert len(my_subgraph.nodes) == len(partition[idx][0].vertexes)
        assert all(
            vertexes[node_idx].rank == rank for node_idx in my_subgraph.nodes
        )
        # only edges between nodes of rank "rank"
        for edge in my_subgraph.edges:
            assert vertexes[edge[0]].rank == vertexes[edge[1]].rank
            assert vertexes[edge[0]].rank == rank
        # all edges
        for edge in filter(
            lambda edge: vertexes[edge[0]].rank == vertexes[edge[0]]
            and vertexes[edge[0]].rank == rank,
            graph.edges,
        ):
            assert edge[1] in my_subgraph.adj[edge[0]]


@pytest.mark.parametrize("graph", test_cases.graphs)
def test_create_initial_partition(graph):
    vertexes, max_rank = prepare_graph(graph)
    partition = create_initial_partition(vertexes, max_rank)

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


@pytest.mark.parametrize("graph", test_cases.graphs)
def test_split_upper_ranks(graph):
    vertexes, max_rank = prepare_graph(graph)
    partition_length = 0 if max_rank == float("-inf") else max_rank + 2

    for idx in range(partition_length):
        partition = create_initial_partition(vertexes, max_rank)
        split_upper_ranks(partition, partition[idx][0])
        assert all(
            check_block_stability(partition[idx][0], upper_rank_block)
            for upper_idx in range(idx + 1, partition_length)
            for upper_rank_block in partition[upper_idx]
        )


@pytest.mark.parametrize(
    "graph",
    map(lambda tp: tp[0], graph_partition_rscp_tuples),
)
def test_fba_correctness(graph):
    assert set(frozenset(block) for block in fba_rscp(graph)) == set(
        frozenset(block) for block in paige_tarjan(graph)
    )
