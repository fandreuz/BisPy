===================
Graph normalization
===================

An *integral* graph is a graph :math:`G = (V,E)` such that
:math:`V \subseteq \mathbb{N}`, :math:`\min(V) = 0`, :math:`\max(V) = |V| - 1`,
namely its nodes are integers starting from 0 and do not have holes.

*BisPy* is able to work **only** with *integral* graphs, this is why we provide
this class to go back and forth between the actual graph and an isomorphic
representation.

.. module:: bispy.utilities.graph_normalization

.. autofunction:: convert_to_integer_graph
.. autofunction:: check_normal_integer_graph
.. autofunction:: back_to_original
