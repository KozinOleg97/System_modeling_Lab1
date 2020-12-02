import math
import operator
import random

import numpy as np
import re
import sys

'''
Полумарковский процесс (?)

Входные данные: 
    stah_matrix - вероятности переходов 
    stah_vector - вероятности переходов для старта
    
    ### Определяют время перехода ###
    time_matrix - типы переходов  
    time_param_matrix - параметры переходов 
    start_time - типы переходов (для старта)
    start_param - параметры переходов (для старта)
    
    1 - Константа
    2 - Экспоненте. распред.
'''


class H_mark_sys:
    start_vector = []
    start_time = []
    stah_matrix = []
    time_matrix = []

    jump_counter = 0

    state_data = []

    def __init__(self, start_vector, start_time, stah_matrix, time_matrix, start_time_params, time_params_matrix,
                 folder, experement_name):

        self.experement_name = experement_name

        self.f = open(experement_name + "_steps_Out.txt", 'w')

        self.out_data_raw = ""
        self.out_state_data = ""
        self.start_vector = self.read_matr(folder + start_vector)

        self.start_time = self.read_matr(folder + start_time)

        self.stah_matrix = self.read_matr(folder + stah_matrix)

        self.time_matrix = self.read_matr(folder + time_matrix)

        self.start_time_param = self.read_param(folder + start_time_params)
        self.time_param_matrix = self.read_param(folder + time_params_matrix)

        # СОздаём матрицу для статистики переходов
        self.statistic_matr = np.zeros((len(self.stah_matrix), len(self.stah_matrix[0])))

    def read_matr(self, filename):
        matr = []

        with open(filename) as f:
            for line in f:
                matr.append([float(x) for x in line.split()])
        return matr

    # Для чтения параметров зла задания случ величины
    def read_param(self, filename):
        matr = []

        with open(filename) as f:
            for line in f:
                matr.append([float(x) for x in re.split(";| ", line)])
        return matr

    def vectorToArray(self, vector):
        return np.hstack(vector)

    def rnd_choice(self, array):
        # array = self.vectorToArray(vector)
        summ = sum(array)
        if summ < 1:
            array[0] += 1 - summ

        summ = sum(array)

        choice_index = np.random.choice(a=len(array), p=array, replace=False)

        return choice_index

        pass

    def start(self, iter):
        cur_variants = self.vectorToArray(self.start_vector)
        cur_times = self.vectorToArray(self.start_time)
        cur_state_index = -1

        action_timer = 0
        # first(initial) step
        new_state_index = self.rnd_choice(cur_variants)
        jump_time = self.jump(cur_state_index, new_state_index, cur_times[new_state_index])

        action_timer = jump_time

        for i in range(iter):

            if action_timer < 0.001:
                # old output
                self.write_jump(index=i, stah=cur_variants, new_state=new_state_index, time=jump_time,
                                old_state=cur_state_index, exp_name=self.experement_name)
                # step
                cur_variants = self.vectorToArray(self.stah_matrix[new_state_index])
                cur_times = self.vectorToArray(self.time_matrix[new_state_index])

                cur_state_index = new_state_index

                # calc new step
                new_state_index = self.rnd_choice(cur_variants)
                jump_time = self.jump(cur_state_index, new_state_index, cur_times[new_state_index])

                action_timer = jump_time

            self.save_state(cur_state_index + 1)

            action_timer = action_timer - 0.001

        # close console file

        self.print_result(iter)
        self.save_data_file(self.experement_name)
        self.f.close()
        pass

    def write_jump(self, index, stah, new_state, time, old_state, exp_name):
        self.statistic_matr[old_state][new_state] += 1

        self.f.write(' '.join(
            ("Шаг № ", str(self.jump_counter + 1), "\t", "В момент времени: ", str(index + 1), "\t", str(old_state + 1),
             " -> ",
             str(new_state + 1), "\tЗа время",
             str(np.around(float(time), decimals=3)),
             "\t", "Вероятности", str(stah), "\n")))
        """    
        print("Шаг № ", self.jump_counter + 1, "\t", "В момент времени: ", index + 1, "\t", old_state + 1, " -> ",
              new_state + 1, "\tЗа время",
              np.around(float(time), decimals=3),
              "\t", "Вероятности", stah)
        """
        # write to file old way
        # temp = self.log_jump(index, stah, new_state, time, old_state, self.jump_counter)
        # self.out_data_raw += temp
        self.jump_counter = self.jump_counter + 1

    def log_jump(self, index, stah, new_state, time, old_state, jump_numb):
        s = "" + str(index + 1) + "\t" + str(old_state + 1) + "\t" + str(new_state + 1) + "\t" + str(
            np.around(float(time), decimals=3)) + "\n"
        return s

    def print_result(self, iter=-1):
        print(self.statistic_matr)
        print("Проверка ", int(np.sum(self.statistic_matr)), " = ", iter)

    # Определяет время прыжка, сначала тип, затем параметры(передаёт)
    def jump(self, cur_state_index, new_state_index, cur_times):
        # Если из стартового положения
        if cur_state_index == -1:
            # константа
            if cur_times == 1:
                return self.start_time_param[new_state_index][0]
            # Експоненциальное распред
            elif cur_times == 2:
                return self.exp_rnd(self.start_time_param[new_state_index])

        # Если не из стартового
        if cur_times == 1:
            return self.time_param_matrix[cur_state_index][new_state_index]
        elif cur_times == 2:
            return self.exp_rnd(self.time_param_matrix[cur_state_index][new_state_index])

        return -1

    def exp_rnd(self, data):
        if type(data) == list:
            data = data[0]
        return random.expovariate(data)

    def save_data_file(self, exp_name):
        my_file = open(exp_name + "_state_raw_OUT.txt", "w")
        for line in self.state_data:
            my_file.write(line)

        my_file.close()

    def save_state(self, state):
        # s = str(state) + "\n"
        # return s
        self.state_data.append(str(state) + "\n")


# ********************************

#номер эксперемента = название файла
experement_numb = "4"

stah_matrix = "matrix_" + experement_numb + ".txt"
stah_vector = "start_vector_" + experement_numb + ".txt"

### Определяют время перехода ###
time_matrix = "time_matrix_" + experement_numb + ".txt"
time_param_matrix = "time_param_matrix_" + experement_numb + ".txt"
start_time = "start_time_" + experement_numb + ".txt"
start_param = "start_time_param_" + experement_numb + ".txt"
###########################################


# 1 iteration = 0.00001 sec
number_of_iteration = 1000000

try:
    sys = H_mark_sys(stah_matrix=stah_matrix,
                     start_vector=stah_vector,
                     time_matrix=time_matrix,
                     time_params_matrix=time_param_matrix,
                     start_time=start_time,
                     start_time_params=start_param,
                     folder="data/",
                     experement_name="exp" + experement_numb)
    sys.start(iter=number_of_iteration)
except FileNotFoundError as err:
    sys = H_mark_sys(stah_matrix=stah_matrix,
                     start_vector=stah_vector,
                     time_matrix=time_matrix,
                     time_params_matrix=time_param_matrix,
                     start_time=start_time,
                     start_time_params=start_param,
                     folder="dist/data/",
                     experement_name="exp" + experement_numb)
    sys.start(iter=number_of_iteration)
