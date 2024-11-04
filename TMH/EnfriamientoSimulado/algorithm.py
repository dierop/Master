import math

from EnfriamientoSimulado.neighbors import Neighborhod
from EnfriamientoSimulado.temperature import Temperature
from GeneticAlgorithm.individuo import Fenotype


class EnfriamientoSimulado:
    best_ind: Fenotype
    best: float

    def __init__(self, lnumbers=None, rnumbers=None, individual=None):
        if individual:
            self.best_ind = individual
        else:
            self.best_ind = Fenotype(lnumbers=lnumbers, rnumbers=rnumbers)
        self.best = self.best_ind.compute_distance()

    def acceptance(self, temperature, old_dis: float, new_dis: float):
        if new_dis == math.inf:
            return False
        elif new_dis < old_dis:
            return True
        try:
            acceptance = math.exp(-(old_dis - new_dis) / temperature)
        except OverflowError:
            return False
        return acceptance < 1

    def run(
        self,
        temperature: float,
        cooling_rate: float,
        cooling_type: int,
        max_iterations: int,
        condition_stop: float,
        n_neighbors: int,
        neighbors_type: int,
        neighbor_side: int,
        cooling_iterations: int = None,
    ):
        """run the enfriamiento simulado algorithm

        Args:
            temperature (float): initial temperature
            cooling_rate (float): cooling rate
            cooling_type (int): cooling type
            max_iterations (int): max iterations
            condition_stop (float): condition to stop
            n_neighbors (int): number of neighbors
            neighbors_type (int): neighbors type
            neighbor_side (int): neighbor side
            cooling_iterations (int, optional): cooling iterations. Defaults to None.

        """
        te = Temperature(temperature, cooling_rate=cooling_rate)
        best_list = [(0, self.best)]
        ind = self.best_ind
        for i in range(1, max_iterations):
            if te.temperature <= 0 or self.best <= condition_stop:
                best_list.append((i, self.best))
                break
            neighborhod = Neighborhod(ind, n_neighbors, neighbors_type, neighbor_side)
            new = neighborhod.get_random_neighbor()
            dis = new.compute_distance()
            if self.acceptance(te.temperature, ind.compute_distance(), dis):
                ind = new
                if dis < self.best:
                    self.best = new.compute_distance()
                    self.best_ind = new
                    best_list.append((i, self.best))

            te.reduce(cooling_type, i, cooling_iterations)
        return best_list, self.best_ind
