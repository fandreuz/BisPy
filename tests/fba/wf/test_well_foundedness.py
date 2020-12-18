import networkx as nx
import pytest

from bisimulation_algorithms.dovier_piazza_policriti.well_foundedness import _WHITE, _BLACK, dfs_wf_visit, mark_wf_nodes

import wf_test_cases as test_cases

def test_dfs_wf_visit_visits_neighborhood():
    graph = nx.DiGraph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (2, 4)])

    for node in range(5):
        graph.nodes[node]["wf"] = True
        graph.nodes[node]["color"] = _WHITE

    dfs_wf_visit(graph, 0)

    # the algorithm visited all the neigbors of 0
    assert all([graph.nodes[node]["color"] == _BLACK for node in range(5)])

    assert graph.nodes[0]["wf"]

@pytest.mark.parametrize("graph, wf_nodes, nwf_nodes", test_cases.graphs_wf_nwf)
def test_mark_wf_nodes_correct(graph, wf_nodes, nwf_nodes):
    mark_wf_nodes(graph)

    for i in range(len(graph.nodes)):
        assert (i in wf_nodes and graph.nodes[i]["wf"]) or (
            i in nwf_nodes and not graph.nodes[i]["wf"]
        )
