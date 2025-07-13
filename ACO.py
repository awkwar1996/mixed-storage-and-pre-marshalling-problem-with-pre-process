#!/usr/bin/env/python
'''
Class of ACO
'''
import copy
import random
import time

import torch
from torch.distributions import Categorical
import math
import numpy as np


class ACO:
    def __init__(self, S, M, baseLine, settings, rel_per_stage, instance_name):
        self.ant_number = settings['Ant_number']
        self.iteration = settings['aco_Iteration']
        self.weight_decay = settings['weight_decay']
        self.S = S
        self.M = M
        self.rel_per_stage = rel_per_stage
        self.baseLine = baseLine
        self.lambdas = (self.rel_per_stage * self.M)/(0.05 * self.baseLine) # 按照提升5%时，每个动作给1设定
        self.instance_name = instance_name

        self.phe = np.ones((self.M, self.rel_per_stage, self.S, self.S))
        self.alpha = 0.1  # for phe
        self.beta = 0.9 # for heu

    def main(self, environment):
        iter_result_list, iter_rel_num_list, iter_bp_num_lsit = [], [], []
        for epoch in range(self.iteration):
            start_time = time.time()
            print(f'\n---iteration:{epoch}---')
            print(f'alpha:{self.alpha}\nbeta: {self.beta}')

            best_iter_result, best_iter_rel_num, best_iter_bp_num = math.inf, -1, -1
            iter_reward = np.zeros((self.M, self.rel_per_stage, self.S, self.S))
            for a in range(self.ant_number):

                ant_steps, ant_result, ant_step_heu, ant_bp_num = self._ant_search(copy.deepcopy(environment))
                best_iter_result = min(best_iter_result, ant_result)
                best_iter_rel_num = len(ant_steps)
                best_iter_bp_num = ant_bp_num
                # phenomone reward
                if max(ant_step_heu) == min(ant_step_heu):
                    modified_ant_step_heu = [1/len(ant_step_heu) for _ in ant_step_heu]
                else:
                    modified_ant_step_heu = [i - min(ant_step_heu)/(max(ant_step_heu) - min(ant_step_heu)) for i in ant_step_heu]
                for i, step in enumerate(ant_steps):
                    iter_reward[step[0], step[1], step[2], step[3]] += \
                           self.lambdas * max(0, self.baseLine - ant_result) * modified_ant_step_heu[i] / sum(modified_ant_step_heu)
            iter_result_list.append(best_iter_result)
            iter_rel_num_list.append(best_iter_rel_num)
            iter_bp_num_lsit.append(best_iter_bp_num)
            print(f'results:\n  iter result:  {best_iter_result}\n  global result:{min(iter_result_list)}')

            self.phe = self.weight_decay * self.phe + iter_reward
            self._update_heuPhe_ratio(epoch)
            print('iter time', time.time() - start_time)
            print('iter result', best_iter_result)
            print('iter relocation time', best_iter_rel_num)
            print('iter bp number', best_iter_bp_num)
        return iter_result_list, iter_rel_num_list, iter_bp_num_lsit

    def _ant_search(self, environment):
        steps, heus = [], []
        stage, rel_index, done = 0, 0, 0

        valid_time, heu_time, phe_time, get_action_time, step_time, get_rel_time, step_time1 = 0, 0, 0, 0, 0, 0, 0

        # start_time = time.time()
        while not done:
            mask = environment.get_valid_rel()
            heu = environment.get_heuristic_value()
            phe = self.phe[stage, rel_index, :].flatten()
            action_index = self._get_action(phe, heu, mask)

            s1, s2 = self._action_index_to_stack(action_index)
            steps.append([stage, rel_index, s1, s2])

            stage, rel_index, done, action_heu = environment.aco_step(stage, rel_index, s1, s2)
            heus.append(action_heu)
        # print('ant step time:', time.time() - start_time)

        result = environment.get_relocation()
        bp_num = environment.get_bp_num()
        # print('ant result calculate time:', time.time() - start_time)
        return steps, result, heus, bp_num
    def _action_index_to_stack(self, action_index):
        '''
        from index ranging from  0-S^2 to relocation stack s1 and s2
        :param action_index: int, from 0-S^2
        :return: outbound stack s1 and in stack s2
        '''
        s1 = math.floor(action_index/self.S)
        s2 = action_index - s1 * self.S
        return int(s1), int(s2)

    def _get_action(self, phe, heu, mask):
        if np.max(phe) == np.min(phe):
            nor_phe = np.ones(self.S**2)
        else:
            nor_phe = (phe - np.min(phe)) / (np.max(phe) - np.min(phe))
        if np.max(heu) == np.min(heu):
            nor_heu = np.ones(self.S**2)
        else:
            nor_heu = (heu - np.min(heu)) / (np.max(heu) - np.min(heu))
        pro = ((nor_phe ** self.alpha) + (nor_heu ** self.beta))*mask
        nor_pro = pro / np.sum(pro)
        return np.random.choice(a=self.S**2, p=nor_pro)

    def _update_heuPhe_ratio(self, i):
        self.beta = 0.9 - 0.8 *i / self.iteration
        self.alpha = 1 - self.beta


if __name__ == '__main__':
    pass
