import bisimulation_algorithms.dovier_piazza_policriti.graph_entities as entities
import networkx as nx

block_counterimage_cases = []
block_counterimage_expected = []

# 1
vertexes1 = [entities._Vertex(label=i, rank=0) for i in range(5)]
for i in range(3, 5):
    vertexes1[0].append_to_counterimage(vertexes1[i])
vertexes1[1].append_to_counterimage(vertexes1[2])
block_counterimage_cases.append(entities._Block(0, [vertexes1[0], vertexes1[1]]))
block_counterimage_expected.append(vertexes1[2:5])

# 2
vertexes2 = [entities._Vertex(label=i, rank=0) for i in range(5)]
vertexes2[1].append_to_counterimage(vertexes2[2])
block_counterimage_cases.append(entities._Block(0, [vertexes2[0], vertexes2[1]]))
block_counterimage_expected.append([vertexes2[2]])

# ------------------------------------------------------

prepare_graph_cases = []
prepare_graph_expected = []

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(5))
graph1.add_edges_from([(i, i + 1) for i in range(4)])
prepare_graph_cases.append(graph1)
expected1 = [entities._Vertex(label=i, rank=4 - i) for i in range(5)]
for i in range(4):
    expected1[i].append_to_image(expected1[i + 1])
prepare_graph_expected.append(expected1)
