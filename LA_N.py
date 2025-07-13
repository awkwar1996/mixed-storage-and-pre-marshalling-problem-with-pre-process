import copy
import math
import time
# from Utiles import load_data
'''
Calculate RS by LA-N algorithm from [1]

[1]Petering, M. E., & Hussein, M. I. (2013). A new mixed integer program and extended look-ahead heuristic algorithm 
for the block relocation problem. European Journal of Operational Research, 231(1), 120-130.
'''


def extended_LA(allocation, S, H, P):
    N = sum([len(allocation[s]) for s in range(S)])
    plateNum = [0 for p in range(P)]
    for stack in allocation:
        for plate in stack:
            plateNum[plate - 1] += 1
    plate_index = [sum(plateNum[:i]) for i in range(P)]
    #1.确定出库顺序
    allocation_outbound_version = [[-1 for i in range(len(allocation[s]))] for s in range(S)]
    for h in range(H)[::-1]:
        for s in range(S):
            if len(allocation[s]) >= h + 1:
                allocation_outbound_version[s][h] = plate_index[allocation[s][h] - 1]
                plate_index[allocation[s][h] - 1] += 1

    n, relocation_number = 0, 0
    while n <= N - 1:
        #1.找到出库钢板
        for s in range(S):
            if n in allocation_outbound_version[s]:
                target_stack = s
                break
        #2. 确定N
        look_ahdead_N = S - 1
        #3. 如果出库钢板就是第一个钢板，则直接提取
        if allocation_outbound_version[target_stack][-1] == n:
            allocation_outbound_version[target_stack].pop()
            n += 1
            continue
        #4.修正N,初始化r
        look_ahdead_N1 = min(N - n, look_ahdead_N)
        r = 0
        #更新N1
        while is_N1_ok(allocation_outbound_version, look_ahdead_N1, n, H, S) == False:
            look_ahdead_N1 -= 1
        #确定top钢板集合
        Stacks = Stacks_N1(allocation_outbound_version, look_ahdead_N1, n, S)
        Top_r_Stacks_N1 = []
        stack_location = {}
        for stack in Stacks:
            plate = allocation_outbound_version[stack][-1]
            Top_r_Stacks_N1.append(plate)
            stack_location[plate] = stack
        sorted_Top_r_Stacks_N1 = sorted(Top_r_Stacks_N1)[::-1]
        #确定翻板钢板
        while True:
            relocated_plate = sorted_Top_r_Stacks_N1[r]
            if stack_location[relocated_plate] == target_stack: break
            if len(E(allocation_outbound_version, relocated_plate, stack_location, H,n,S)) > 0 and min(allocation_outbound_version[stack_location[relocated_plate]]) < relocated_plate:
                break
            r += 1
        #确定落位堆位
        well_relocation_set, bad_relocation_set = D(allocation_outbound_version, S, relocated_plate, H, n)
        if len(well_relocation_set) == 0:
            low_n = -math.inf
            for stack in bad_relocation_set:
                if min(allocation_outbound_version[stack]) > low_n:
                    relocation_stack, low_n = stack, min(allocation_outbound_version[stack])
        else:
            low_n = math.inf
            for stack in well_relocation_set:
                if len(allocation_outbound_version[stack]) == 0:
                    if low_n == math.inf:
                        relocation_stack = stack
                elif min(allocation_outbound_version[stack]) < low_n:
                    relocation_stack, low_n = stack, min(allocation_outbound_version[stack])
        allocation_outbound_version[relocation_stack].append(allocation_outbound_version[stack_location[relocated_plate]].pop())
        relocation_number += 1

    return relocation_number
def D(allocation, S, n, H, target_plate):
    a = [s for s in range(S)]
    b = []
    for s in range(S):
        if n in allocation[s] or len(allocation[s]) == H or target_plate in allocation[s]:
            a.remove(s)
            continue
        if len(allocation[s]) == 0 or min(allocation[s]) > n:
            b.append(s)
            a.remove(s)
    return b, a
def E(allocation, n, dict1,H, target_plate, S):
    a = []
    for s in range(S):
        if s == dict1[n] or len(allocation[s]) == H or target_plate in allocation[s]: continue
        if len(allocation[s]) == 0 or min(allocation[s]) > n:
            a.append(s)
    return a
def Stacks_N1(allocation, N1, n, S):
    Stacks = []
    for s in range(S):
        if len(allocation[s]) == 0: continue
        if min(allocation[s]) <= n + N1 - 1:
            Stacks.append(s)
    return Stacks
def is_N1_ok(allocation, N1, n, H, S):
    Stacks = Stacks_N1(allocation, N1, n, S)
    other_stacks = set([i for i in range(S)]) - set(Stacks)
    if len(other_stacks) == 0:
        return False

    for stack in other_stacks:
        if len(allocation[stack]) < H: return True
    return False




def extended_LA_for_heu(allocation, S, H):
    '''
    Used to find the clue for relocation
    :param allocation:
    :param S:
    :param H:
    :return:
    '''
    N = sum([len(allocation[s]) for s in range(S)])
    #1.确定出库顺序
    allocation_outbound_version = [[-1 for i in range(len(allocation[s]))] for s in range(S)]
    decided_location = []

    # 给各个板编号
    n = 0
    while n <= N - 1:
        min_group, max_height, min_stack = math.inf, -1, math.inf
        for h in range(H)[::-1]:
            for s in range(S):
                if len(allocation[s]) >= h + 1 and (s,h) not in decided_location and allocation[s][h] < min_group:
                    min_group, max_height, min_stack = allocation[s][h], h, s
        allocation_outbound_version[min_stack][max_height] = n
        decided_location.append((min_stack, max_height))
        n += 1
    index_config = copy.deepcopy(allocation_outbound_version)

    n = 0
    relocated_time = {}
    while n <= N - 1:
        #1.找到出库钢板
        for s in range(S):
            if n in allocation_outbound_version[s]:
                target_stack = s
                break
        #2. 确定N
        look_ahdead_N = S - 1
        #3. 如果出库钢板就是第一个钢板，则直接提取
        if allocation_outbound_version[target_stack][-1] == n:
            allocation_outbound_version[target_stack].pop()
            n += 1
            continue
        #4.修正N,初始化r
        look_ahdead_N1 = min(N - n, look_ahdead_N)
        r = 0
        #更新N1
        while is_N1_ok(allocation_outbound_version, look_ahdead_N1, n, H, S) == False:
            look_ahdead_N1 -= 1
        #确定top钢板集合
        Stacks = Stacks_N1(allocation_outbound_version, look_ahdead_N1, n, S)
        Top_r_Stacks_N1 = []
        stack_location = {}
        for stack in Stacks:
            plate = allocation_outbound_version[stack][-1]
            Top_r_Stacks_N1.append(plate)
            stack_location[plate] = stack
        sorted_Top_r_Stacks_N1 = sorted(Top_r_Stacks_N1)[::-1]
        #确定翻板钢板
        while True:
            relocated_plate = sorted_Top_r_Stacks_N1[r]
            if stack_location[relocated_plate] == target_stack: break
            if len(E(allocation_outbound_version, relocated_plate, stack_location, H,n,S)) > 0 and min(allocation_outbound_version[stack_location[relocated_plate]]) < relocated_plate:
                break
            r += 1
        #确定落位堆位
        well_relocation_set, bad_relocation_set = D(allocation_outbound_version, S, relocated_plate, H, n)
        if len(well_relocation_set) == 0:
            low_n = -math.inf
            for stack in bad_relocation_set:
                if min(allocation_outbound_version[stack]) > low_n:
                    relocation_stack, low_n = stack, min(allocation_outbound_version[stack])
        else:
            low_n = math.inf
            for stack in well_relocation_set:
                if len(allocation_outbound_version[stack]) == 0:
                    if low_n == math.inf:
                        relocation_stack = stack
                elif min(allocation_outbound_version[stack]) < low_n:
                    relocation_stack, low_n = stack, min(allocation_outbound_version[stack])
        allocation_outbound_version[relocation_stack].append(allocation_outbound_version[stack_location[relocated_plate]].pop())
        if relocated_plate not in relocated_time.keys():
            relocated_time[relocated_plate] = 1
        else:
            relocated_time[relocated_plate] += 1

    relocated_map = []
    for s in range(S):
        temp = []
        for h in range(len(index_config[s])):
            if index_config[s][h] not in relocated_time.keys():
                temp.append(0)
            else:
                temp.append(relocated_time[index_config[s][h]])
        relocated_map.append(temp)
    return relocated_map
if __name__ == "__main__":
    # S, H, _, _, _, storage_configuration, _ = load_data('data_example1.xlsx')

    relocated_map = extended_LA1(storage_configuration, S, H)
    print('hello')

