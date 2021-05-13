from bispy.utilities.graph_entities import (
    _Vertex,
    _Edge,
    _SCC,
)
from typing import List, Dict, Set


def kosaraju(
    base,
    return_sccs=False,
    return_finishing_time_list=False,
):
    finishing_time_list = []
    available_labels = {}

    if isinstance(base, _Vertex):
        vertexes = []
        predecessors(base, vertexes)

        # unvisit
        for node in vertexes:
            node.visited = False

        based_sccs = True
    else:
        vertexes = base
        based_sccs = False

    # visit G
    for node in vertexes:
        if not node.visited:
            visit(node, finishing_time_list, available_labels, based_sccs)

    # unvisit
    for node in vertexes:
        node.visited = False

    scc_instances = []
    available_labels = list(available_labels.keys())

    # visit G^{-1}
    for i in range(len(finishing_time_list) - 1, -1, -1):
        if finishing_time_list[i].scc is None:
            if len(available_labels) > 0:
                label = available_labels.pop()
            else:
                label = len(scc_instances)

            scc_instance = _SCC(label=label)
            scc_instances.append(scc_instance)

            assign_scc(finishing_time_list[i], scc_instance, based_sccs)

    for node in vertexes:
        if based_sccs:
            del node.reachable_from_base

    if return_finishing_time_list and return_sccs:
        return scc_instances, finishing_time_list
    elif return_finishing_time_list:
        return finishing_time_list
    elif return_sccs:
        return scc_instances


def assign_scc(node: _Vertex, scc_instance: _SCC, based_scc_tree: bool):
    scc_instance.add_vertex(node)

    for edge in node.counterimage:
        source = edge.source
        if edge.source.scc is None and (
            not based_scc_tree
            or (
                hasattr(source, "reachable_from_base")
                and source.reachable_from_base
            )
        ):
            assign_scc(edge.source, scc_instance, based_scc_tree)

    return scc_instance


def predecessors(node: _Vertex, reachable_vertexes: List[_Vertex]):
    node.visited = True
    node.reachable_from_base = True
    reachable_vertexes.append(node)

    for edge in node.counterimage:
        if not edge.source.visited:
            predecessors(edge.source, reachable_vertexes)


def visit(
    node: _Vertex,
    finishing_time_list: List[_Vertex],
    available_labels: Dict[int, bool],
    based_scc_tree: bool,
):
    node.visited = True
    if node.scc is not None:
        # we want to destroy this SCC, but we want to know which labels we can
        # use now
        available_labels[node.scc.label] = True
        # clear SCC
        node.scc = None

    for edge in node.image:
        dest = edge.destination
        if not dest.visited and (
            not based_scc_tree
            or (
                hasattr(dest, "reachable_from_base")
                and dest.reachable_from_base
            )
        ):
            visit(
                edge.destination,
                finishing_time_list,
                available_labels,
                based_scc_tree,
            )
    finishing_time_list.append(node)
