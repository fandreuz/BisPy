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
studied throughout the years, and it is now known that the problem has an
$O(|E| \log |V|)$ algorithmic solution [@paigetarjan], where $V$ is the set of
nodes in the graph, and $E$ is the set of edges of the graph.

$\texttt{BisPy}$ is a Python package for the computation of maximum
bisimulation.

# Statement of need

To the best of our knowledge \texttt{BisPy} is the first Python project to
address the problem presented above, and to fulfill the needs of an healthy
open source project. We found some sparse implementations of the most famous
algorithm for the computation of the maximum bisimulation (_Paige-Tarjan_),
however the source code lacked documentation and test cases, and did not seem
to be intended for distribution.

We think that our project may be a useful tool to study practical cases for
students approaching the field — since the notion of bisimulation may be
somewhat counterintuitive at first glance — as well as to established
researchers, who may use \texttt{BisPy} to study improvements on particular
types of graphs and to compare new algorithms with the state of the art.

It is interesting to observe that the package \texttt{BisPy}, briefly presented
below, contains the implementation of more than one algorithm for the
computation of maximum bisimulation, and every algorithm uses a peculiar
strategy to obtain the result. For this reason we think that our package may be
useful to assess the performance of different approaches on a particular
problem.

# \texttt{BisPy}

Our package contains the implementation of the following algorithms:

- Paige-Tarjan [-@paigetarjan], which employs an insight from the famous
  algorithm for the minimization of finite states automata [@hopcroft];
- Dovier-Piazza-Policriti [-@dovier], which uses the notion of _rank_ to
  optimize the overhead of splitting the initial partition, and can be computed
  — prior the execution of the algorithm — using an $O(|V|+|E|)$ procedure
  [@sharir; @tarjan];
- Saha [-@saha], which can be used to update the maximum bisimulation of a
  graph after the addition of a new edge, and is more efficient than the
  computation _from scratch_ in some cases (the computational complexity
  depends on how much the maximum bisimulation changes due to the
  modification).

Other algorithms to compute the maximum bisimulation are available, but for
what we could see they are slight variations of one of those mentioned above,
or tailored on particular cases.

Our implementations have been tested and documented deeply; moreover we
splitted the algorithms in smaller functions, which we preferred over having a
monolithic block of code in order to improve readability and testability. This
kind of modularity allowed us to reuse functions across multiple algorithms,
since several procedures are shared (e.g., $\texttt{split}$, or the computation
of rank), and for the same reason we think that the addition of new
functionalities would be straightforward since we already have a significant
set of common functions implemented.

# Example

We present the code which we used to generate the example shown in
\autoref{fig:example}. First of all we import the modules needed to generate
the graph (\texttt{BisPy} takes \texttt{NetworkX} directed graphs in input) and
to compute the maximum bisimulation.

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
of a list of tuples, each of which contains the labels of all the nodes which
are members of an equivalence class of the maximum bisimulation.

# Acknowledgements

We acknowledge the support received from Alberto Casagrande during the
preliminar theoretical study of the topic, as well as SISSA mathLab for
providing the hardware to perform experiments on large graphs.

# References
