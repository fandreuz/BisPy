import pytest
import networkx as nx
import dovier_fba.rank as rank
import rank_test_cases as test_cases

@pytest.mark.parametrize("graph", test_cases.graphs)
def test_prepare_scc(graph):
    graph_scc = rank.prepare_scc(graph)
    scc_map = rank.build_map_to_scc(graph_scc, graph)

    for scc in graph_scc.nodes:
        if len(scc) == 1:
            for node in scc:
                assert graph.nodes[node]['wf'] == graph_scc.nodes[scc]['wf']
                if len(graph.adj[node]) == 0:
                    assert graph_scc.nodes[scc]['G-leaf']
        else:
            assert not graph_scc.nodes[scc]['wf']

def test_map_to_scc():
    components = [frozenset([0, 1, 2]), frozenset([3, 4]), frozenset([5])]

    graph_scc = nx.DiGraph()
    graph_scc.add_nodes_from(components)

    graph = nx.DiGraph()
    graph.add_nodes_from(range(6))

    scc_map = rank.build_map_to_scc(graph_scc, graph)

    assert scc_map[0] == components[0]
    assert scc_map[1] == components[0]
    assert scc_map[2] == components[0]
    assert scc_map[3] == components[1]
    assert scc_map[4] == components[1]
    assert scc_map[5] == components[2]

@pytest.mark.parametrize("graph, node_rank_dict", test_cases.graphs_noderankdict)
def test_compute_rank(graph, node_rank_dict: dict):
    rank.compute_rank(graph)

    for node in graph.nodes:
        assert graph.nodes[node]['rank'] == node_rank_dict[node]
