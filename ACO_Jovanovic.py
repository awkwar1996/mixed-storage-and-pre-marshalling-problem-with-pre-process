#!/usr/bin/env/python
'''
ACO method introduced in
Jovanovic R, Tuba M, Voß S. An efficient ant colony optimization algorithm for the blocks relocation problem[J].
European Journal of Operational Research, 2019, 274(1): 78-90.
'''
import copy
import random
import time

import torch
from torch.distributions import Categorical
import math
import numpy as np


class ACO_Jovanovic:
    def __init__(self, S, M, baseLine, settings, rel_per_stage, instance_name):
        self.ant_number = settings['Ant_number']
        self.iteration = settings['aco_Iteration']
        self.weight_decay = 0.9
        self.S = S
        self.M = M
        self.rel_per_stage = rel_per_stage
        self.baseLine = baseLine
        # self.lambdas = (self.rel_per_stage * self.M)/(0.05 * self.baseLine) # 按照提升5%时，每个动作给1设定
        self.instance_name = instance_name

        self.phe = np.full((self.M, self.rel_per_stage, self.S, self.S), float(1/self.S*self.baseLine))
        self.q0 = 0.9
        self.phi = 0.9
        self.p = 0.1

    def main(self, environment):

        iter_result_list, iter_rel_num_list, iter_bp_num_lsit = [self.baseLine], [], []
        for epoch in range(self.iteration):
            start_time = time.time()
            print(f'\n---iteration:{epoch}---')
            # print(f'alpha:{self.alpha}\nbeta: {self.beta}')

            best_iter_result, best_iter_rel_num, best_iter_bp_num = math.inf, -1, -1

            # iter_reward = np.zeros((self.M, self.rel_per_stage, self.S, self.S))
            for a in range(self.ant_number):
                ant_steps, ant_result, ant_bp_num = self._ant_search(copy.deepcopy(environment))
                best_iter_result = min(best_iter_result, ant_result)
                best_iter_rel_num = len(ant_steps)
                best_iter_bp_num = ant_bp_num
                # local update
                for i, step in enumerate(ant_steps):
                    self.phe[step[0], step[1], step[2], step[3]] = self.phi * self.phe[step[0], step[1], step[2], step[3]]
                    self.phe = np.clip(self.phe, float(1/self.S**2*min(iter_result_list)), math.inf)
            iter_result_list.append(best_iter_result)
            iter_rel_num_list.append(best_iter_rel_num)
            iter_bp_num_lsit.append(best_iter_bp_num)
            delta_tau = max(1/(best_iter_result-self.baseLine * 0.3 + 1), 0)
            self.phe = (1-self.p) * self.phe + self.p * delta_tau
            self.phe = np.clip(self.phe, float(1 / self.S ** 2 * min(iter_result_list)), math.inf)
            print(f'results:\n  iter result:  {best_iter_result}\n  global result:{min(iter_result_list)}')
            print('iter time', time.time() - start_time)
            print('iter result', best_iter_result)
            print('iter relocation time', best_iter_rel_num)
            print('iter bp number', best_iter_bp_num)
        return iter_result_list[1:], iter_rel_num_list, iter_bp_num_lsit

    def _ant_search(self, environment):
        steps = []
        stage, rel_index, done = 0, 0, 0

        # valid_time, heu_time, phe_time, get_action_time, step_time, get_rel_time, step_time1 = 0, 0, 0, 0, 0, 0, 0

        # start_time = time.time()
        while not done:
            valid_rels = environment.get_valid_rel()
            heu = environment.get_heuristic_value(valid_rels)
            chosen_rel = self._get_action(heu, valid_rels, stage, rel_index)

            steps.append([stage, rel_index, chosen_rel[0], chosen_rel[1]])
            stage, rel_index, done = environment.aco_step(stage, rel_index, chosen_rel[0], chosen_rel[1])

        result = environment.get_relocation()
        bp_num = environment.get_bp_num()
        # print('ant result calculate time:', time.time() - start_time)
        return steps, result, bp_num

    def _action_index_to_stack(self, action_index):
        '''
        from index ranging from  0-S^2 to relocation stack s1 and s2
        :param action_index: int, from 0-S^2
        :return: outbound stack s1 and in stack s2
        '''
        s1 = math.floor(action_index/self.S)
        s2 = action_index - s1 * self.S
        return int(s1), int(s2)

    def _get_action(self, heu, valid_rels, stage, rel_index):
        if random.random() < self.q0:
            return valid_rels[heu.index(max(heu))]
        else:
            phe = []
            for rel in valid_rels:
                phe.append(self.phe[stage, rel_index, rel[0], rel[1]])

            pro = []
            for index, _ in enumerate(valid_rels):
                pro.append(heu[index]*phe[index])

            if max(pro) == min(pro):
                nor_pro = [1 for _ in valid_rels]
            else:
                nor_pro = [(i - min(pro)) / (max(pro) - min(pro)) for i in pro]

            nor_pro = [i/sum(nor_pro) for i in nor_pro]

            p = random.random()
            index = -1
            cum_sum = 0
            while p > cum_sum:
                index += 1
                cum_sum += nor_pro[index]
            return valid_rels[min(index, len(valid_rels) - 1)]


if __name__ == '__main__':
    pass
