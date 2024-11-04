from typing import Union

from GeneticAlgorithm.child_generation import GenerateNextGeneration
from GeneticAlgorithm.individuo import Fenotype
from GeneticAlgorithm.replace import Replace
from GeneticAlgorithm.selection import Selection


class GeneticAlgorithm:
    lnumbers: list[float]
    rnumbers: list[float]

    def __init__(self, lnumbers, rnumbers):
        self.lnumbers = lnumbers
        self.rnumbers = rnumbers

    def run(
        self,
        pquantity: int,
        squantity: int,
        cquantity: int,
        max_iterations: int,
        condition_stop: float,
        p_restart_iterations: int,
        selection_type: int,
        cross_types: list,
        mutation_types: list,
        mutation_probability: float,
        replace_type: int,
        replace_arg: Union[int, float],
        select_roulette_gs=None,
    ):
        """run the genetic algorithm

        Args:
            pquantity (int): population quantity
            squantity (int): selection quantity
            cquantity (int): children quantity
            max_iterations (int): max iterations
            condition_stop (float): condition to stop
            p_restart_iterations (int): iterations to restart
            selection_type (int): selection type
            cross_types (list): cross types
            mutation_types (list): mutation types
            mutation_probability (float): mutation probability
            replace_type (int): replace type
            replace_arg (Union[int,float]): replace argument
            select_roulette_gs ([type], optional): group size for roulette selection. Defaults to None.

        """
        population = [
            Fenotype(lnumbers=self.lnumbers, rnumbers=self.rnumbers)
            for _ in range(pquantity)
        ]
        best = 1000000
        best_fitness = []
        best_fitness_indexed = []
        for i in range(max_iterations):
            if best < condition_stop:
                print(f"Condition stop reached at iteration {i}")
                break
            selection = Selection(population=population, quantity=squantity)

            parents = selection.select(
                type=selection_type, group_size=select_roulette_gs
            )

            children = GenerateNextGeneration(
                parent_list=parents,
                probability=mutation_probability,
                cross_types=cross_types,
                mutation_types=mutation_types,
                quantity=cquantity,
            ).generate_children()
            replace = Replace(population, children, pquantity)

            if (
                i % p_restart_iterations == 0
                and len(best_fitness) >= p_restart_iterations
                and min(best_fitness) >= best
            ):
                # print("Restarting the population")
                # No improvement in the last x iterations
                population = replace.catastrophic(2, self.lnumbers, self.rnumbers)
                best_fitness = []
            else:

                population = replace.replace(replace_type, replace_arg)

            best_fitness.append(
                Selection(population=population, quantity=1)
                .elitism()[0]
                .compute_distance()
            )
            if best_fitness[-1] < best:
                best = best_fitness[-1]
                best_fitness_indexed.append((best, i))

            # print(f"Generation: {i} Best: {best_fitness}")

            if best_fitness[-1] > best:
                print("something is wrong")

        # get the best fitness changes and their index
        return (
            best_fitness_indexed,
            Selection(population=population, quantity=1).elitism()[0],
        )
