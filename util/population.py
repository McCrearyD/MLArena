from typing import List
from util.evolutionary_neural_network import *
from controllers.creature_controller import *
from actors.pawns.fitness_pawn import *
from util.match_up import *

import math
import random
import os
import shutil
import json

POPULATION_DIRECTORY = 'populations'


def generate_random_networks(size) -> List[EvoNeuralNetwork]:
    out = []

    for i in range(size):
        out.append(
            EvoNeuralNetwork(NETWORK_DIMENSIONS)
        )

    return out


class Population:
    controller_class = CreatureController
    neural_networks = List[EvoNeuralNetwork]
    creatures_to_nets: dict = None
    opponent_factory: Callable = None
    current_gen: int = 0
    dir_name: str

    max_overall_fitness = 0
    generational_fitnesses = None

    def __init__(self, name: str, size: int = -1, networks: List[EvoNeuralNetwork] = None):
        assert size > 0 or networks != None, 'Populations MUST be initialized with either a size or networks.'
        assert name != None, 'Population MUST have a name.'

        if size < 0:
            self.neural_networks = networks
        else:
            self.neural_networks = generate_random_networks(size)

        self.dir_name = name
        self.generate_creatures()
        self.generational_fitnesses = self.load_generational_fitnesses()

    def set_opponent_factory(self, factory: Callable):
        self.opponent_factory = factory

    def get(self, i: int) -> EvoNeuralNetwork:
        """Returns the neural network at the given index."""
        return self.neural_networks[i]

    def count_alive(self):
        c = 0

        for creature in self.creatures_to_nets.keys():
            if not creature.is_dead:
                c += 1

        return c

    def get_network(self, creature: FitnessPawn):
        return self.creatures_to_nets.get(creature)

    def best_network(self) -> EvoNeuralNetwork:
        best = None
        best_fit = float('-inf')

        for pawn in self.creatures_to_nets.keys():
            fit = pawn.calculate_fitness()
            if fit > best_fit:
                best_fit = fit
                best = self.creatures_to_nets[pawn]

        return best

    def pick_random(self) -> EvoNeuralNetwork:
        fitness_sum = 1

        for pawn in self.creatures_to_nets.keys():
            fitness_sum += pawn.calculate_fitness()

        r = random.randrange(start=0, stop=math.floor(fitness_sum))
        pawns = list(self.creatures_to_nets.keys())
        np.random.shuffle(pawns)

        for pawn in pawns:
            r -= pawn.calculate_fitness()
            if r <= 1:
                return self.creatures_to_nets[pawn]

        raise Exception('This shouldn\'t be possible..')

    def size(self):
        return len(self.neural_networks)

    def build_match_ups(self, other_population: 'Population' = None):
        """Converts the current creature set into a set of MatchUps"""
        match_ups: Set[MatchUp] = set()
        other_creatures = None if other_population is None else list(
            other_population.creatures_to_nets.keys())

        for i, creature_pawn in enumerate(self.creatures_to_nets.keys()):
            match_ups.add(
                MatchUp(
                    creature_pawn,
                    self.opponent_factory(
                    ) if other_creatures is None else other_creatures[i]
                )
            )

        return match_ups

    def generate_creatures(self):
        """Generates creatures that use the current Neural Network set."""
        self.creatures_to_nets = dict()

        for neural_network in self.neural_networks:
            # Create a new creature for this Neural Network.
            new_creature = FitnessPawn()
            new_creature.set_controller(
                self.controller_class(
                    new_creature,
                    neural_network
                )
            )

            # Put back into dict.
            self.creatures_to_nets[new_creature] = neural_network

    def natural_selection(self):
        """Uses natural selection to alter the current Neural Network population."""

        gen_max = max(
            [c.calculate_fitness() for c in self.creatures_to_nets.keys()]
        )

        # Log data
        self.max_overall_fitness = \
            max(self.max_overall_fitness, gen_max)
        self.generational_fitnesses.append(gen_max)

        # Save best network unmutated AND get the best with mutations.
        best = self.best_network()
        new_nets = [
            best.clone(),
            best.clone().mutate()
        ]

        l = round(self.size() / 2) - 1

        # For the rest, cross them over.
        for i in range(l):

            if i < l / 2:
                parentA = self.pick_random()
                parentB = self.pick_random()
                children = parentA.crossover(parentB)
                [child.mutate() for child in children]  # mutate all (2) children
                new_nets.extend(children)

            else:
                cr = (
                    self.pick_random().clone(),
                    self.pick_random().clone()
                )

                cr[1].mutate()
                new_nets.extend(cr)

        # assert self.size() == len(new_nets), \
        #     'Inconsistent population size. Start: %i End: %i' % (
        #         self.size(),
        #         len(new_nets)
        # )

        self.neural_networks = new_nets

    def save_to_dir(self, path: str = None):
        print('\nSaving Population \"%s\"...' % self.dir_name)

        if path == None:
            path = os.path.join(POPULATION_DIRECTORY, self.dir_name)
        else:
            path = os.path.join(POPULATION_DIRECTORY, path)

        # Clean existing dir
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

        # Save all nets inside dir
        for i, net in enumerate(self.neural_networks):
            net.save_to_file('%s/%i' % (path, i))

        if not os.path.isdir('%s/data' % path):
            os.makedirs('%s/data' % path)

        # Save extra data
        with open('%s/data/data.json' % path, 'w') as outfile:
            json.dump({
                'current_gen': self.current_gen,
                'max_overall_fitness': self.max_overall_fitness
            }, outfile)

        generational_fitnesses = np.array(self.generational_fitnesses)
        np.save('%s/data/generational_fitnesses.npy' %
                path, generational_fitnesses)

        print('Success!')

    def list_all_saved():
        """Returns a string describing all of the saved populations."""

        population_names = os.listdir(POPULATION_DIRECTORY)

        out = '\n----------------------------\n'
        for pop_name in population_names:
            p = os.path.join(POPULATION_DIRECTORY, pop_name)
            if os.path.isdir(p):

                with open(os.path.join(p, 'data/data.json')) as f:
                    data: dict = json.load(f)

                    out += '\"%s\": size: %s gens: %s\n' % (
                        pop_name,
                        len(os.listdir(p))-1,
                        str(data.get('current_gen'))
                    )

        out += '----------------------------\n'
        return out

    def is_valid_population_directory(path: str):
        return os.path.exists(os.path.join(POPULATION_DIRECTORY, path))

    def get_valid_populations():
        out = []

        if os.path.isdir(POPULATION_DIRECTORY):
            for f in os.listdir(POPULATION_DIRECTORY):
                if os.path.isdir(os.path.join(POPULATION_DIRECTORY, f)):
                    out.append(f)

        return out

    def load_from_dir(path: str):
        name = path
        path = os.path.join(POPULATION_DIRECTORY, path)

        if not os.path.exists(path):
            raise Exception(
                'Path given %s was not found while trying to load a population.' % path)

        networks = []

        for fname in os.listdir(path):
            path_to_file = os.path.join(path, fname)

            if os.path.isfile(path_to_file):
                if path_to_file.endswith('.npy'):
                    networks.append(
                        EvoNeuralNetwork.load_from_file(path_to_file)
                    )

        population = Population(name=name, networks=networks)
        with open(os.path.join(path, 'data/data.json')) as f:
            j: dict = json.load(f)
            for key in j.keys():
                population.__dict__[key] = j[key]

        return population

    def load_generational_fitnesses(self, path: str = None):
        if path == None:
            path = os.path.join(POPULATION_DIRECTORY, self.dir_name)
        else:
            path = os.path.join(POPULATION_DIRECTORY, path)

        path = '%s/data/generational_fitnesses.npy' % path

        if os.path.isfile(path):
            return np.load(path).tolist()

        return []
