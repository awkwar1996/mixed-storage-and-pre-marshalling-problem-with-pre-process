#!/usr/bin/env/python
'''
Class of GA
'''
import copy
import time
import torch
from torch.distributions import Categorical
import math
import random
import numpy as np


class GA:
    def __init__(self, S, M, baseLine, settings, rel_per_stage, instance_name):
        self.population = settings['population']
        self.iteration = settings['GA_iteration']
        self.crossover_rate = settings['crossover_rate']
        self.mutation_rate = settings['mutation_rate']
        self.S = S
        self.M = M
        self.chromosome_length = rel_per_stage * M
        self.baseLine = baseLine
        self.instance_name = instance_name
        self.population_list = []

    def initial_population_list(self):
        for i in range(self.population):
            chromosome = []
            for j in range(self.chromosome_length):
                chromosome.append(random.choice(range(self.S * self.S)))
            self.population_list.append(chromosome)

    def main(self, environment):
        iter_result_list, iter_relTime_list, iter_bpNum_list = [], [], []
        self.initial_population_list()

        for epoch in range(self.iteration):
            start_time = time.time()
            print(f'\n---iteration:{epoch}---')

            best_iter_result, best_iter_length, best_iter_bpNum = math.inf, -1, 0
            for i in range(self.population):
                chromosome = self.population_list[i]
                chromosome_result, chromosome_length, chromosome_bpNum = self._ga_step(copy.deepcopy(environment), chromosome, i)
                if best_iter_result > chromosome_result:
                    best_iter_result = chromosome_result
                    best_iter_length = chromosome_length
                    best_iter_bpNum = chromosome_bpNum
            # update phenomone
            iter_result_list.append(best_iter_result)
            iter_relTime_list.append(best_iter_length)
            iter_bpNum_list.append(best_iter_bpNum)
            print(f'results:\n  iter result:  {best_iter_result}\n  global result:{min(iter_result_list)}')
            self._update_chromosome()
            print('iter time', time.time() - start_time)
            print('iter result', best_iter_result)
            print('iter relocation time', best_iter_length)
            print('iter bp number', best_iter_bpNum)
        return iter_result_list, iter_relTime_list, iter_bpNum_list

    def _ga_step(self, environment, chromosome, chromosome_index):
        done = 0
        chromosome_copy = copy.deepcopy(chromosome)
        gene_index = 0
        while not done:
            action = chromosome_copy.pop(0)
            s1 = math.floor(action / self.S)
            s2 = action - s1 * self.S
            while not environment.action_ok(s1, s2):
                action = random.choice(range(self.S * self.S))
                s1 = math.floor(action / self.S)
                s2 = action - s1 * self.S
            self.population_list[chromosome_index][gene_index] = action # 有修复，所以要新加
            done = environment.ga_step(s1, s2)
            gene_index += 1
        result = environment.get_relocation()
        bp_num = environment.get_bp_num()
        return result, gene_index, bp_num

    def _update_chromosome(self):
        for i in range(self.population):
            # 进行变异
            if random.random() < self.mutation_rate:
                random_index = random.choice(range(len(self.population_list[i])))
                self.population_list[i][random_index] = random.choice(range(self.S * self.S))
            else:
                chromosome1 = self.population_list[i]
                chromosome2 = self.population_list[random.choice(range(self.population))]
                random_index = random.choice(range(len(self.population_list[i])))
                chromosome = copy.deepcopy(chromosome1[:random_index])
                chromosome.extend(chromosome2[random_index:])
                self.population_list[i] = chromosome


if __name__ == '__main__':
    pass
