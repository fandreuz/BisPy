<p align="center">
  <a href="https://github.com/fAndreuzzi/BisPy" target="_blank" >
    <img alt="BisPy" src="logo.png" width="400" />
  </a>
</p>

![Python package](https://github.com/fAndreuzzi/BisPy/workflows/Python%20package/badge.svg?branch=master)
<a href='https://coveralls.io/github/fAndreuzzi/BisPy'><img src='https://coveralls.io/repos/github/fAndreuzzi/BisPy/badge.svg' alt='Coverage Status' /></a>
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)
<img src='https://img.shields.io/badge/Code%20style-Black-%23000000'/>
[![Documentation Status](https://readthedocs.org/projects/bispy-bisimulation-in-python/badge/?version=latest)](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest)
[![status](https://joss.theoj.org/papers/9d9c3ca0715d482938b5a450525cefa0/status.svg)](https://joss.theoj.org/papers/9d9c3ca0715d482938b5a450525cefa0)
[![PyPI version](https://badge.fury.io/py/BisPy.svg)](https://badge.fury.io/py/BisPy)

## Description

**BisPy** is a Python package for the computation of the maximum bisimulation
of directed graphs. At the moment it supports the following algorithms:

- Paige-Tarjan
- Dovier-Piazza-Policriti
- Saha

A brief introduction to the problem can be found
[here](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest#a-brief-introduction-to-bisimulation).

## Usage

### Paige-Tarjan, Dovier-Piazza-Policriti

To compute the maximum bisimulation of a graph, first of all we import
`paige_tarjan` and `dovier_piazza_policriti` from **BisPy**, as well as the
package _NetworkX_, which we use to represent graphs:

```python
>>> import networkx as nx
>>> from bispy import compute_maximum_bisimulation, Algorithms
```

We then create a simple graph:

```python
>>> graph = nx.balanced_tree(2,3, create_using=nx.DiGraph)
```

It's important to set `create_using=nx.DiGraph` since **BisPy** works only with
_directed_ graphs. Now we can compute the _maximum bisimulation_ using
_Paige-Tarjan_'s algorithm, which is the default for the function
`compute_maximum_bisimulation`:

```python
>>> compute_maximum_bisimulation(graph)
[(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6), (1, 2), (0,)]
```

We can use _Dovier-Piazza-Policriti_'s algorithm as well:

```python
>>> compute_maximum_bisimulation(graph, algorithm=Algorithms.DovierPiazzaPolicriti)
[(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6),  (1, 2), (0,)]

```

We may also introduce a _labeling set_ (or _initial partition_):

```python
>>> compute_maximum_bisimulation(graph, initial_partition=[(0,7,10), (1,2,3,4,5,6,8,9,11,12,13,14)])
[(7, 10), (5, 6), (8, 9, 11, 12, 13, 14), (3, 4), (2,), (1,), (0,)]

```

### Saha

In order to use _Saha_'s algorithm we only need to import the following
function:

```python
>>> from bispy import saha
```

We call that function to obtain an object of type `SahaPartition`, which has a
method called `add_edge`. This method adds a new edge to the graph and
recomputes the maximum bisimulation incrementally:

```python
saha_partition = saha(graph)
```

(We reused the `graph` object which we defined in the previous paragraph). We
can now use the aforementioned method `add_edge` (note that when you call this
method the instance of `graph` which you passed is **not** modified):

```python
>>> for edge in [(1,0), (4,0)]:
...    maximum_bisimulation = saha_partition.add_edge(edge)
...    print(maximum_bisimulation)
[(3, 4, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,)]
[(3, 5, 6), (7, 8, 9, 10, 11, 12, 13, 14), (0,), (2,), (1,), (4,)]
```

## Documentation

You can read the documentation (hosted on ReadTheDocs) at this
[link](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest).

To build the HTML version of the docs locally use:

```bash
> cd docs
> make html
```

The generated html can be found in `docs/build/html`.

## Dependencies and installation

**BisPy** requires the modules `llist, networkx`. The code is tested
for _Python 3_, while compatibility with _Python 2_ is not guaranteed. It can
be installed using `pip` or directly from the source code.

### Installing via _pip_

To install the package:

```bash
> pip install bispy
```

To uninstall the package:

```bash
> pip uninstall bispy
```

### Installing from source

You can clone this repository on your local machine using:

```bash
> git clone https://github.com/fAndreuzzi/BisPy
```

To install the package:

```bash
> cd BisPy
> python setup.py install
```


## Testing

We are using **GitHub actions** for continuous intergration testing. To run
tests locally (`pytest` is required) use the following command from the root
folder of **BisPy**:

```bash
> pytest tests
```

## Authors and acknowledgements

**BisPy** is currently developed and mantained by **Francesco Andreuzzi**. You
can contact me at:

- andreuzzi.francesco at gmail.com
- fandreuz at sissa.it

The project has been developed under the supervision of professor **Alberto
Casagrande** (_University of Trieste_), which was my advisor for my _bachelor
thesis_.

## Reporting a bug

The best way to report a bug is using the
[Issues](https://github.com/fAndreuzzi/BisPy/issues) section. Please, be clear,
and give detailed examples on how to reproduce the bug (the best option would
be the graph which triggered the error you are reporting).

## How to contribute

We are more than happy to receive contributions on tests, documentation and
new features. Our [Issues](https://github.com/fAndreuzzi/BisPy/issues)
section is always full of things to do.

Here are the guidelines to submit a patch:

1. Start by opening a new [issue](https://github.com/fAndreuzzi/BisPy/issues)
   describing the bug you want to fix, or the feature you want to introduce.
   This lets us keep track of what is being done at the moment, and possibly
   avoid writing different solutions for the same problem.

2. Fork the project, and setup a **new** branch to work in (_fix-issue-22_, for
   instance). If you do not separate your work in different branches you may
   have a bad time when trying to push a pull request to fix a particular
   issue.

3. Run [black](https://github.com/psf/black) before pushing
   your code for review.

4. Any significant changes should almost always be accompanied by tests. The
   project already has good test coverage, so look at some of the existing
   tests if you're unsure how to go about it.

5. Provide menaningful **commit messages** to help us keeping a good _git_
   history.

6. Finally you can submbit your _pull request_!

## References

During the development we constulted the following resources:

- Saha, Diptikalyan. "An incremental bisimulation algorithm." International
  Conference on Foundations of Software Technology and Theoretical Computer
  Science. Springer, Berlin, Heidelberg, 2007.
  [DOI](https://doi.org/10.1007/978-3-540-77050-3_17)
- Dovier, Agostino, Carla Piazza, and Alberto Policriti. "A fast bisimulation
  algorithm." International Conference on Computer Aided Verification.
  Springer, Berlin, Heidelberg, 2001.
  [DOI](https://doi.org/10.1007/3-540-44585-4_8)
- Gentilini, Raffaella, Carla Piazza, and Alberto Policriti. "From bisimulation
  to simulation: Coarsest partition problems." Journal of Automated Reasoning
  31.1 (2003): 73-103. [DOI](https://doi.org/10.1023/A:1027328830731)
- Paige, Robert, and Robert E. Tarjan. "Three partition refinement algorithms."
  SIAM Journal on Computing 16.6 (1987): 973-989.
  [DOI](https://doi.org/10.1137/0216062)
- Hopcroft, John. "An n log n algorithm for minimizing states in a finite
  automaton." Theory of machines and computations. Academic Press, 1971.
  189-196.
- Aczel, Peter. "Non-well-founded sets." (1988).
- Kanellakis, Paris C., and Scott A. Smolka. "CCS expressions, finite state
  processes, and three problems of equivalence." Information and computation
  86.1 (1990): 43-68. [DOI](<https://doi.org/10.1016/0890-5401(90)90025-D>)
- Sharir, Micha. "A strong-connectivity algorithm and its applications in data
  flow analysis." Computers & Mathematics with Applications 7.1 (1981): 67-72.
  [DOI](<https://doi.org/10.1016/0898-1221(81)90008-0>)
- Cormen, Thomas H., et al. Introduction to algorithms. MIT press, 2009.
  (ISBN: 9780262533058)

## License

See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
