![Python package](https://github.com/fAndreuzzi/BisPy/workflows/Python%20package/badge.svg?branch=master) <a href='https://coveralls.io/github/fAndreuzzi/BisPy'><img src='https://coveralls.io/repos/github/fAndreuzzi/BisPy/badge.svg' alt='Coverage Status' /></a>
 [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE) <img src='https://img.shields.io/badge/Code%20style-Black-%23000000'/> [![Documentation Status](https://readthedocs.org/projects/bispy-bisimulation-in-python/badge/?version=latest)](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest)

# Description
**BisPy** is a Python package for the computation of the maximum bisimulation of directed graphs. At the moment it supports the following algorithms:
- Paige-Tarjan
- Dovier-Piazza-Policriti
- Saha

An brief introduction to the problem can be found [here](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest#a-brief-introduction-to-bisimulation).

## Dependencies and installation
**BisPy** requires requires the modules `llist, networkx`. The code is tested
for *Python 3*, while compatibility with *Python 2* is not guaranteed. It can
be installed using `pip` or directly from the source code.

### Installing via *pip*
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

## Documentation
We used [Sphinx](http://www.sphinx-doc.org/en/stable/) and
[ReadTheDocs](https://readthedocs.org/) for code documentation. You can view
the documentation [here](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest).

To build the HTML version of the docs locally use:

```bash
> cd docs
> make html
```

The generated html can be found in `docs/build/html`.

## Testing

We are using GitHub actions for continuous intergration testing. The current
status is shown in the following badge: [Python package](https://github.com/fAndreuzzi/BisPy/workflows/Python%20package/badge.svg?branch=master).

To run tests locally (`pytest` is required) use the command:

```bash
> pytest tests
```

From the root folder of **BisPy**.

## Authors and acknowledgements
**BisPy** is currently developed and mantained by **Francesco Andreuzzi**.
You can contact me at:
* andreuzzi.francesco at gmail.com
* fandreuz at sissa.it

The project has been developed under the supervision of professor
**Alberto Casagrande** (*University of Trieste*), which was my advisor for
my *bachelor thesis*.

## How to contribute
Contributors are welcome! We are more than happy to receive contributions on
tests, documentation and new features. Our
[Issues](https://github.com/fAndreuzzi/BisPy/issues) section is always full of
things to do.

Here are the guidelines to submit a patch:

  1. Start by opening a new [issue](https://github.com/fAndreuzzi/BisPy/issues)
        describing the bug you want to fix, or the feature you want to
        introduce. This lets us keep track of what is being done at the moment,
        and possibly avoid writing different solutions for the same problem.

  2. Fork the project, and setup a **new** branch to work in (*fix-issue-22*,
        for instance). If you do not separate your work in different branches
        you may have a bad time when trying to push a pull request to fix
        a particular issue.

  3. Run the [**black**](https://github.com/psf/black) formatter before pushing
        your code for review.

  4. Any significant changes should almost always be accompanied by tests.  The
     project already has good test coverage, so look at some of the existing
     tests if you're unsure how to go about it.

  5. Provide menaningful **commit messages** to help us keeping a good *git*
        history.

  6. Finally you can submbit your *pull request*!

## References
During the development we constulted the following resources:

- Saha, Diptikalyan. "An incremental bisimulation algorithm."
  International Conference on Foundations of Software Technology
   and Theoretical Computer Science.
  Springer, Berlin, Heidelberg, 2007.
  [DOI](https://doi.org/10.1007/978-3-540-77050-3_17)
- Dovier, Agostino, Carla Piazza, and Alberto Policriti.
  "A fast bisimulation algorithm." International Conference on
   Computer Aided Verification.
  Springer, Berlin, Heidelberg, 2001.
  [DOI](https://doi.org/10.1007/3-540-44585-4_8)
- Gentilini, Raffaella, Carla Piazza, and Alberto Policriti.
  "From bisimulation to simulation: Coarsest partition problems."
  Journal of Automated Reasoning 31.1 (2003): 73-103.
  [DOI](https://doi.org/10.1023/A:1027328830731)
- Paige, Robert, and Robert E. Tarjan.
  "Three partition refinement algorithms."
  SIAM Journal on Computing 16.6 (1987): 973-989.
  [DOI](https://doi.org/10.1137/0216062)
- Hopcroft, John.
  "An n log n algorithm for minimizing states in a finite automaton."
  Theory of machines and computations. Academic Press, 1971. 189-196.
- Aczel, Peter.
  "Non-well-founded sets." (1988).
- Kanellakis, Paris C., and Scott A. Smolka.
  "CCS expressions, finite state processes, and three problems of equivalence."
  Information and computation 86.1 (1990): 43-68.
  [DOI](https://doi.org/10.1016/0890-5401(90)90025-D)
- Sharir, Micha.
  "A strong-connectivity algorithm and its applications in data flow analysis."
  Computers & Mathematics with Applications 7.1 (1981): 67-72.
  [DOI](https://doi.org/10.1016/0898-1221(81)90008-0)
- Cormen, Thomas H., et al.
  Introduction to algorithms. MIT press, 2009.
  (ISBN: 9780262533058)

## License

See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
