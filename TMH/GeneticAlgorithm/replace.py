from GeneticAlgorithm.individuo import Fenotype
from GeneticAlgorithm.selection import Selection


class Replace:
    population: list[Fenotype]
    children: list[Fenotype]
    quantity: int

    def __init__(self, population, children, quantity):
        self.population = population.copy()
        self.children = children.copy()
        self.quantity = quantity

    def generational_best(self, best_population: int):

        return (
            Selection(self.children, self.quantity - best_population).elitism()
            + Selection(self.population, best_population).elitism()
        )

    def replace_worst(self, number_worst: int):
        # Need to have +- the saem number of children as the population that we want to replace
        return Selection(
            self.children
            + Selection(self.population, len(self.population) - number_worst).elitism(),
            self.quantity,
        ).elitism()

    def gap_generational(self, gap: float):
        q_gaps = int(self.quantity * gap)
        return (
            Selection(self.children, 1 - q_gaps).elitism()
            + Selection(self.population, q_gaps).elitism()
        )

    def catastrophic(self, best: int, lnumbers: list[float], rnumbers: list[float]):
        new_population = Selection(self.population + self.children, best).elitism()

        for _ in range(self.quantity - best):
            new_population.append(Fenotype(lnumbers=lnumbers, rnumbers=rnumbers))
        return new_population

    def replace(self, type: int, *args, **kwargs):
        if type == 1:
            return self.generational_best(*args, **kwargs)
        elif type == 2:
            return self.replace_worst(*args, **kwargs)
        elif type == 3:
            return self.gap_generational(*args, **kwargs)
        elif type == 4:
            return self.catastrophic(*args, **kwargs)
        else:
            raise Exception("Invalid replace type")
