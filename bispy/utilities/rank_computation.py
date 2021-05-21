from bispy.utilities.graph_entities import _Vertex, _SCC
from typing import List, Set, Dict
from .kosaraju import kosaraju


def visit_scc(node: _SCC, finishing_time_list: List[_SCC]):
    node.visited = True
    for dest in node.image:
        if not dest.visited:
            visit_scc(dest, finishing_time_list)
    finishing_time_list.append(node)


def scc_finishing_time_list(sccs: List[_SCC]):
    scc_finishing_time_list = []

    for scc in sccs:
        if not scc.visited:
            visit_scc(scc, scc_finishing_time_list)

    # clear visited
    for scc in sccs:
        scc.visited = False

    return scc_finishing_time_list


def compute_rank(vertexes, sccs=None):
    """
    Compute rank and well-foundedness of the nodes of the graph represented by
    `vertexes` (edges should be stored inside the attributes
    :attr:`~bispy.utilities.graph_entities._Vertex.image`,
    :attr:`~bispy.utilities.graph_entities._Vertex.counterimage`).

    Data can be found afterwards in
    :attr:`~bispy.utilities.graph_entities._Vertex.wf`,
    :attr:`~bispy.utilities.graph_entities._Vertex.rank`.

    :param vertexes: The representation of the graph, in *BisPy* format.
    :type vertexes: list(:class:`~bispy.utilities.graph_entities._Vertex`)
    :param sccs: Strongly connected components of the graph. If `None`, the
        Kosaraju algorithm will be used.
    :type sccs: list(:class:`~bispy.utilities.graph_entities._SCC`)
    """
    if sccs is None:
        sccs = kosaraju(vertexes, return_sccs=True)
    for scc in sccs:
        scc.compute_image()

    for scc in scc_finishing_time_list(sccs):
        # this is a SCC leaf
        if len(scc.image) == 0:
            # this is a leaf of G
            if scc.wf:
                scc.mark_leaf()
            else:
                scc.mark_scc_leaf()
        else:
            for image_scc in scc.image:
                if image_scc.wf:
                    if image_scc.rank + 1 > scc.rank:
                        scc._rank = image_scc.rank + 1
                else:
                    if image_scc.rank > scc.rank:
                        scc._rank = image_scc.rank

    for scc in sccs:
        for vx in scc._vertexes:
            vx.visited = False
