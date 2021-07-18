import networkx as nx
from enum import Enum, auto
from functools import wraps
from bispy.saha.saha import saha as saha_internal
from bispy import (
    paige_tarjan,
    dovier_piazza_policriti,
    decorate_nx_graph,
    paige_tarjan_qblocks,
)
from typing import List, Tuple, Union
from bispy.utilities.graph_decorator import to_tuple_list


def saha_generator_non_updating(graph: nx.Graph, initial_edges=None):
    """Provides a generator that keeps extending the `graph` from the provided `initial_edges`

    Example:
        >>> graph = networkx.balanced_tree(2,3)
        >>> list(saha_generator_non_updating(graph, [(1, 0), (4, 0)]))
        [[Q(V3,V5,V6), Q(V7,V8,V9,V10,V11,V12,V13,V14), Q(), Q(), Q(), Q(), Q(), Q()],
         [Q(V3,V5,V6), Q(V7,V8,V9,V10,V11,V12,V13,V14), Q(V0), Q(V2), Q(V1), Q(V4)]]

    :param graph: The input graph.
    :param initial_edges: The edges the iterator adds iteratively to the graph
    :returns: An iterator over maximum bisimulations.
    """
    initial_edges = initial_edges or []
    vertexes, qblocks = decorate_nx_graph(graph)
    maximum_bisimulation = paige_tarjan_qblocks(qblocks)
    for edge in initial_edges:
        maximum_bisimulation = saha_internal(
            maximum_bisimulation, vertexes, edge
        )
        yield maximum_bisimulation


class SahaIterator:
    """Similar to `saha_generator_non_updating`, but allows the user to incrementally add new edges to the pool.

    Example:
        ```
        def update(it):
            it.add_edge((4, 0))

        correct_results = ([(3, 4, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,)],
                   [(3, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,), (4,)])
        it = SahaIterator(graph, [(1, 0)])
        for i, max_bisim in enumerate(map(to_tuple_list, it)):
            assert max_bisim == correct_results[i]
            if i == 0: # if we want to add edges to the graph
                update(it)
        ```
    """

    def __init__(self, graph: nx.Graph, initial_edges=None):
        self.graph = graph
        self.next_edges = []
        self.current_iter = saha_generator_non_updating(
            self.graph, initial_edges
        )

    def __iter__(self):
        return self

    def add_edge(self, edge):
        self.next_edges.append(edge)

    def __next__(self):
        try:
            return next(self.current_iter)
        except StopIteration as e:
            if self.next_edges:
                self.current_iter = saha_generator_non_updating(
                    self.graph, self.next_edges
                )
                self.next_edges = []
                return self.__next__()
            else:
                raise e


def saha_iter(graph: nx.Graph, initial_edges=None):
    return SahaIterator(graph, initial_edges)


def total_saha(graph: nx.Graph, edges: List[Tuple[int]]):
    """Adds edges to the graph one after another and returns the final result."""
    return to_tuple_list(list(saha_iter(graph, edges))[-1])


class MaxBisimAlgorithm(Enum):
    PaigeTarjan = auto()
    DovierPiazzaPolicriti = auto()
    TotalSaha = auto()


def find_max_bisimulation(
    graph: nx.DiGraph, algorithm=MaxBisimAlgorithm.PaigeTarjan, **args
):
    """Find the maximum bisimulation of a `graph` using the provided `algorithm`.

    Example:
        >>> import networkx as nx
        >>> from bispy import find_max_bisimulation, MaxBisimAlgorithm
        >>> graph = nx.balanced_tree(2,3, create_using=nx.DiGraph)
        >>> find_max_bisimulation(graph)
        [(3, 4, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (1, 2), (0,)]
        >>> find_max_bisimulation(graph), algorithm=MaxBisimAlgorithm.TotalSaha, edges=[(1, 0), (4, 0)])
        [(3, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,), (4,)]
        >>> find_max_bisimulation(graph), algorithm=MaxBisimAlgorithm.DovierPiazzaPolicriti)
        [(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6), (1, 2), (0,)]

    :param graph: The input graph.
    :param algorithm: The algorithm used to compute the total bisimulation.
    :param args: Optional arguments for the used algorithm. Refer to the "bare" functions for possible arguments.
    :returns: The maximum bisimulation as a list of tuples.

    """
    if algorithm == MaxBisimAlgorithm.PaigeTarjan:
        return paige_tarjan(graph, **args)
    elif algorithm == MaxBisimAlgorithm.DovierPiazzaPolicriti:
        return dovier_piazza_policriti(graph, **args)
    elif algorithm == MaxBisimAlgorithm.TotalSaha:
        return total_saha(graph, **args)
