from lexical import recognizedID
from syntax import get_syntax_result, function_param_list
from zjdm import Zjdmsc

global_main_symbol = []  # 存放变量
function = {}  # 除main函数外其他函数里参数 以及对应的ss:[bp+n]， 局部变量  以及对应的ss:[bp-n]     sub sp n    n的值为局部变量个数*2


# {函数1：[]，函数2：[]}                 #  n=参数个数*2+2  [{参数1：'ss:[bp+n]',参数2:'ss:[bp+n-2]'...} ,{局部变量1:'ss:[bp-2]',
# 局部变量2:'ss:[bp-2-2]'}]

def is_var(s):
    state = '0'
    for ch in s:
        if state == '0':
            if ch.isalpha() or ch == '_':
                state = '1'
            else:
                return False
        elif state == '1':
            if ch.isalnum() or ch == '_':
                state = '1'
            else:
                return False
    return True


# 获取
def function_get(quaternion_list):
    sys = quaternion_list.index(['sys', '_', '_', '_'])
    for i, v in function_param_list.items():
        function[i] = [{}, {}]
        for j in v:
            function[i][0][j] = '_'
    for i, line in enumerate(quaternion_list[1:sys + 1:]):
        if line[0] not in ['jnz', 'para', 'call', 'j', 'jz']:
            for var in line[1:]:
                if is_var(var) and var not in global_main_symbol + ['_']:
                    global_main_symbol.append(var)
    fun_list = []
    for i, line in enumerate(quaternion_list[sys + 1:]):
        if line[0] != 'ret' and line[1] == line[2] == line[3] == '_':
            fun_list.append(line[0])
    for i in range(len(fun_list)):
        for variable in symbol_variable_list.keys():
            for var in symbol_variable_list[variable].keys():
                if len(var.split('/')) > 2 and var.split('/')[2] == str(i + 2):
                    function[fun_list[i]][1][variable] = '_'
    for i, v in function.items():
        n = (len(function[i][0]) + len(function[i][1])) * 2
        for s, vv in enumerate(function[i][0].keys()):
            function[i][0][vv] = 'ss:[bp+' + str(n - (s * 2)) + ']'
        for s, vv in enumerate(function[i][1].keys()):
            function[i][1][vv] = 'ss:[bp-' + str(2 + (s * 2)) + ']'


def target_code(four_table):
    global s
    global fun_name  # 根据中间代码来确定当前执行的函数名
    fun_name = '**'
    f = open('C:/Users/YL139/Desktop/byyl/test/byxt/data_segment.txt', 'r')
    s = f.read()
    for i in global_main_symbol:
        s += '\t_' + i + ' dw 0\n'
    f.close()
    f = open('C:/Users/YL139/Desktop/byyl/test/byxt/code_segment1.txt', 'r')
    s1 = f.read()
    s += s1
    f = open('C:/Users/YL139/Desktop/byyl/test/byxt/code_segment2.txt', 'r')
    rear = f.read()
    f.close()
    fun_name = '**'
    for i, line in enumerate(four_table):
        one = four_table[i][0]
        if one == 'main' or one == 'OP':
            continue
        two = str(four_table[i][1])
        three = str(four_table[i][2])
        four = str(four_table[i][3])
        if one not in ['j']:
            if two != '_' and two in global_main_symbol:
                two = 'ds:[_' + two + ']'
            elif two[0] == '$':
                two = 'es:[' + str(int(two[5:]) * 2) + ']'
            elif fun_name != '**' and two in function[fun_name][0]:
                two = function[fun_name][0][two]
            elif fun_name != '**' and two in function[fun_name][1]:
                two = function[fun_name][1][two]
            if three != '_' and three in global_main_symbol:
                three = 'ds:[_' + three + ']'
            elif three[0] == '$':
                three = 'es:[' + str(int(three[5:]) * 2) + ']'
            elif fun_name != '**' and three in function[fun_name][0]:
                three = function[fun_name][0][three]
            elif fun_name != '**' and three in function[fun_name][1]:
                three = function[fun_name][1][three]
            if four != '_' and four in global_main_symbol:
                four = 'ds:[_' + four + ']'
            elif four[0] == '$':
                four = 'es:[' + str(int(four[5:]) * 2) + ']'
            elif fun_name != '**' and four in function[fun_name][0]:
                four = function[fun_name][0][four]
            elif fun_name != '**' and four in function[fun_name][1]:
                four = function[fun_name][1][four]
        if one == '=':
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'MOV ' + four + ',AX\n'
        elif one == '+':
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'ADD AX,' + three + '\n\t' + 'MOV ' + four + ',AX\n'
        elif one == '-':
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'SUB AX,' + three + '\n\t' + 'MOV ' + four + ',AX\n'
        elif one == '*':
            s += '_%d:\t' % (
                    i - 1) + 'MOV AX,' + two + '\n\t' + 'MOV BX,' + three + '\n\t' + 'MUL BX\n\t' + 'MOV ' + four + ',AX\n'
        elif one == '/':
            s += '_%d:\t' % (
                    i - 1) + 'MOV AX,' + two + '\n\t' + 'MOV DX,0\n\t' + 'MOV AX,' + three + '\n\t' + 'DIV BX\n\t' + 'MOV ' + four + ',AX\n'
        elif one == '%':
            s += '_%d:\t' % (
                    i - 1) + 'MOV AX,' + two + '\n\t' + 'MOV DX,0\n\t' + 'MOV BX,' + three + '\n\t' + 'DIV BX\n\t' + 'MOV ' + four + ',DX\n'
        elif one == '<':
            s += '_%d:\t' % (
                    i - 1) + 'MOV DX,1\n\t''MOV AX,' + two + '\n\t' + 'CMP AX,' + three + '\n\t' + 'JB _LT_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_LT_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '>=':
            s += '_%d:\t' % (
                    i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,' + three + '\n\t' + 'JNB _GE_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_GE_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '>':
            s += '_%d:\t' % (
                    i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,' + three + '\n\t' + 'JA _GT_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_GT_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '<=':
            s += '_%d:\t' % (
                    i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,' + three + '\n\t' + 'JNA _LE_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_LE_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '==':
            s += '_%d:\t' % (
                    i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,' + three + '\n\t' + 'JE _EQ_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_EQ_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '!=':
            s += '_%d:\t' % (
                    i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,' + three + '\n\t' + 'JN _NE_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_NE_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '&&':
            s += '_%d:\t' % (i - 1) + 'MOV DX,0\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,0\n\t' + 'JE _AND_' + str(
                i - 1) + '\n\t' + 'MOV AX,' + three + '\n\t' + 'CMP AX,0\n\t' + 'JE _AND_' + str(
                i - 1) + '\n\t' + 'MOV DX,1\n' + '_AND_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '||':
            s += '_%d:\t' % (i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,0\n\t' + 'JNE _OR_' + str(
                i - 1) + '\n\t' + 'MOV AX,' + three + '\n\t' + 'CMP AX,0\n\t' + 'JNE _OR_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_OR_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == '!':
            s += '_%d:\t' % (i - 1) + 'MOV DX,1\n\t' + 'MOV AX,' + two + '\n\t' + 'CMP AX,0\n\t' + 'JE _NOT_' + str(
                i - 1) + '\n\t' + 'MOV DX,0\n' + '_NOT_' + str(i - 1) + ':\tMOV ' + four + ',DX\n'
        elif one == 'j':
            gg = '_' + str(int(four) - 1)
            if four_table[int(four)][0] == 'sys':
                gg = 'quit'
            s += '_%d:\t' % (i - 1) + 'JMP far ptr ' + gg + '\n'
        elif one == 'jz':
            gg = '_' + str(int(four) - 1)
            if four_table[int(four)][0] == 'sys':
                gg = 'quit'
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'CMP AX,0\n\t' + 'JNE _NE_' + str(
                i - 1) + '\n\t' + 'JMP far ptr ' + gg + '\n' + '_NE_' + str(i - 1) + ':\tNOP\n'
        elif one == 'jnz':
            gg = '_' + str(int(four) - 1)
            if four_table[int(four)][0] == 'sys':
                gg = 'quit'
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'CMP AX,0\n\t' + 'JE _EZ_' + str(
                i - 1) + '\n\t' + 'JMP far ptr ' + gg + '\n' + '_EZ_' + str(i - 1) + ':\tNOP\n'
        elif one == 'para':
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'PUSH AX\n'
        elif one == 'call':
            s += '_%d:\t' % (i - 1) + 'CALL ' + two + '\n'
            if four != '_':
                s += '\tMOV ' + four + ',AX\n'
        elif one == 'ret' and two != '_':
            s += '_%d:\t' % (i - 1) + 'MOV AX,' + two + '\n\t' + 'MOV SP,BP\n\t' + 'POP BP\n\t' + 'RET '
            if four != '_':
                s += str(len(function[fun_name][0]) * 2)  # ret 后的数字是参数个数*2  即参数区的大小 返回原来地址
            s += '\n'
            fun_name = '**'
        elif one == 'ret':
            s += '_%d:\t' % (i - 1) + 'MOV SP,BP\n\t' + 'POP PB\n\t' + 'RET\n'
            fun_name = '**'
        elif one == 'sys':
            s += 'quit:\t' + 'mov ah,4ch\n\t' + 'int 21h\n'
        else:
            fun_name = one
            s += one + ':\t' + 'PUSH BP\n\t' + 'MOV BP,SP\n\t' + 'SUB SP,' + str(len(function[fun_name][1]) * 2) + '\n'
    return s + rear


def get_target_code(mid_result):
    global global_main_symbol, function, quaternion_list, symbol_constant_list, symbol_variable_list, symbol_function_list, func_param_list, function_param_list
    quaternion_list = mid_result
    global_main_symbol = []
    function = {}
    function_get(quaternion_list)
    target_code_list = target_code(quaternion_list)
    return target_code_list


if __name__ == '__main__':
    code = open('C:/Users/YL139/Desktop/byyl/test/byxt/zjdm_example/test0.1.txt', encoding='UTF-8').read()
    token_information, error_information = recognizedID(code)
    result = get_syntax_result(token_information)
    quaternion_list = result[2]

    # syner = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/zjdm_example/test0.1.txt")
    # syner.run()
    # quaternion_list = enumerate(syner.quaternary_list)
    # for i, k in enumerate(syner.quaternary_list):
    #     quaternion_list = k

    function_get(quaternion_list)
    target_code_list = target_code(quaternion_list)
    # print(target_code_list)

    Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/mbdm.txt', mode='w', encoding='UTF-8')
    for k in target_code_list:
        Note1.write(k)
    Note1.close()
