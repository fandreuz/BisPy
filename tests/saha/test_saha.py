import pytest
import networkx as nx
from bisimulation_algorithms.dovier_piazza_policriti.graph_decorator import (
    prepare_graph,
)
from bisimulation_algorithms.dovier_piazza_policriti.fba import (
    create_initial_partition,
)


def test_check_old_blocks_relation():
    graph = nx.DiGraph()
    graph.add_nodes_from(range(5))
    graph.add_nodes_from([(0,1), (1,2), (2,3), (4,1)])
