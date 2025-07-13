#!/usr/bin/env/python
import copy
import math
import os
from ACO_Jovanovic import ACO_Jovanovic
from Utiles import parameter_setting, load_data, save_result2
from Environment_Jovanovic import Environment_Jovanovic
import time

if __name__ == '__main__':
    settings = parameter_setting()
    instances_files = os.listdir('instance/1')
    for file_name in instances_files:
        print(f'------------{file_name}------------')
        # M, mean, std = int(file_name[1:3]), int(file_name[7:9]), int(file_name[12])
        S, H, M, N_i, P, inbound_plates, preprocess_time, config, operate_time, min_operate_time = load_data(f'instance/1/{file_name}')
        env = Environment_Jovanovic(
            S=S,
            H=H,
            M=M,
            P=P,
            inbound_plate=inbound_plates,
            preprocess_time=preprocess_time,
            configuration=config,
            operate_time=operate_time
        )
        aco = ACO_Jovanovic(
            S=S,
            M=M,
            baseLine=env.relocation_baseLine,
            settings=settings,
            rel_per_stage=math.ceil(max(preprocess_time)/min_operate_time),
            instance_name=file_name
        )
        start_time = time.time()
        iter_result_list, iter_relTime_list, iter_bp_num_list = aco.main(copy.deepcopy(env))
        end_time = time.time()
        save_result2(iter_result_list, iter_relTime_list, iter_bp_num_list, f'result/aco_jovanovic/{file_name}', end_time - start_time)
        print(iter_result_list)

        del S, H, M, N_i, P, inbound_plates, preprocess_time, config, operate_time, min_operate_time
        del env, aco
        del iter_result_list, iter_relTime_list, iter_bp_num_list
