from PyQt5.QtWidgets import QInputDialog
from zjdm import *


def jsq(s, four):  # 分析四元式，运算结果
    end_res = ''
    va = {}
    for i in range(1000):
        va[str(i)] = i
        va[i] = i

    index = 0
    # now = 0

    while True:
        if s[index][0] == 'sys' or index == len(s) - 1:
            break
        elif s[index][0] == 'call' and s[index][1] == 'read':
            va[s[index][3]] = four
        elif s[index][0] == 'call' and s[index][1] == 'write':
            end_res += str(va[s[index][3]]) + '\n'
        elif s[index][0] == '+':
            va[s[index][3]] = int(va[s[index][1]]) + int(va[s[index][2]])
        elif s[index][0] == '-':
            va[s[index][3]] = int(va[s[index][1]]) - int(va[s[index][2]])
        elif s[index][0] == '*':
            va[s[index][3]] = int(va[s[index][1]]) * int(va[s[index][2]])
        elif s[index][0] == '/':
            va[s[index][3]] = int(va[s[index][1]]) / int(va[s[index][2]])
        elif s[index][0] == '%':
            va[s[index][3]] = int(va[s[index][1]]) % int(va[s[index][2]])
        elif s[index][0] == '=':
            va[s[index][3]] = int(va[s[index][1]])

        elif s[index][0][0] == 'J':
            if len(s[index][0]) == 1:
                index = int(s[index][3]) - 1

            elif s[index][0][1:] == '>=':
                if int(va[s[index][1]]) >= int(va[s[index][2]]):
                    index = int(s[index][3]) - 1
            elif s[index][0][1:] == '<=':
                if int(va[s[index][1]]) <= int(va[s[index][2]]):
                    index = int(s[index][3]) - 1
            elif s[index][0][1] == '>':
                if int(va[s[index][1]]) > int(va[s[index][2]]):
                    index = int(s[index][3]) - 1
            elif s[index][0][1] == '<':
                if int(va[s[index][1]]) < int(va[s[index][2]]):
                    index = int(s[index][3]) - 1
            elif s[index][0][1:] == '==':
                if int(va[s[index][1]]) == int(va[s[index][2]]):
                    index = int(s[index][3]) - 1
            elif s[index][0][1:] == '!=':
                if int(va[s[index][1]]) != int(va[s[index][2]]):
                    index = int(s[index][3]) - 1
        index = index + 1
    return end_res


if __name__ == '__main__':
    syner = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/zjdm_example/test0.1.txt")
    syner.run()
    quaternion_list = enumerate(syner.quaternary_list)
    for i, k in enumerate(syner.quaternary_list):
        quaternion_list = k
    # go_run(self, quaternion_list)
