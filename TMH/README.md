# 💩 TMH: Tecnicas Metahuristicas

Source code for TMH subject. The main focus are the usage of algorithms to search for suboptimal solutions to a problem.  In this case Genetic Algorithm and Simulated Annealing to solve how to minimize the difference between two groups of numbers using basic operations.

## ⚙️ Installation & Setup

To install it you just need to run the following command in an environment with Python
3.10 or higher with [poetry](https://python-poetry.org/docs/#installation) installed:

`poetry install`

Finally, in order to run the static code analysis checks you should use the following
set of commands once installed:

```
poetry run ruff --fix .
poetry run black .
```

## 💻 Projects

>[!Warning] 
>Some of the code is mixed between the two projects :S

- __Genetic Algorithm__: Has the code for all the definition of the individuals and the algorithm implementation. It has different types of selection, mutation, replacing, reproducing and some code to try fixing the bad solutions.

- __Enfriamiento Simulado__: Has the code for the implementation of the algorithm. It has different types of neigthbors creation, and annealing.

- __test.ipynb__: Expertiments, test and graphics over the results.
