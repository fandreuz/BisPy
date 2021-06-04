import pytest
import networkx as nx
from bispy.utilities.graph_entities import _Vertex, _QBlock

def test_fast_mitosis():
    vxs = list(map(_Vertex, range(10)))
    qb = _QBlock(vxs, None)
    qb2 = qb.fast_mitosis(vxs[2:4])

    for v in qb.vertexes:
        assert v.label != 2 and v.label != 3
    assert qb.vertexes.size == 8

    for v in qb2.vertexes:
        assert v.label == 2 or v.label == 3
    assert qb2.vertexes.size == 2
