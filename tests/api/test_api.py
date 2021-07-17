from bispy.api.api import saha_generator_non_updating, saha_iter
from bispy.utilities.graph_decorator import to_tuple_list
import pytest
import networkx as nx
import tests.api.api_test_cases as test_cases


@pytest.mark.parametrize("graph, initial_edges, correct_results", test_cases.ins_n_outs)
def test_non_updating_generator_works(graph, initial_edges, correct_results):
    for i, max_bisim in enumerate(saha_generator_non_updating(graph, initial_edges)):
        res = to_tuple_list(max_bisim)
        assert correct_results[i] == res


@pytest.mark.parametrize("graph, initial_edges, correct_results", test_cases.ins_n_outs)
def test_iterator_works(graph, initial_edges, correct_results):
    def update(i, it):
        it.add_edge(initial_edges[i + 1])

    it = saha_iter(graph, [initial_edges[0]])
    for i, max_bisim in enumerate(it):
        assert to_tuple_list(max_bisim) == correct_results[i]
        if i < len(initial_edges) - 1:
            update(i, it)
