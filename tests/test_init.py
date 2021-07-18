import pytest
from bispy import Algorithms, compute_maximum_bisimulation, paige_tarjan
import networkx as nx
from bispy.utilities.graph_decorator import to_set


def test_compute():
    graph = nx.balanced_tree(2, 3, create_using=nx.DiGraph)
    initial_partition = [
        (0, 1, 2), (3, 4), (5, 6), (7, 8, 9, 10), (11, 12, 13), (14,)
    ]

    assert to_set(compute_maximum_bisimulation(
        graph, initial_partition
    )) == to_set(paige_tarjan(graph, initial_partition))

    assert to_set(compute_maximum_bisimulation(
        graph, initial_partition, algorithm=Algorithms.DovierPiazzaPolicriti
    )) == to_set(paige_tarjan(graph, initial_partition))

    assert to_set(compute_maximum_bisimulation(
        graph, initial_partition, algorithm=Algorithms.PaigeTarjan
    )) == to_set(paige_tarjan(graph, initial_partition))
