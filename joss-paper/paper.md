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

A binary relation $\mathcal{B}$ on the set $V$ of the nodes of a directed graph
is a bisimulation if the following condition is satisfied [@gentilini]:

\begin{gather} (a,b) \in \mathcal{B} \implies \begin{cases} a \to a' &\implies
\exists b' \in V \mid (a',b') \in \mathcal{B} \land b \to b'\\ b \to b'
&\implies \exists a' \in V \mid (a',b') \in \mathcal{B} \land a \to a'
\end{cases} \end{gather}

A _labeling function_ $\ell : V \to L$ may be introduced, in which case the
graph becomes a _Kripke structure_ and the additional condition
$(a,b) \in \mathcal{B} \implies \ell(a) = \ell(b)$ must be satisfied.

<p style="text-align: center;">

![On the left, a balanced tree paired with a labeling function which induces a partition on $V$ of cardinality 2. We represented visually the corresponding maximum bisimulation on the right, computed using \texttt{BisPy}.\label{fig:example}](example.png)

</p>

The notion of _bisimulation_ and in particular of _maximum bisimulation_ —
namely the bisimulation which contains all the other bisimulations on the graph
— has applications in modal logic, formal verification and concurrency theory
[@kanellakis], and is used for graph reduction as well [@gentilini]. The fact
that _graphs_ may be used to create digital models of a wide span of complex
systems makes bisimulation a useful tool in many different cases. For this
reason several algorithms for the computation of maximum bisimulation have been
studied throughout the years, and it is now widely known that the problem has
an $O(|E| \log |V|)$ algorithmic solution, where $V$ is the set of nodes in the
graph, and $E$ is the set of edges of the graph.

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

# Example

We present the code which we used to generate the example shown in
\autoref{fig:example}. First of all we import the modules needed
to generate the graph (\texttt{BisPy} takes \texttt{NetworkX} directed graphs
in input) and to compute the maximum bisimulation.

```python
>>> import networkx as nx
>>> from bispy import compute_maximum_bisimulation
```

After that we generate the graph, which as we mentioned before is a balanced
tree with _branching-factor_=2 and _depth_=3. We also create a list of tuples
which represents the labeling function which we employed in the example.

```python
>>> graph = nx.balanced_tree(2,3, create_using=nx.DiGraph)
>>> labels = [(0,1,2,3,4,5,6,7,9,10,11,12,13),(8,14)]
```

We can now compute the maximum bisimulation of the Kripke structure taken into
account as follows:

```python
>>> compute_maximum_bisimulation(graph, labels)
[(4,5),(7,9,10,11,12,13),(8,14),(3,6),(0,),(1,2)]
```

The visualization shown above has been drawn using the library
\texttt{PyGraphviz}. \texttt{BisPy} provides the requested output in the form
of a list of tuples, each of which contains the labels of all the nodes
which are members of an equivalence class of the maximum bisimulation.

# Statement of need

To the best of our knowledge \texttt{BisPy} is the first Python project to
address the problem of bisimulation and to fulfill the needs of an healthy open
source project. We found some sparse implementations of _Paige-Tarjan_'s
algorithm, however the source code lacked documentation and test cases, and did
not seem to be intended for distribution.

We think that our project may be a useful tool to study practical cases for
people who are approaching the field — since the notion of bisimulation may be
somewhat counterintuitive at first glance — as well as to established
researchers, who may use \texttt{BisPy} to study improvements on particular
types of graphs and to compare new algorithms with the state of the art.

# Acknowledgements

We acknowledge the support received from Alberto Casagrande during the
preliminar theoretical study of the topic, as well as SISSA mathLab for
providing the hardware to perform experiments on large graphs.

# References
