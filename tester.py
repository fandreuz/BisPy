import networkx as nx
import matplotlib.pyplot as plt
import randomcolor
import rank
import fba
from networkx.drawing.nx_agraph import to_agraph

MATERIAL_COLORS = ['#26A69A', '#9FA8DA', '#80DEEA', '#FDD835', '#FF8A65', '#A1887F']

def draw(graph, file_name):
    for node in graph.nodes:
        graph.nodes[node]['height'] = 0.1
        graph.nodes[node]['shape'] = 'circle'

        graph.nodes[node]['width'] = 0.3
        graph.nodes[node]['height'] = 0.3
        graph.nodes[node]['fixedsize'] = True
        graph.nodes[node]['fontsize'] = 6

    for edge in graph.edges:
        graph.edges[edge]['arrowsize'] = 0.2

    A = to_agraph(graph)
    A.layout('sfdp')
    A.graph_attr['nodesep'] = 1
    A.graph_attr['dpi'] = 300
    A.graph_attr['height'] = 500
    A.draw('{}.png'.format(file_name))

def test_wf(graph):
    rank.well_founded_nodes(graph)

    for node in graph.nodes:
        if not graph.nodes[node]['wf']:
            graph.nodes[node]['fillcolor'] = 'red'
            graph.nodes[node]['style'] = 'filled'

    draw(graph, 'wf')

def test_rank(graph):
    rank.compute_rank(graph)

    graph_scc = rank.prepare_scc(graph)
    scc_map = rank.build_map_to_scc(graph_scc, graph)

    if len(MATERIAL_COLORS) < len(graph_scc.nodes):
        random_color = randomcolor.RandomColor()
        for i in range(len(graph_scc.nodes) - len(MATERIAL_COLORS)):
            MATERIAL_COLORS.append(random_color.generate()[0])

    scc_color_map = {scc: MATERIAL_COLORS[index] for index,scc in enumerate(graph_scc.nodes)}

    for node in graph.nodes:
        graph.nodes[node]['fillcolor'] = scc_color_map[scc_map[node]]
        graph.nodes[node]['style'] = 'filled'

        graph.nodes[node]['label'] = '{}({})'.format(node, graph.nodes[node]['rank'])

    draw(graph, 'rank')

def test_collapse(graph):
    draw(graph, 'no-collapse')
    fba.collapse(graph, [0,1,2,3])
    draw(graph, 'collapsed')

graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
test_collapse(graph)

graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
test_wf(graph)

graph = nx.erdos_renyi_graph(10, 0.15, directed=True)
test_rank(graph)
