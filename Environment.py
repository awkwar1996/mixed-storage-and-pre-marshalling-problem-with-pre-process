import copy
import random
import time
from itertools import product
from LA_N import extended_LA
import numpy as np
import torch
import math

'''
Class of Environment
'''


class Environment:
    def __init__(self, S, H, M, P, inbound_plate, preprocess_time, configuration, operate_time):
        # 参数
        self.S = S
        self.H = H
        self.M = M
        self.operate_time = operate_time
        self.N = sum([len(configuration[s]) for s in range(S)]) + len(inbound_plate)
        self.P = P

        # 初始时刻量
        self.crane_location = 0
        self.inbound_plate = inbound_plate
        self.preprocess_time = preprocess_time
        self.configuration = configuration
        self.plateNum_in_group = self._calculate_plateNum_in_groups()

        # relocation baseline
        self.relocation_baseLine = self._get_relocation_baseLine()
        print(f'relocation baseline:{self.relocation_baseLine}')
        # valid relocation matrix
        self.valid_rel = self._set_valid_rel()
        # heuristic matrix
        self.heuristic_value = np.zeros((self.S, self.S))
        self._update_heuristic_value()

    def _calculate_plateNum_in_groups(self):
        '''
        calculate the number of stored plates in each group
        :return: a list showing the number of stored plates in each group
        '''
        plateNum_in_group = [0 for p in range(self.P)]
        for stack in self.configuration:
            for plate in stack:
                plateNum_in_group[plate - 1] += 1
        return plateNum_in_group

    def _get_relocation_baseLine(self):
        '''
        the base outbound relocation number, assuming that each plate is stored in the stacks with the least index.
        :return: outbound relocation number
        '''
        configuration = copy.deepcopy(self.configuration)
        inbound_plate = copy.deepcopy(self.inbound_plate)
        while len(inbound_plate) > 0:
            plate = inbound_plate.pop(0)
            for s in range(self.S):
                if len(configuration[s]) < self.H:
                    configuration[s].append(plate)
                    break
        return extended_LA(configuration, self.S, self.H, self.P)

    def _get_stack_group(self, stack):
        if len(stack) == 0: return self.P
        return min(stack)

    def _heuristic_value_for_action(self, s1, s2):
        '''
        return the heuristic value for the action when the top plate of stack s1 is relocated to stack s2
        :param s1:
        :param s2:
        :return: the heuristic value for the action
        '''

        if self.valid_rel[s1, s2] == 0:
            return -1

        # check the type of relocation
        group = self.configuration[s1][-1]
        well_located_in_s1, well_located_in_s2 = False, False
        stack_group1 = self._get_stack_group(self.configuration[s1])
        stack_group2 = self._get_stack_group(self.configuration[s2])
        if group == stack_group1: well_located_in_s1 = True
        if group <= stack_group2: well_located_in_s2 = True

        # set heuristic value for each type of relocation
        # B-B
        if well_located_in_s1 == False and well_located_in_s2 == False:
            plateNum_in_group1 = sum(self.plateNum_in_group[stack_group1:group - 1])
            plateNum_in_group2 = sum(self.plateNum_in_group[stack_group2:group - 1])
            return 1.816 * self.P * (stack_group1 - stack_group2) + 0.083 * self.S * (plateNum_in_group1 - plateNum_in_group2)
        # B-G
        if well_located_in_s1 == False and well_located_in_s2 == True:
            plateNum_in_group = sum(self.plateNum_in_group[1:self.P - 2])
            return 1.816 * self.P * (self.P - 1) + 0.083 * self.S * plateNum_in_group + 10 * (stack_group2 - group)
        #G-B
        if well_located_in_s1 == True and well_located_in_s2 == False:
            plateNum_in_group = sum(self.plateNum_in_group[1:self.P - 2])
            return -1.816 * self.P * (self.P - 1) - 0.083 * self.S * plateNum_in_group - 10 * (stack_group1 - stack_group2)
        #G-G
        plateNum_in_group1 = sum(self.plateNum_in_group[stack_group1:group - 1])
        plateNum_in_group2 = sum(self.plateNum_in_group[stack_group2:group - 1])
        return (1.816 * self.P + 1) * (stack_group1 - stack_group2) + 0.083 * self.S * (plateNum_in_group1 - plateNum_in_group2)

    def _update_heuristic_value(self, s1=-1, s2=-1):
        if s1 ==-1 and s2 ==-1:
            for i, j in product(range(self.S), range(self.S)):
                self.heuristic_value[i, j] = self._heuristic_value_for_action(i, j)
        else:
            for s in range(self.S):
                if s != s1 and s != s2:
                    self.heuristic_value[s, s1] = self._heuristic_value_for_action(s, s1)
                    self.heuristic_value[s1, s] = self._heuristic_value_for_action(s1, s)
                    self.heuristic_value[s, s2] = self._heuristic_value_for_action(s, s2)
                    self.heuristic_value[s2, s] = self._heuristic_value_for_action(s2, s)

    def get_heuristic_value(self):
        return self.heuristic_value.flatten()

    def _set_valid_rel(self, s1 = -1, s2 = -1):
        '''
        set valid relocation set
        :param s1:
        :param s2:
        :return:
        '''
        # s1=s2=-1, initialize
        if s1 == s2 == -1:
            valid_rel = np.ones((self.S, self.S))
            for i in range(self.S):
                if len(self.configuration[i]) == 0:
                    valid_rel[i] = np.array([0 for _ in range(self.S)])
                elif len(self.configuration[i]) == self.H:
                    valid_rel[:, i] = np.array([0 for _ in range(self.S)])
                valid_rel[i, i] = 0
            return valid_rel

        # for s1, can move in. If empty, cannot move out
        if s1 != -1:
            for s in range(self.S):
                if not (len(self.configuration[s]) == 0 or s == s1):
                    self.valid_rel[s, s1] = 1
            if len(self.configuration[s1]) == 0:
                self.valid_rel[s1] = np.array([0 for _ in range(self.S)])
        # for s2, can move out. If full, cannot move in
        if s2 != -1:
            self.valid_rel[s2] = np.array([0 for _ in range(self.S)])
            if len(self.configuration[s2]) == self.H:
                self.valid_rel[:, s2] = np.array([0 for _ in range(self.S)])
        return True

    def get_valid_rel(self):
        '''
        get the valid move, and made it to the mask
        return: (torch.tensor)
        '''
        # for s in range(self.S):
        #     print(self.configuration[s])
        # print('valid rel:\n',self.valid_rel)
        return self.valid_rel.flatten()

    def get_relocation(self):
        '''
        return outbound relocation for the configuration
        :return:
        '''

        return extended_LA(self.configuration, self.S, self.H, self.P)

    def get_bp_num(self):
        num = 0
        for stack in self.configuration:
            if len(stack) <= 1: continue
            min_plate = math.inf
            for plate in stack:
                if plate < min_plate: min_plate = plate
                elif plate > min_plate: num += 1
        return num
    def _get_inbound_location(self, plate):
        well_relocation, u, stack = False, math.inf, -1
        for s in range(self.S):
            if len(self.configuration[s]) == self.H:
                continue

            stack_group = self._get_stack_group(self.configuration[s])
            # not chosen
            if stack == -1:
                stack = s
                if stack_group >= plate:
                    well_relocation = True
                else:
                    plateNum_in_group = sum(self.plateNum_in_group[stack_group:plate - 1])
                    u = 1.816 * self.P * (plate - stack_group) + 0.083 * self.S * plateNum_in_group
            # former chosen stack is not good while the new one is good
            elif stack_group >= plate and not well_relocation:
                stack = s
                well_relocation = True
            #former chosen stack and the new one are all good
            elif stack_group >= plate and well_relocation:
                if stack_group < self._get_stack_group(self.configuration[stack]):
                    stack = s
            # former chosen stack and the new one are all not good
            elif stack_group < plate and not well_relocation:
                plateNum_in_group = sum(self.plateNum_in_group[stack_group:plate - 1])
                u1 = 1.816 * self.P * (plate - stack_group) + 0.083 * self.S * plateNum_in_group
                if u1 < u:
                    u, stack = u1, s
        return stack

    def aco_step(self, stage, rel_index, s1, s2):
        # print(f's1={s1},s2={s2}')
        # for stack in self.configuration:
        #     print(stack)
        # print(self.valid_rel)
        # 1.通过action，得到起始和落位堆位
        heu_val = self.heuristic_value[s1, s2]
        # 2.翻板
        self.configuration[s2].append(self.configuration[s1].pop())
        operate_time = self.operate_time[self.crane_location, s1 + 1, s2 + 1]# in move time s=0 is the exit
        self.crane_location = s2+1

        for ix in range(len(self.preprocess_time)):
            self.preprocess_time[ix], operate_time = max(0, self.preprocess_time[ix] - operate_time), max(
                operate_time - self.preprocess_time[ix], 0)
            if operate_time == 0:
                break
        # update heuristic value and valid set
        self._set_valid_rel(s1, s2)
        self._update_heuristic_value(s1, s2)

        # 3.如果可以入库，进行入库操作
        if 0 in self.preprocess_time:
            # 3.1，确定入库钢板
            plate, _ = self.inbound_plate.pop(0), self.preprocess_time.pop(0)
            # 3.2.确定存储堆位
            stack = self._get_inbound_location(plate)
            self.configuration[stack].append(plate)
            # 3.3.确定移动时间
            operate_time = self.operate_time[self.crane_location, 0, stack + 1]
            self.crane_location = stack + 1
            for ix in range(len(self.preprocess_time)):
                self.preprocess_time[ix], operate_time = max(0, self.preprocess_time[ix] - operate_time), max(
                    operate_time - self.preprocess_time[ix], 0)
                if operate_time == 0:
                    break

            self.plateNum_in_group[plate - 1] += 1
            # update heuristic value and valid set
            self._set_valid_rel(-1, stack)
            self._update_heuristic_value()
            return stage + 1, 0, len(self.inbound_plate) == 0, heu_val
        else:
            return stage, rel_index + 1, len(self.inbound_plate) == 0, heu_val

    def action_ok(self, s1, s2):
        if self.valid_rel[s1, s2] == 1:
            return True
        return False

    def ga_step(self, s1, s2):
        # 2.翻板
        self.configuration[s2].append(self.configuration[s1].pop())
        operate_time = self.operate_time[self.crane_location, s1 + 1, s2 + 1]  # in move time s=0 is the exit
        self.crane_location = s2 + 1

        for ix in range(len(self.preprocess_time)):
            self.preprocess_time[ix], operate_time = max(0, self.preprocess_time[ix] - operate_time), max(
                operate_time - self.preprocess_time[ix], 0)
            if operate_time == 0:
                break

        self._set_valid_rel(s1, s2)

        # 3.如果可以入库，进行入库操作
        if 0 in self.preprocess_time:
            # 3.1，确定入库钢板
            plate, _ = self.inbound_plate.pop(0), self.preprocess_time.pop(0)
            # 3.2.确定存储堆位
            stack = self._get_inbound_location(plate)
            self.configuration[stack].append(plate)
            # 3.3.确定移动时间
            operate_time = self.operate_time[self.crane_location, 0, stack + 1]
            self.crane_location = stack + 1
            for ix in range(len(self.preprocess_time)):
                self.preprocess_time[ix], operate_time = max(0, self.preprocess_time[ix] - operate_time), max(
                    operate_time - self.preprocess_time[ix], 0)
                if operate_time == 0:
                    break
            # update heuristic value and valid set
            self._set_valid_rel(-1, stack)

        return len(self.inbound_plate) == 0