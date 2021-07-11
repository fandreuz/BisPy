import pytest
from bispy.utilities.graph_entities import (
    _QBlock,
    _Vertex,
    _Edge,
)
from typing import Set, Tuple, List
import networkx as nx
from bispy.saha.ranked_pta import ranked_split
from bispy.paige_tarjan.paige_tarjan import paige_tarjan
from bispy.saha.saha import add_edge
from bispy.utilities.graph_decorator import decorate_nx_graph

def partition_to_integer(partition: List[_QBlock]) -> Set[Set[int]]:
    return set(
        frozenset(vertex.label for vertex in block.vertexes)
        for block in filter(lambda b: b.vertexes.size > 0, partition)
    )


def integer_to_partition(
    partition: List[Tuple], vertexes: List[_Vertex]
) -> List[_QBlock]:
    qblocks = []
    for block in partition:
        qblocks.append(_QBlock([vertexes[i] for i in block], None))
    return qblocks


def test_resets_aux_count():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (0, 2), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3)])

    vertexes, _ = decorate_nx_graph(g)

    integer_partition = paige_tarjan(g)
    q_partition = integer_to_partition(integer_partition, vertexes)

    # now we modify the graph
    add_edge(vertexes[3], vertexes[0])

    # find [v]
    modified_destination_block = None
    for block in q_partition:
        for vertex in block.vertexes:
            if vertex.label == 0:
                modified_destination_block = block
                break

    ranked_split(q_partition, modified_destination_block, 2)

    for vx in vertexes:
        assert not hasattr(vx, 'aux_count') or vx.aux_count is None


def test_ranked_split():
    g = nx.DiGraph()
    g.add_nodes_from(range(5))
    g.add_edges_from([(0, 1), (0, 2), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3)])

    vertexes, _ = decorate_nx_graph(g)

    integer_partition = paige_tarjan(g)
    q_partition = integer_to_partition(integer_partition, vertexes)

    # now we modify the graph
    add_edge(vertexes[3], vertexes[0])

    # find [v]
    modified_destination_block = None
    for block in q_partition:
        for vertex in block.vertexes:
            if vertex.label == 0:
                modified_destination_block = block
                break

    ranked_split(q_partition, modified_destination_block, 2)

    final_integer_partition = partition_to_integer(q_partition)
    assert final_integer_partition == set(
        [frozenset([0]), frozenset([1, 2]), frozenset([3]), frozenset([4])]
    )
