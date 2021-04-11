from bisimulation_algorithms.utilities.graph_entities import (
    _Vertex,
    _Edge
)
from typing import List, Dict, Set

def kosaraju(nwf_nodes: List[_Vertex]) -> Dict[int, Set]:
    finishing_time_list = []
    vertex_to_scc = {}

    # visit G
    for node in nwf_nodes:
        if not node.visited:
            visit(node, finishing_time_list)

    # visit G^{-1}
    for i in range(len(nwf_nodes) - 1, -1, -1):
        assign_scc(finishing_time_list[i], vertex_to_scc)

    return vertex_to_scc

def assign_scc(node: _Vertex, vertex_to_scc: Dict[int, Set], scc_set: set = None):
    if node.label in vertex_to_scc:
        return

    if scc_set is None:
        scc_set = set()

    scc_set.add(node)
    vertex_to_scc[node.label] = scc_set
    for edge in node.counterimage:
        assign_scc(edge.source, vertex_to_scc, scc_set)

def visit(node: _Vertex, finishing_time_list: List[_Vertex]):
    node.visited = True
    for edge in node.image:
        if not edge.destination.visited:
            visit(edge.destination, finishing_time_list)
    finishing_time_list.append(node)
