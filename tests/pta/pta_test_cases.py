import networkx as nx

initial_partitions = [
    [],
    [[0]],
    [[0], [1]],
    [[0], [1, 2]],
    [[0, 3], [1, 2]],
    [[0, 3, 4], [1, 2]],
    [[0, 3, 4], [1, 2], [5]],
    [[0, 3, 4], [1, 2], [5], [6]],
    [
        [0, 3, 4],
        [1, 2],
        [5],
        [6],
        [7],
    ],
    [
        [0, 3, 4],
        [1, 2],
        [5, 8],
        [6],
        [7],
    ],
    [
        [0, 3, 4],
        [1, 2, 9],
        [5, 8],
        [6],
        [7],
    ],
]


graph_partition_tuples = []

# 1
graph1 = nx.DiGraph()
graph1.add_nodes_from(range(10))
graph1.add_edges_from(
    [
        (0, 6),
        (1, 2),
        (1, 4),
        (2, 7),
        (3, 7),
        (4, 2),
        (5, 2),
        (5, 8),
        (6, 1),
        (6, 4),
        (6, 8),
        (8, 1),
        (9, 2),
        (9, 4),
    ]
)
graph_partition_tuples.append((graph1, initial_partitions[len(graph1.nodes)]))

# 2
graph2 = nx.DiGraph()
graph2.add_nodes_from(range(10))
graph2.add_edges_from(
    [
        (0, 1),
        (0, 7),
        (0, 8),
        (3, 2),
        (4, 2),
        (4, 6),
        (7, 1),
        (7, 2),
        (8, 0),
        (8, 1),
        (8, 9),
        (9, 6),
    ]
)
graph_partition_tuples.append((graph2, initial_partitions[len(graph2.nodes)]))

# 3
graph3 = nx.DiGraph()
graph3.add_nodes_from(range(10))
graph3.add_edges_from(
    [
        (0, 2),
        (0, 3),
        (0, 5),
        (1, 3),
        (1, 4),
        (2, 6),
        (2, 9),
        (4, 9),
        (5, 8),
        (6, 7),
        (7, 9),
        (8, 3),
    ]
)
graph_partition_tuples.append((graph3, initial_partitions[len(graph3.nodes)]))

# 4
graph4 = nx.DiGraph()
graph4.add_nodes_from(range(10))
graph4.add_edges_from(
    [
        (0, 6),
        (1, 0),
        (1, 2),
        (1, 4),
        (2, 0),
        (2, 3),
        (3, 1),
        (4, 1),
        (4, 5),
        (6, 2),
        (9, 4),
        (9, 6),
    ]
)
graph_partition_tuples.append((graph4, initial_partitions[len(graph4.nodes)]))

# 5
graph5 = nx.DiGraph()
graph5.add_nodes_from(range(5))
graph5.add_edges_from(
    [(0, 2), (2, 0), (2, 3), (2, 4), (3, 0), (3, 1), (4, 0), (4, 2), (4, 3)]
)
graph_partition_tuples.append((graph5, initial_partitions[len(graph5.nodes)]))

# 6
graph6 = nx.DiGraph()
graph6.add_nodes_from(range(5))
graph6.add_edges_from(
    [(0, 3), (1, 3), (2, 1), (2, 3), (3, 0), (3, 4), (4, 0), (4, 2), (4, 3)]
)
graph_partition_tuples.append((graph6, initial_partitions[len(graph6.nodes)]))

# 7
graph7 = nx.DiGraph()
graph7.add_nodes_from(range(5))
graph7.add_edges_from(
    [(0, 1), (0, 2), (0, 3), (1, 2), (2, 4), (3, 0), (3, 2), (4, 1), (4, 3)]
)
graph_partition_tuples.append((graph7, initial_partitions[len(graph7.nodes)]))

# 8
graph8 = nx.DiGraph()
graph8.add_nodes_from(range(5))
graph8.add_edges_from(
    [
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 0),
        (2, 1),
        (2, 3),
        (3, 2),
        (4, 0),
        (4, 1),
        (4, 2),
        (4, 3),
    ]
)
graph_partition_tuples.append((graph8, initial_partitions[len(graph8.nodes)]))

# 9
graph9 = nx.DiGraph()
graph9.add_nodes_from(range(3))
graph9.add_edges_from([(0, 1), (0, 2), (1, 0), (2, 0), (2, 1)])
graph_partition_tuples.append((graph9, initial_partitions[len(graph9.nodes)]))

# 10
graph10 = nx.DiGraph()
graph10.add_nodes_from(range(3))
graph10.add_edges_from([(0, 1), (0, 2), (1, 0), (1, 2)])
graph_partition_tuples.append((graph10, initial_partitions[len(graph10.nodes)]))

# 11
graph11 = nx.DiGraph()
graph11.add_nodes_from(range(3))
graph11.add_edges_from([(0, 1), (1, 2), (2, 0), (2, 1)])
graph_partition_tuples.append((graph11, initial_partitions[len(graph11.nodes)]))

# 12
graph12 = nx.DiGraph()
graph12.add_nodes_from(range(3))
graph12.add_edges_from([(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])
graph_partition_tuples.append((graph12, initial_partitions[len(graph12.nodes)]))

graph_partition_rscp_tuples = []


# 1
graph = nx.DiGraph()
graph.add_nodes_from(range(6))
graph.add_edges_from([(0, 2), (0, 3), (1, 2), (2, 4), (3, 4)])
graph_partition_rscp_tuples.append(
    (graph, [(2, 4), (0, 1, 3, 5)], set([(0,), (1,), (2,), (3,), (4,), (5,)]))
)

# 2
graph = nx.DiGraph()
graph.add_nodes_from(range(8))
graph.add_edges_from(
    [
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 7),
        (1, 2),
        (1, 7),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (2, 7),
        (3, 4),
        (3, 5),
        (4, 7),
        (5, 6),
        (6, 7),
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(1,), (2,), (3,), (4,), (0, 5, 6, 7)],
        set([(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,)]),
    )
)

# 3
graph = nx.DiGraph()
graph.add_nodes_from(range(6))
graph.add_edges_from(
    [
        (0, 2),
        (0, 3),
        (0, 5),
        (1, 2),
        (1, 4),
        (1, 5),
        (2, 4),
        (2, 5),
        (3, 5),
        (4, 5),
    ]
)
graph_partition_rscp_tuples.append(
    (graph, [(2,), (3,), (1, 4), (0, 5)], set([(0,), (1,), (2,), (3,), (4,), (5,)]))
)

# 4
graph = nx.DiGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from(
    [
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 6),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5),
        (3, 6),
        (4, 5),
        (4, 6),
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(3,), (4,), (5,), (0, 1, 2, 6)],
        set([(0,), (1,), (2,), (3,), (4,), (5,), (6,)]),
    )
)

# 5
graph = nx.DiGraph()
graph.add_nodes_from(range(9))
graph.add_edges_from(
    [
        (0, 1),
        (0, 4),
        (0, 5),
        (0, 8),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 6),
        (2, 8),
        (3, 4),
        (3, 7),
        (3, 8),
        (4, 5),
        (4, 6),
        (4, 7),
        (5, 6),
        (5, 7),
        (5, 8),
        (6, 7),
        (6, 8),
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,), (2, 5, 7), (1, 3, 4, 6, 8)],
        set([(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,)]),
    )
)

# 6
graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from([(0, 2), (0, 3), (0, 4), (1, 3), (2, 3), (2, 4), (3, 4)])
graph_partition_rscp_tuples.append(
    (graph, [(1,), (3,), (0, 2, 4)], set([(0,), (1,), (2,), (3,), (4,)]))
)

# 7
graph = nx.DiGraph()
graph.add_nodes_from(range(6))
graph.add_edges_from(
    [
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (1, 2),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5),
        (4, 5),
    ]
)
graph_partition_rscp_tuples.append(
    (graph, [(0, 2, 4), (1, 3, 5)], set([(0,), (1,), (2,), (3,), (4,), (5,)]))
)

# 8
graph = nx.DiGraph()
graph.add_nodes_from(range(9))
graph.add_edges_from([(0, 4), (0, 7), (5, 7), (6, 8)])
graph_partition_rscp_tuples.append(
    (
        graph,
        [(2,), (3,), (0, 4), (5,), (1, 7), (6, 8)],
        set([(0,), (1, 7), (2,), (3,), (4,), (5,), (6,), (8,)]),
    )
)

# 9
graph = nx.DiGraph()
graph.add_nodes_from(range(8))
graph.add_edges_from(
    [
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 6),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 7),
        (3, 4),
        (3, 6),
        (3, 7),
        (4, 6),
        (4, 7),
        (5, 6),
        (5, 7),
        (6, 7),
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(4,), (1, 2, 5), (6,), (0, 3, 7)],
        set([(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,)]),
    )
)

# 10
graph = nx.DiGraph()
graph.add_nodes_from(range(8))
graph.add_edges_from(
    [
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 6),
        (0, 7),
        (1, 2),
        (1, 3),
        (1, 5),
        (1, 7),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (3, 4),
        (3, 5),
        (4, 7),
        (5, 6),
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(1,), (2,), (3, 5), (0, 4, 6), (7,)],
        set([(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,)]),
    )
)

# 11
graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from(
    [
        (0,1),(1,2),(2,3),(3,4),(4,0)
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(4,),(0,1,2,3)],
        set([(0,), (1,), (2,), (3,), (4,)]),
    )
)

# 12
graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from(
    [
        (0,1),(1,2),(2,3),(3,0),(0,4)
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,1,2,3,4)],
        set([(0,), (1,), (2,), (3,), (4,)]),
    )
)

# 13
graph = nx.DiGraph()
graph.add_nodes_from(range(4))
graph.add_edges_from(
    [
        (3,0), (0,1), (1,2),
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,), (1,2,3)],
        set([(0,), (1,), (2,), (3,),]),
    )
)

# 14
graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from(
    [
        (0,1), (1,2), (2,3), (3,4), (4,0)
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,1,2,3,4)],
        set([(0,1,2,3,4)]),
    )
)

# 15
graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from(
    [
        (0,1), (1,2), (2,3), (3,4), (4,0), (2,4)
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,1,2,3,4)],
        set([(0,1,2,3,4)]),
    )
)

# 16
graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from(
    [
        (0,1), (1,3), (3,4), (4,3), (0,4), (2,4)
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,1,2), (3,4)],
        set([(3,4), (1,2), (0,)]),
    )
)

# 17
graph = nx.DiGraph()
graph.add_nodes_from(range(7))
graph.add_edges_from(
    [
        (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 1), (1, 2), (1, 3), (1, 3),
        (1, 4), (1, 5), (1, 6), (4, 2), (4, 3), (5, 2), (5, 3),
        (5, 4), (5, 0), (6, 3), (6, 4), (6, 5)
    ]
)
graph_partition_rscp_tuples.append(
    (
        graph,
        [(0,1,2,6), (3,), (4,), (5,)],
        set([tuple([i]) for i in range(7)]),
    )
)

def build_full_graphs(num_of_nodes):
        graph = nx.DiGraph()
        for i in range(num_of_nodes):
            j = i
            p = 0
            while j>0:
                if j%2==1:
                    graph.add_edge(i,p)
                    j -= 1
                else:
                    p += 1
                    j /= 2
        return graph
