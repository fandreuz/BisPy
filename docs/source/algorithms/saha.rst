Saha
^^^^

.. module:: bispy.saha.saha

To implement the algorithm we followed the pseudocode and the analysis provided
in the following paper::

    Saha, Diptikalyan.
    "An incremental bisimulation algorithm."
    International Conference on Foundations of Software Technology
        and Theoretical Computer Science.
    Springer, Berlin, Heidelberg, 2007.

Using *Saha*'s incremental algorithm we can update the RSCP/maximum
bisimulation after the addition of a new edge. While we may do the same thing
computing the maximum bisimulation from scratch after the modification,
*Saha*'s algorithm may be able to take less time on average.

However, the complexity of *Saha*'s algorithm is highly dependent on how much
the maximum bisimulation changes as a consequence of the addition of the new
edge:

.. math::

    \begin{align*}
        T_{\text{Saha}} = O(|E_1|\log|V_1|) &+ O(|\Delta_\texttt{wf}\log|\Delta_\texttt{wf}|) + O(|E_\texttt{nwf}| + |V_\texttt{nwf}|)\\
        &+ O(|E_2||V_2|) + O(|E_2|\log|V_2|)
    \end{align*}

Therefore without an additional hypothesis on the nature of the edges added
we may encounter some cases for which the incremental algorithm takes much
more than re-computing the maximum bisimulation from scratch using
:ref:`PaigeTarjan` or :ref:`DovierPiazzaPolicriti`'s algorithm.

Summary
"""""""

.. autosummary::
    :nosignatures:

    saha
    add_edge
    is_in_image
    check_new_scc
    both_blocks_go_or_dont_go_to_block
    exists_causal_splitter
    merge_condition
    recursive_merge
    merge_phase
    preprocess_initial_partition
    merge_split_phase
    propagate_nwf
    propagate_wf
    build_well_founded_topological_list
    filter_deteached



Code documentation
""""""""""""""""""

.. autofunction:: saha
.. autofunction:: add_edge
.. autofunction:: is_in_image
.. autofunction:: check_new_scc
.. autofunction:: both_blocks_go_or_dont_go_to_block
.. autofunction:: exists_causal_splitter
.. autofunction:: merge_condition
.. autofunction:: recursive_merge
.. autofunction:: merge_phase
.. autofunction:: preprocess_initial_partition
.. autofunction:: merge_split_phase
.. autofunction:: propagate_nwf
.. autofunction:: propagate_wf
.. autofunction:: build_well_founded_topological_list
.. autofunction:: filter_deteached
