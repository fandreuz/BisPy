import networkx as nx
from bisimulation_algorithms.paige_tarjan.graph_decorator import initialize

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
g0 = nx.DiGraph()
g0.add_nodes_from(range(3))
g0.add_edges_from([(1, 0),(0,1)])
new_scc_graphs.append(g0)

new_scc_new_edge.append((1,2))
new_scc_correct_value.append(False)
new_scc_finishing_time.append([0,1])


# exists causal splitter
exists_causal_splitter_qblocks = []
exists_causal_splitter_result_map = []

# 0
g0 = nx.DiGraph()
g0.add_nodes_from(range(6))
g0.add_edges_from([(5,0),(5,5),(6,5), (0,3), (1,3), (2,4), (3,3), (4,3)])

qblocks0, _ = initialize(g0, [(0,1,2),(3,4),(5,),(6,)])
exists_causal_splitter_qblocks.append(qblocks0)
# integer tuples are the indexes of the blocks in qblocks0
result0 = [((2,3), True), ((0,1), False), ((1,2), True)]
exists_causal_splitter_result_map.append(result0)

# both blocks go to block
both_blocks_goto_result_map = []

# 0
both_blocks_goto_result_map.append([((0,1,0), True), ((0,1,1), True), ((0,1,2), True), ((0,1,3), True), ((0,2,0), False), ((0,2,1), False), ((0,2,2), False), ((0,2,3), True), ((0,3,0), True), ((0,3,1), False), ((0,3,2), False), ((1,2,0), False), ((1,2,1), False), ((1,2,2), False), ((1,2,3), True), ((1,3,0), True), ((1,3,1), False), ((1,3,2), False), ((1,3,3), True), ((2,3,0), False), ((2,3,1), True), ((2,3,2), True), ((2,3,3), True)])
