from Agents.RandomAgent import RandomAgent as ra
from Agents.AdrianHerasAgent import AdrianHerasAgent as aha
from Agents.AlexPastorAgent import AlexPastorAgent as apa
from Agents.AlexPelochoJaimeAgent import AlexPelochoJaimeAgent as apja
from Agents.CarlesZaidaAgent import CarlesZaidaAgent as cza
from Agents.CrabisaAgent import CrabisaAgent as ca
from Agents.EdoAgent import EdoAgent as ea
from Agents.PabloAleixAlexAgent import PabloAleixAlexAgent as paaa
from Agents.SigmaAgent import SigmaAgent as sa
from Agents.TristanAgent import TristanAgent as ta

from Managers.GameDirector import GameDirector
AGENTS = [ra, aha, apa, apja, cza, ca, ea, paaa, sa, ta]

import random
import numpy as np
from deap import base, creator, tools, algorithms
import multiprocessing

# ===== 1. Definir el problema de optimización (Maximización o Minimización) =====
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # Maximización
creator.create("Individual", list, fitness=creator.FitnessMax)

# ===== 2. Inicialización de individuos =====

def normalize_individual(individual):
    """Normaliza los valores del individuo para que sumen 1."""
    for i in range(len(individual)):
        individual[i] = abs(individual[i])  # Asegurar que los valores son positivos
    total = sum(individual)
    if total == 0:
        return individual  # Evitar división por cero (debería ser raro)
    for i in range(len(individual)):
        individual[i] /= total
    return individual

def init_individual():
    """Crea una lista de 10 valores aleatorios y los normaliza para que sumen 1."""
    raw_values = [random.random() for _ in range(len(AGENTS))]
    normalized_values = normalize_individual(raw_values)
    return creator.Individual(normalized_values)


# ===== 3. Función de fitness =====
def run_pycatan_simulation(group, rounds=4):
    """Ejecuta una simulación de PyCatan con 4 individuos y devuelve sus puntuaciones."""
    out = {0:0, 0:0, 0:0, 0:0}
    for _ in range(rounds):
        try:
            game_director = GameDirector(agents=group, max_rounds=200, store_trace=False)
            game_trace = game_director.game_start(print_outcome=False)
            last_round = max(game_trace["game"].keys(), key=lambda r: int(r.split("_")[-1]))
            last_turn = max(game_trace["game"][last_round].keys(), key=lambda t: int(t.split("_")[-1].lstrip("P")))
            victory_points = game_trace["game"][last_round][last_turn]["end_turn"]["victory_points"]
           
            winner = max(victory_points, key=lambda player: int(victory_points[player]))
            for agent in out.keys():
                if agent == int(winner.lstrip("J")):
                    out[agent] += 1
        except Exception as e:
            print(f"Error: {e}")
        
def run_pycatan_simulation(group, pos):
    """Ejecuta una simulación de PyCatan con 4 individuos y devuelve sus puntuaciones."""
    
    while True:
        try:
            game_director = GameDirector(agents=group, max_rounds=200, store_trace=False)
            game_trace = game_director.game_start(print_outcome=False)
            last_round = max(game_trace["game"].keys(), key=lambda r: int(r.split("_")[-1]))
            last_turn = max(game_trace["game"][last_round].keys(), key=lambda t: int(t.split("_")[-1].lstrip("P")))
            victory_points = game_trace["game"][last_round][last_turn]["end_turn"]["victory_points"]
            
            # Ordenar jugadores por puntos de victoria de mayor a menor
            sorted_players = sorted(victory_points.keys(), key=lambda player: int(victory_points[player]), reverse=True)
            
            # Asignar puntos según la posición, ajustando el índice con (round_idx + i) % 4
            points_distribution = [1, 0.5, 0.25, 0] 
            for rank, player in enumerate(sorted_players):
                agent_id = int(player.lstrip("J"))
                if agent_id == pos:
                    return points_distribution[rank]
        except Exception as e:
            print(f"Error: {e}")

def evaluate_individual(args):
    """Evalúa un solo individuo ejecutando varias simulaciones y actualiza pos_win."""
    individual, partidas = args
    f = 0
    # partidas = 12
    
    for p in range(partidas):
        ag = np.random.choice(AGENTS, 1, p=individual)[0]
        oponents = list(np.random.choice(AGENTS, 3, replace=True))
        group = oponents[:p % 4] + [ag] + oponents[p % 4:]
        
        fit = run_pycatan_simulation(group, p % 4)
        f += fit
        if fit == 1:
            with manager.Lock():  # Asegurar acceso seguro a `pos_win_shared`
                pos_win_shared[p % 4] += 1
            
    return f


def fitness(population, partidas=12):
    args_list = [(ind, partidas) for ind in population]
    fitnesses = toolbox.map(toolbox.evaluate, args_list)  # Evaluación en paralelo
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = (fit,)  # Asignar valores de fitness

def seleccion_por_torneo_con_mantencion(population, k, tournsize=3):
    # Selección por torneo (como normalmente lo haría DEAP)
    selected_individuals = tools.selTournament(population, k, tournsize=tournsize)
    
    # Seleccionar al mejor individuo
    best_individual = tools.selBest(population, k=1)[0]
    
    # Asegurar que el mejor individuo se incluya en la próxima generación
    if best_individual not in selected_individuals:
        selected_individuals[0] = best_individual  # Sustituir al peor por el mejor
        
    return selected_individuals


# ===== 4. Configuración del toolbox =====
toolbox = base.Toolbox()
toolbox.register("individual", init_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


manager = multiprocessing.Manager()
pos_win_shared = manager.list([0, 0, 0, 0])  # Lista compartida entre procesos
NUM_CORES = max(1,multiprocessing.cpu_count()-1)


toolbox.register("evaluate", evaluate_individual)
# ===== 5. Algoritmo Genético =====
def main(poblacion, partidas=12, ngen=50, mutpb=0.1, cxpb=0.5):
    pool = multiprocessing.Pool(processes=NUM_CORES)
    toolbox.register("map", pool.map)
    with manager.Lock():  # Asegurar acceso seguro a `pos_win_shared`
        pos_win_shared[:] = [0, 0, 0, 0]
    toolbox.register("mate", tools.cxBlend, alpha=cxpb)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=mutpb)

    random.seed(42)
    population = toolbox.population(n=poblacion)  # Población inicial de 4 individuos por partida
    pos_win=[0,0,0,0]
    # Crear logbook
    logbook = tools.Logbook()
    logbook.header = ["gen", "avg", "max"]  # Encabezado de los datos
    
    
    fitness(population, partidas=partidas)

    # Estadísticas
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)

    record = stats.compile(population)  # Obtener estadísticas de la generación
    logbook.record(gen=0, **record) 

    for gen in range(1,ngen+1):
        # print(f"Generación {gen}")
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
        for ind in offspring:
            ind[:] = normalize_individual(ind)

        fitness(offspring, partidas=partidas)

        population = seleccion_por_torneo_con_mantencion(offspring + population, poblacion, tournsize=3)
        record = stats.compile(population)
        logbook.record(gen=gen, **record)
    # Cerrar pool de procesos
    pool.close()
    pool.join()
    # Mejor individuo
    print(f"Partidas ganadas por posicion: {pos_win_shared}")
    best_ind = tools.selBest(population, k=1)[0]
    max_fit = best_ind.fitness.values[0]
    print("\nMejor solución encontrada:", best_ind)
    return logbook, best_ind,max_fit, pos_win_shared


