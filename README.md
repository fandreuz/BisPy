![Python package](https://github.com/fAndreuzzi/Bisimulation-Algorithms/workflows/Python%20package/badge.svg?branch=master) <a href='https://coveralls.io/github/fAndreuzzi/Bisimulation-Algorithms'><img src='https://coveralls.io/repos/github/fAndreuzzi/Bisimulation-Algorithms/badge.svg' alt='Coverage Status' /></a>
 [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE) <img src='https://img.shields.io/badge/code style-PEP8-informational' alt='Code style' />

# Bisimulation-Algorithms

## The problem
Let's consider a directed graph G=(V,E). A *bisimulation* on G is a binary relation R on V which satisfies the following two properties:

![Bisimulation definition](res/bisimulation-definition.png)

This is in fact a condition on the *behavior* of the nodes: two nodes *behave* in the *same way* if for each node reached by one of them, there's a fourth node reached by the other node which *behaves* like the third.

This informal definition of bisimulation is equivalent to the formal one above, but it's somewhat more explicit.

## Algorithmic approach
The somewhat recursive statement of the problem makes the bisimulation an apparently difficult problem from an algorithmic point of view. However, as Kanellakis C. and Smolka S. shown in their paper published in 1990, computing the *maximum* bisimulation of a graph (namely the *biggest* bisimulation, the one which relates the highest number of nodes) is equivalent to determining the *relational stable coarsest partition*.

The *RSCP* of a set S given a binary relation R, as the name suggests, is the *coarsest* (which contains the fewest number of blocks) *stable partition*, where *stability* is a quality of partitions which is defined as follows for a given partition P:

![Stability definition](res/stability-definition.png)

This statemente is reassuring: in order to verify that two nodes are *bisimilar* (which is quite interesting for the applications) we do not need to visit exhaustively their children, and then the children of the children, and so on. We only need to compute the RSCP of V with respect to the relation E, and check whether the two nodes are in the same block.

## Algorithms
This library contains the implementation in Python 3 of the following algorithms:
|  Name        |  Strategy   | Complexity  | Link |
|------------|:-------------:|:---:| -----------------------|
| **Paige-Tarjan** | Negative    | ![Loglinear complexity](res/log-linear-complexity.png)  | ![Paper](https://scholarsmine.mst.edu/cgi/viewcontent.cgi?article=1348&context=math_stat_facwork) |
| **Dovier-Piazza-Policriti** | Negative    | ![Loglinear complexity](res/log-linear-complexity.png) | ![Paper](https://pdf.sciencedirectassets.com/271538/1-s2.0-S0304397500X05348/1-s2.0-S030439750300361X/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEH8aCXVzLWVhc3QtMSJHMEUCIQD0HTsvtrNKRZ0B59etVuPxRrKlnrF59Jxm1YsQ7rVkCwIgbmetaKcZEuJ5s8qq1zls67pbKcwJ3OMj3tWmJ251RwwqvQMIt%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARADGgwwNTkwMDM1NDY4NjUiDIGG0Avb8O2EJGz%2BESqRA5iL0g3GixhOZG1gNqLdKlywdsgMc29vXar9vInoNowNMXlwJ9Jg0G34qjx4KQJvEgeptuAzMhraNSe5HsOMPTNrQ%2FZz2FL7q8igYLJ3v2xNqTDBKUJGsMz5T4GUJp7q8b0iwEQ3kATAvd8iN7T7g5pIseJFfAyongauePhN0Sp9g8P2J3j5C6MgpZ8GSdPcOnnd8GaEeG2LPY68z7zLWqS6og5CGbNxOvn2AYENnxRqs0i07McmR54CZ7mkb%2FGRxuTaGqCPOZqcQBXzvfCHaO171NN4MG%2F%2B3tBxmEMpUydCcYkMggU5kW8mehEtT1IALYNju64teuCEriKuLnODp1eE62A16sjc08fyBwWBIItJWp4kmUC3UH0%2FfG%2FD7XJ%2BQ8wNCv%2BiR4heGjB1wv1zRz3oFOnVvrCweGMRSqM3KBwNHEZyWZ%2BS9CRojBWSytTK1yTAqDcBJC1l7YtLJABVkltBVU%2BKkagQi6f3EYrmBYQ6Ik%2FmStSV%2F87c476aYYK%2BPAF6prW7kZGU7L69Poe08eiGMP2J5oIGOusBB1u7bA4JCQl9lFRLYAiOzI9ikwqsVPXlJsSMcZZ4hLEK5Xpi0T81L%2BhN076UQEq1QjxQx7VWP0JBFZxYQ12ZaEDFfMiEK85arFYIgDN2L38T6LAmPohMzEc4A%2BF65zQITnoShO05Lb%2Bz9k01rODLQxp0hxu5KM%2BTncTAOnjOlAJUrt7ywld5AVQbI27x5olVDV03OVe83%2BGbVjjB3%2Ba9uAj7xvTLjfTDhG9%2Blg0EZt2NfI2Fd9rUVVociW0iQS7dJGF58R2BvS9r%2BcFgph8UsgMAcr%2BFpXmHn2iHoesHSWeOvIqgDJqwZ6TdUQ%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210323T074502Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYVNXX7VHM%2F20210323%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=97fbaf2af0ce8f90407bae54d0667e1e4891a5b60ce7bef0d22e22371a8bad54&hash=bc9051325abb41aa7a3ed91285fb0c9c609ce978a08461e47972cbc8298aa479&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S030439750300361X&tid=spdf-57e77b0e-7d66-4742-a044-ceeb86a8c5e9&sid=cb6c89ab9f04f344098ae8a94138b86b77fdgxrqb&type=client) |
| **Saha**         | Incremental |  Depends on changes. | ![Paper](https://www.researchgate.net/profile/Diptikalyan-Saha/publication/221583570_An_Incremental_Bisimulation_Algorithm/links/57dbbcd508ae72d72ea44ac1/An-Incremental-Bisimulation-Algorithm.pdf) |

## Installation
The package isn't published, therefore the following steps are needed:
1. Open a terminal window;
2. Navigate to a suitable directory;
3. Clone the repository: `git clone https://github.com/fAndreuzzi/Bisimulation-Algorithms.git`;
4. Open the new directory `cd Bisimulation-Algorithms`;
5. Install the package in development mode: `pip install -e ./` or `pip3 install -e ./`.

## Usage
This example shows how to use the PTA algorithm on a given graph. We use [NetworkX](https://networkx.org/) to represent the input.

The following snippet:
```python
import networkx as nx

graph = nx.DiGraph()
graph.add_nodes_from(range(5))
graph.add_edges_from([(0,1), (0,3), (1,4), (2,3), (4,3)])
```
intializes a graph which contains 5 nodes (from 0 to 4) and some edges. We assume that the initial partition is the trivial one:
`{0,1,2,3,4}`.

We can obtain the RSCP with the Paige-Tarjan Algorithm as follows:
```python
from bisimulation_algorithms import paige_tarjan

rscp = paige_tarjan(graph)
print(rscp)
```
Output: `[(3,), (1,), (2, 4), (0,)]`

If we wanted to use a different initial partition, like:
```
initial_partition = [(0,1,2), (3,4)]
```

the code would have been:
```python
rscp = paige_tarjan(graph, initial_partition)
print(rscp)
```
Output: `[(3,), (1,), (2,) (4,), (0,)]`

## Examples
Initial partition | RSCP
--- | ---
![](res/pta-before.png) | ![](res/pta-after.png)
![](res/pta-before2.png) | ![](res/pta-after2.png)

## Applications
Work in progress.
