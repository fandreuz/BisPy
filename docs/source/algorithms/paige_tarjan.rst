.. _PaigeTarjan:

Paige-Tarjan
^^^^^^^^^^^^

.. module:: bispy.paige_tarjan.paige_tarjan

To implement the algorithm we followed the pseudocode and the analysis provided
in the following paper::

    Paige, Robert, and Robert E. Tarjan.
    "Three partition refinement algorithms."
    SIAM Journal on Computing 16.6 (1987): 973-989.

*Paige-Tarjan*'s algorithm provides the first efficient algorithmic solution
to the problem of the maximum bisimulation.

Summary
"""""""

.. autosummary::
    :nosignatures:

    paige_tarjan
    paige_tarjan_qblocks
    extract_splitter
    build_block_counterimage
    build_exclusive_B_counterimage
    split
    update_counts
    refine

Code documentation
""""""""""""""""""

.. autofunction:: paige_tarjan
.. autofunction:: paige_tarjan_qblocks
.. autofunction:: extract_splitter
.. autofunction:: build_block_counterimage
.. autofunction:: build_exclusive_B_counterimage
.. autofunction:: split
.. autofunction:: update_counts
.. autofunction:: refine
