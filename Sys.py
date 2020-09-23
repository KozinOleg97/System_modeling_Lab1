import math
import operator
import random

import numpy as np
import re


class H_mark_sys:
    start_vector = []
    start_time = []
    stah_matrix = []
    time_matrix = []

    def __init__(self, start_vector, start_time, stah_matrix, time_matrix, start_time_params, time_params_matrix):
        self.start_vector = self.read_matr(start_vector)

        self.start_time = self.read_matr(start_time)

        self.stah_matrix = self.read_matr(stah_matrix)

        self.time_matrix = self.read_matr(time_matrix)

        self.start_time_param = self.read_param(start_time_params)
        self.time_param_matrix = self.read_param(time_params_matrix)

        # СОздаём матрицу для статистики переходов
        self.statistic_matr = np.zeros((len(self.stah_matrix), len(self.stah_matrix[0])))

    def read_matr(self, filename):
        matr = []
        with open(filename) as f:
            for line in f:
                # re.split('; |, ', str)
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

        for i in range(iter):
            new_state_index = self.rnd_choice(cur_variants)
            jump_time = self.jump(cur_state_index, new_state_index, cur_times[new_state_index])

            self.write_jump(index=i, stah=cur_variants, new_state=new_state_index, time=jump_time,
                            old_state=cur_state_index)

            cur_variants = self.vectorToArray(self.stah_matrix[new_state_index])
            cur_times = self.vectorToArray(self.time_matrix[new_state_index])

            cur_state_index = new_state_index

        self.print_result(iter)
        pass

    def write_jump(self, index, stah, new_state, time, old_state):

        self.statistic_matr[old_state][new_state] += 1

        print("Шаг: ", index + 1, "\t", old_state + 1, " -> ", new_state + 1, "\tЗа время",
              np.around(float(time), decimals=3),
              "\t", "Вероятности", stah)

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


# ********************************

sys = H_mark_sys("start_vector_1.txt", "start_time_1.txt", "matrix_1.txt", "time_matrix_1.txt",
                 "start_time_param_1.txt",
                 "time_param_matrix_1.txt")

sys.start(iter=1000)

# mas = [0, 0, 0]
# for i in range(100000):
#     choice_index = sys.rnd_choice(sys.start_vector)
#     mas[choice_index] += 1
input()
pass
