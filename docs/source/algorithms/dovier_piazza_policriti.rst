.. _DovierPiazzaPolicriti:

Dovier-Piazza-Policriti
^^^^^^^^^^^^^^^^^^^^^^^

.. module:: bispy.dovier_piazza_policriti.dovier_piazza_policriti

To implement the algorithm we followed the pseudocode and the analysis provided
in the following paper::

    Dovier, Agostino, Carla Piazza, and Alberto Policriti.
    "A fast bisimulation algorithm."
    International Conference on Computer Aided Verification.
    Springer, Berlin, Heidelberg, 2001.

The most significant improvement with respect to
:mod:`bispy.paige_tarjan.paige_tarjan` is due to the usage of the notion of
*rank*, motivated by the following observation:

.. math::

    a \equiv b \implies \texttt{rank}(a) = \texttt{rank}(b)

.. seealso:: :ref:`Rank definition`

Therefore we may be able to obtain the equivalence classes of the maximum
bisimulation in a smaller number of steps when the relation "same rank"
is a good approximation of the maximum bisimulation.

Summary
"""""""

.. autosummary::
    :nosignatures:

    rscp
    fba
    collapse
    build_block_counterimage
    split_upper_ranks

Code documentation
""""""""""""""""""

.. autofunction:: rscp
.. autofunction:: fba
.. autofunction:: collapse
.. autofunction:: build_block_counterimage
.. autofunction:: split_upper_ranks
