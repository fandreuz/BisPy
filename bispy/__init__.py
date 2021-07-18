from .paige_tarjan.paige_tarjan import (
    paige_tarjan,
    paige_tarjan_qblocks,
)
from .dovier_piazza_policriti.dovier_piazza_policriti import (
    dovier_piazza_policriti,
    dovier_piazza_policriti_partition,
)
from .saha.saha_partition import saha

from .utilities.graph_decorator import (
    decorate_bispy_graph,
    decorate_nx_graph,
    to_tuple_list,
)


class Algorithms(Enum):
    PaigeTarjan = auto()
    DovierPiazzaPolicriti = auto()


def compute_maximum_bisimulation(
    graph: nx.DiGraph,
    initial_partition,
    algorithm=Algorithm.PaigeTarjan,
):
    """Compute the maximum bisimulation of the given graph, possibly using
    an initial partition (or labeling set). The preferred algorithm may be
    chosen as well (*Paige-Tarjan* or *Dovier-Piazza-Policriti*).

    Example:
        >>> import networkx as nx
        >>> from bispy import compute_maximum_bisimulation, Algorithms
        >>> graph = nx.balanced_tree(2,3, create_using=nx.DiGraph)
        >>> compute_maximum_bisimulation(graph)
        [(3, 4, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (1, 2), (0,)]
        >>> compute_maximum_bisimulation(graph),
            algorithm=Algorithms.DovierPiazzaPolicriti)
        [(3, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,), (4,)]

    :param graph: The input graph.
    :param initial_partition: A partition of the set of nodes of the graph,
        two nodes in different blocks of this partition cannot be bisimilar.
        Defaults to the trivial initial partition.
    :param algorithm: The algorithm used to compute the maximum bisimulation.
    :returns: The maximum bisimulation of the given graph, with the given
        initial partition.
    """

    if algorithm == Algorithms.PaigeTarjan:
        return paige_tarjan(graph, initial_partition)
    elif algorithm == Algorithms.DovierPiazzaPolicriti:
        return dovier_piazza_policriti(graph, initial_partition)
