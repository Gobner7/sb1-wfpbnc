import random
from deap import base, creator, tools, algorithms

class GeneticOptimizer:
    def __init__(self, strategy, backtester):
        self.strategy = strategy
        self.backtester = backtester
        self.setup_genetic_algorithm()

    def setup_genetic_algorithm(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_int", random.randint, 10, 100)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_int, n=5)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def evaluate(self, individual):
        # Update strategy parameters
        params = {
            'n_sma_fast': individual[0],
            'n_sma_slow': individual[1],
            'rsi_period': individual[2],
            'atr_multiplier': individual[3],
            'volume_ratio_threshold': individual[4] / 10  # Scale down to get values between 1 and 10
        }
        self.strategy.update_params(params)

        # Run backtest
        stats = self.backtester.run(self.data, self.strategy)
        return stats['Return [%]'],

    def optimize(self, data, population_size=50, generations=10):
        self.data = data
        population = self.toolbox.population(n=population_size)
        result, logbook = algorithms.eaSimple(population, self.toolbox, cxpb=0.5, mutpb=0.2, ngen=generations, verbose=True)

        best_individual = tools.selBest(result, k=1)[0]
        best_params = {
            'n_sma_fast': best_individual[0],
            'n_sma_slow': best_individual[1],
            'rsi_period': best_individual[2],
            'atr_multiplier': best_individual[3],
            'volume_ratio_threshold': best_individual[4] / 10
        }

        return best_params