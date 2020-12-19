from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import _Block, _Vertex
import bisimulation_algorithms.dovier_piazza_policriti.fba as fba
import networkx as nx

block_counterimage_cases = []
block_counterimage_expected = []

# 1
vertexes1 = [_Vertex(label=i, rank=0) for i in range(5)]
for i in range(3, 5):
    vertexes1[0].append_to_counterimage(vertexes1[i])
vertexes1[1].append_to_counterimage(vertexes1[2])
block_counterimage_cases.append(_Block(0, [vertexes1[0], vertexes1[1]]))
block_counterimage_expected.append(vertexes1[2:5])

# 2
vertexes2 = [_Vertex(label=i, rank=0) for i in range(5)]
vertexes2[1].append_to_counterimage(vertexes2[2])
block_counterimage_cases.append(_Block(0, [vertexes2[0], vertexes2[1]]))
block_counterimage_expected.append([vertexes2[2]])

# ------------------------------------------------------

prepare_graph_cases = []
prepare_graph_expected = []

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(5))
graph1.add_edges_from([(i, i + 1) for i in range(4)])
prepare_graph_cases.append(graph1)
expected1 = [_Vertex(label=i, rank=4 - i) for i in range(5)]
for i in range(4):
    expected1[i].append_to_image(expected1[i + 1])
prepare_graph_expected.append(expected1)

# ------------------------------------------------------

create_subgraph_cases = []
create_subgraph_cases_rank = []
create_subgraph_expected = []

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(5))
graph1.add_edges_from((i, i + 1) for i in range(3))
graph1.add_edge(3, 0)
graph1.add_edge(4,0)

create_subgraph_cases_rank.append(float('-inf'))
create_subgraph_expected.append(graph1)
create_subgraph_cases.append(fba.create_initial_partition(fba.prepare_graph(graph1))[0])

# 2
graph2 = nx.DiGraph()
graph2.add_nodes_from(range(3))
graph2.add_edges_from([(0, 1), (0, 2)])

graph2e = nx.DiGraph()
graph2e.add_nodes_from([1,2])

create_subgraph_cases_rank.append(0)
create_subgraph_expected.append(graph2e)
create_subgraph_cases.append(fba.create_initial_partition(fba.prepare_graph(graph2))[1])
