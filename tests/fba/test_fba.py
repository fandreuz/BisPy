import pytest
from bispy.dovier_piazza_policriti.ranked_partition import RankedPartition
from bispy.dovier_piazza_policriti.dovier_piazza_policriti import (
    build_block_counterimage,
    split_upper_ranks,
    dovier_piazza_policriti
)
from .fba_test_cases import graphs, block_counterimaged_block, fba_correctness_graphs
import networkx as nx
from tests.pta.rscp_utilities import check_block_stability
from tests.pta.pta_test_cases import graph_partition_rscp_tuples
from bispy.paige_tarjan.paige_tarjan import paige_tarjan
from operator import attrgetter, or_
from functools import reduce
from bispy.utilities.graph_entities import (
    _QBlock as _Block,
)
from bispy.utilities.graph_decorator import decorate_nx_graph


@pytest.mark.parametrize(
    "graph, counterimaged_block_indexes",
    zip(
        graphs,
        block_counterimaged_block,
    ),
)
def test_build_block_counterimage(graph, counterimaged_block_indexes):
    vertexes, _ = decorate_nx_graph(graph)
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
    vertexes, _ = decorate_nx_graph(graph)

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
def test_split_upper_ranks(graph):
    vertexes, _ = decorate_nx_graph(graph)
    max_rank = max(vertex.rank for vertex in vertexes)
    partition_length = 0 if max_rank == float("-inf") else max_rank + 2

    for idx in range(partition_length):
        partition = RankedPartition(vertexes)
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
    assert set(frozenset(block) for block in dovier_piazza_policriti(graph)) == set(
        frozenset(block) for block in paige_tarjan(graph)
    )

# this is for particular cases which aren't covered in PTA tests
@pytest.mark.parametrize(
    "graph",
    fba_correctness_graphs,
)
def test_fba_correctness2(graph):
    assert set(frozenset(block) for block in dovier_piazza_policriti(graph)) == set(
        frozenset(block) for block in paige_tarjan(graph)
    )
