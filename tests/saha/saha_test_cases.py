import networkx as nx
from bispy.utilities.graph_decorator import decorate_bispy_graph, decorate_nx_graph

# new scc
new_scc_graphs = []
new_scc_new_edge = []
new_scc_correct_value = []
new_scc_finishing_time = []

# 0
g0 = nx.DiGraph()
g0.add_nodes_from(range(5))
g0.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
new_scc_graphs.append(g0)

new_scc_new_edge.append((2,0))
new_scc_correct_value.append(True)
new_scc_finishing_time.append([0,1,2])

# 1
g1 = nx.DiGraph()
g1.add_nodes_from(range(8))
g1.add_edges_from([(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
new_scc_graphs.append(g1)

new_scc_new_edge.append((3, 4))
new_scc_correct_value.append(False)
new_scc_finishing_time.append([0,1,2,3])

# 2
g2 = nx.DiGraph()
g2.add_nodes_from(range(5))
g2.add_edges_from([(0, 1), (1, 2), (2, 3), (3,4)])
new_scc_graphs.append(g2)

new_scc_new_edge.append((0, 4))
new_scc_correct_value.append(False)
new_scc_finishing_time.append([0])

# 3
g3 = nx.DiGraph()
g3.add_nodes_from(range(3))
g3.add_edges_from([(1, 0),(0,1)])
new_scc_graphs.append(g3)

new_scc_new_edge.append((1,2))
new_scc_correct_value.append(False)
new_scc_finishing_time.append([0,1])

# 4
g4 = nx.DiGraph()
g4.add_nodes_from(range(6))
g4.add_edges_from([(1,2), (0,2), (0,3), (2,4), (3,4)])
new_scc_graphs.append(g4)

new_scc_new_edge.append((4,2))
new_scc_correct_value.append(True)
new_scc_finishing_time.append(None)

# 5
g5 = nx.DiGraph()
g5.add_nodes_from(range(5))
g5.add_edges_from([(0,1), (1,2), (2,3), (3,0), (0,4)])
new_scc_graphs.append(g5)

new_scc_new_edge.append(((4,0)))
new_scc_correct_value.append(True)
new_scc_finishing_time.append(None)


# exists causal splitter
exists_causal_splitter_qblocks = []
exists_causal_splitter_result_map = []

# 0
g0 = nx.DiGraph()
g0.add_nodes_from(range(6))
g0.add_edges_from([(5,0),(5,5),(6,5), (0,3), (1,3), (2,4), (3,3), (4,3)])
ip0 = [(0, 1, 2), (3, 4), (5,), (6,)]

vertexes0, qblocks0 = decorate_nx_graph(g0, ip0)
decorate_bispy_graph(vertexes0, ip0)
exists_causal_splitter_qblocks.append(qblocks0)
# integer tuples are the indexes of the blocks in qblocks0
result0 = [((2,3), True), ((0,1), True), ((1,2), False)]
exists_causal_splitter_result_map.append(result0)

# both blocks go to block
both_blocks_goto_result_map = []

# 0
both_blocks_goto_result_map.append([((0,1,0), True), ((0,1,1), True), ((0,1,2), True), ((0,1,3), True), ((0,2,0), False), ((0,2,1), False), ((0,2,2), False), ((0,2,3), True), ((0,3,0), True), ((0,3,1), False), ((0,3,2), False), ((1,2,0), False), ((1,2,1), False), ((1,2,2), False), ((1,2,3), True), ((1,3,0), True), ((1,3,1), False), ((1,3,2), False), ((1,3,3), True), ((2,3,0), False), ((2,3,1), True), ((2,3,2), True), ((2,3,3), True)])


# update rscp
update_rscp_graphs = []
update_rscp_new_edge = []
update_rscp_initial_partition = []

# 0
g0 = nx.DiGraph()
g0.add_nodes_from(range(6))
g0.add_edges_from([(1, 0), (2, 1), (3, 2), (3, 0), (1, 4), (1, 5)])
update_rscp_graphs.append(g0)
update_rscp_initial_partition.append([(0,), (1, 3, 5), (2, 4)])
update_rscp_new_edge.append((4,3))

# 1
g1 = nx.DiGraph()
g1.add_nodes_from(range(8))
g1.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 7), (1, 2),
    (1, 7), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (4, 7),
    (5, 6)
])
update_rscp_graphs.append(g1)
update_rscp_initial_partition.append([(1,), (2,), (3,), (4,), (0, 5, 6, 7)])
update_rscp_new_edge.append((6,7))

# 2
g2 = nx.DiGraph()
g2.add_nodes_from(range(6))
g2.add_edges_from([(2,0), (3,1), (4,3), (5,3), (5,4)])
update_rscp_graphs.append(g2)
update_rscp_initial_partition.append([(0,1,2,3,4,5)])
update_rscp_new_edge.append((0,1))
