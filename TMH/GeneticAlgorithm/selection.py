import math
import random

from GeneticAlgorithm.individuo import Fenotype


class Selection:
    population: list[Fenotype]
    fitness: list[float]
    quantity: int

    def __init__(
        self,
        population,
        quantity,
    ):
        pop = population.copy()
        random.shuffle(pop)
        fit = [ind.compute_distance() for ind in pop]
        self.quantity = quantity

        self.population, self.fitness = [
            pop[i] for i in range(len(pop)) if fit[i] != math.inf
        ], [fit[i] for i in range(len(fit)) if fit[i] != math.inf]

    def elitism(self):
        return sorted(
            self.population, key=lambda ind: self.fitness[self.population.index(ind)]
        )[: self.quantity]

    def tournament(self, group_size: int):
        new_population = self.population.copy()
        while len(new_population) > self.quantity:
            best = []
            for g in range(len(self.population) // group_size):
                group = self.population[g * group_size : (g + 1) * group_size]
                best_individual = min(
                    group, key=lambda ind: self.fitness[self.population.index(ind)]
                )
                best.append(best_individual)
            new_population = best
        while len(new_population) < self.quantity:
            c = None
            while c is None or c in new_population:
                c = random.choice(self.population)
            new_population.append(c)

        return new_population

    def roulette(self):

        total_fitness = sum(self.fitness)
        proportional_fitness = [f / total_fitness for f in self.fitness]
        new_population = []

        for _ in range(self.quantity):
            r = random.random()
            s = 0
            for j in range(len(self.population)):
                s += proportional_fitness[j]
                if s >= r:
                    new_population.append(self.population[j])
                    break
        return new_population

    def select(self, type, *args, **kwargs):
        if type == 1:
            return self.elitism()
        elif type == 2:
            return self.tournament(*args, **kwargs)
        elif type == 3:
            return self.roulette()
        else:
            raise Exception("Invalid selection type")
