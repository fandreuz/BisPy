---
title: "BisPy: Bisimulation in Python"
tags:
  - Bisimulation
  - Graph theory
  - Graph algorithms
authors:
  - name: Francesco Andreuzzi
    orcid: 0000-0002-9508-7801
    affiliation: "1,2"
affiliations:
  - name: Internation School of Advanced Studies, SISSA, Trieste, Italy
    index: 1
  - name: Università degli Studi di Trieste
    index: 2
date: 11 July 2021
bibliography: paper.bib
---

# Summary

The notion of _bisimulation_ in directed graphs, and in particular of _maximum
bisimulation_, has applications in modal logic, formal verification and
concurrency theory [@kanellakis], and is used for graph reduction as well
[@gentilini]. The fact that _graphs_ may be used to create digital models of a
wide span of complex systems makes bisimulation a useful tool in many different
cases. For this reason several algorithms for the computation of maximum
bisimulation have been studied throughout the years, and it is now widely known
that the problem has an $O(|E| \log |V|)$ algorithmic solution, where $V$ is
the set of nodes in the graph, and $E$ is the set of edges of the graph.

The first procedure to match this time complexity was _Paige-Tarjan_'s
algorithm [-@paigetarjan], whose authors obtained an efficient solution
employing an insight from the famous algorithm for the minimization of finite
states automata [@hopcroft]. Even though the problem was formally solved,
several decades later a new algorithm was presented [@dovier].
_Dovier-Piazza-Policriti_'s algorithm uses extensively the notion of _rank_,
which can be defined in an informal way as the distance of a node from the
_leafs_ (or _sinks_) of the graph, and may be computed — prior the execution of
the algorithm — using an $O(|V|+|E|)$ procedure [@sharir; @tarjan]. The authors
claimed that their new method outperformed _Paige-Tarjan_'s algorithm in
several cases, even though the time complexity remains the same. Finally we
considered an _incremental_ algorithm, namely a method which updates the
maximum bisimulation after a modification on the graph (in our case, the
addition of a new edge). Its time complexity is substantially different than
that of from-scratch algorithms, since it depends on how much the maximum
bisimulation changes as a consequence of the modification [@saha]. We found
also other algorithms to compute the maximum bisimulation, but for what we
could see they were slightly variations of the classical ones, or tailored on
particular cases.

$\texttt{BisPy}$ is a Python package for the computation of maximum
bisimulation. It contains the implementation of the algorithms mentioned in the
previous paragraph, each of which have been tested and documented. It is
interesting to note that the three methods included in the package use a
substantially different strategy to reach the result, therefore the performance
of different methods may be compared easily on practical applications.

The algorithms have been splitted in several functions rather than being
implemented in a monolithic block of code, in order to improve readability and
testability. Moreover, this kind of modularity allowed us to reuse functions in
multiple algorithms, since several procedures are shared (e.g.,
$\texttt{split}$, or the computation of rank), and for the same reason we think
that the addition of new functionalities would be straightforward since we
already have a solid set of common functions implemented.

# Statement of need

To the best of our knowledge, there is not another project which addresses
bisimulation and fulfills the needs of a serious open source project. We found
some sparse implementations of _Paige-Tarjan_'s algorithm, but the source code
lacked documentation and test cases. We think that our project may be a useful
tool to study practical cases for people who are approaching the field — since
the notion of bisimulation may be somewhat counterintuitive at first glance —
as well as to established researchers in the field, who may use
$\texttt{BisPy}$ to study improvements on particular types of graphs, and to
compare new algorithms with the state of the art.

# Acknowledgements

We acknowledge the support received from Alberto Casagrande during the
preliminar theoretical study of the topic, as well as SISSA mathLab for
providing the hardware to perform experiments on large graphs.

# References
