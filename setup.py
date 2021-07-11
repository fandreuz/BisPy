import setuptools

long_description = """
![Python package](https://github.com/fAndreuzzi/BisPy/workflows/Python%20package/badge.svg?branch=master) <a href='https://coveralls.io/github/fAndreuzzi/BisPy'><img src='https://coveralls.io/repos/github/fAndreuzzi/BisPy/badge.svg' alt='Coverage Status' /></a>
 [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE) <img src='https://img.shields.io/badge/Code%20style-Black-%23000000'/> [![Documentation Status](https://readthedocs.org/projects/bispy-bisimulation-in-python/badge/?version=latest)](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest)

## Description
**BisPy** is a Python package for the computation of the maximum bisimulation of directed graphs. At the moment it supports the following algorithms:
- Paige-Tarjan
- Dovier-Piazza-Policriti
- Saha

An brief introduction to the problem can be found [here](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest#a-brief-introduction-to-bisimulation).

## Usage
### Paige-Tarjan, Dovier-Piazza-Policriti
Compute the maximum bisimulation of a graph (represented by an object of type `networkx.DiGraph`):
```python
> import networkx as nx
> from bispy import paige_tarjan, dovier_piazza_policriti

# we create the graph
> graph = networkx.balanced_tree(2,3)

# Paige-Tarjan's algorithm
> paige_tarjan(graph)
[(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6), (1, 2), (0,)]

# and Dovier-Piazza-Policriti's algorithm
> dovier_piazza_policriti(graph)
[(7, 8, 9, 10, 11, 12, 13, 14), (3, 4, 5, 6), (1, 2), (0,)]
```

More about the available features (like using a *labeling set*) is discussed in the documentation for [Paige-Tarjan](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/algorithms/paige_tarjan.html)'s and [Dovier-Piazza-Policriti](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/algorithms/dovier_piazza_policriti.html)'s algorithms.

### Saha
The interface for using *Saha*'s algorithm is a little bit different since we do not want to rebuild the *BisPy* representation of the graph from scratch.
```python
> import networkx as nx
> from bispy import decorate_nx_graph, to_tuple_list, paige_tarjan_qblocks, saha

# we create the graph
> graph = networkx.balanced_tree(2,3)

# we build its BisPy representation
> vertexes, qblocks = decorate_nx_graph(graph)
# compute the maximum bisimulation. `maximum_bisimulation is a list of `_QBlock` objects
> maximum_bisimulation = paige_tarjan_qblocks(qblocks)

# from now on we can update the maximum bisimulation incrementally, everytime
# we add a new edge to the graph
> new_edges_list = random_edges_generator()
> for edge in new_edges_list:
>    maximum_bisimulation = saha(maximum_bisimulation, vertexes, edge)
>    # print the current maximum bisimulation
>    print(to_tuple_list(maximum_bisimulation))
```

Note that *Saha*'s algorithm must be applied on a **maximum bisimulation**, otherwise it is going to return wrong results. This is why we called `paige_tarjan_qblocks` (which is just a version of *Paige-Tarjan*'s algorithm which can be applied to the variable `qblocks`) before the call to *Saha*'s algorithm.

You can read more about [Saha](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/algorithms/saha.html#)'s algorithm and the module [graph_decorator](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/utilities/graph_decorator.html) on the documentation.

## Dependencies and installation
**BisPy** requires requires the modules `llist, networkx`. The code is tested
for *Python 3*, while compatibility with *Python 2* is not guaranteed. It can
be installed using `pip` or directly from the source code.

## Documentation
We used [Sphinx](http://www.sphinx-doc.org/en/stable/) and
[ReadTheDocs](https://readthedocs.org/) for code documentation. You can view
the documentation [here](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest).

## Authors and acknowledgements
**BisPy** is currently developed and mantained by **Francesco Andreuzzi**.
You can contact me at:
* andreuzzi.francesco at gmail.com
* fandreuz at sissa.it

## License
See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
"""

setuptools.setup(
    name="BisPy",
    version="0.1.2",

    author="Francesco Andreuzzi",
    author_email="andreuzzi.francesco@gmail.com",

    description="A bisimulation library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/fAndreuzzi/BisPy",
    project_urls={
        "Bug Tracker": "https://github.com/fAndreuzzi/BisPy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],

    packages=setuptools.find_packages(),
    python_requires=">=3.5",

    license='MIT',

    install_requires=['networkx', 'llist'],
)
