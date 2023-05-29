# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 16:17:22 2020

@author: nuage
"""

import re

token2word = {}  # 全token表，后续转换

keyword_token = {'char': 101, 'int': 102, 'float': 103, 'break': 104, 'const': 105,
                 'return': 106, 'void': 107, 'continue': 108, 'do': 109, 'while': 110,
                 'if': 111, 'else': 112, 'for': 113, 'write': 114, 'true': 115, 'false': 116,
                 'main': 117, 'read': 118}
other_token = {'{': 301, '}': 302, ';': 303, ',': 304, '(': 201, ')': 202, '[': 203,
               ']': 204, '!': 205, '*': 206, '/': 207, '%': 208, '+': 209, '-': 210,
               '<': 211, '<=': 212, '>': 213, '>=': 214, '==': 215, '!=': 216, '&&': 217,
               '||': 218, '=': 219, '.': 220, '&': 221, '|': 222, '*=': 223, '/=': 224,
               '+=': 225, '-=': 226, '++': 227, '--': 228}


# 词法分析0.5
def recognizedID(code):
    code += '\n'
    token_information = []
    error_information = []
    line = 0
    now = 0
    i = 0
    while i < len(code):
        if code[i] == '\n':
            line += 1
            now = 0
            i += 1
        elif code[i].strip() == '':  # 忽视空字符
            now += 1
            i += 1
        else:
            if code[i].isalpha() or code[i] == '_':
                tempt, end = recognized_identifer(code[i:])
                #                print(i,end)
                token_information.append([line, now, now + end, code[i:i + end], tempt])
                i += end
                now += end
            elif code[i].isdigit():
                tempt, end = recognized_value(code[i:])
                #                print(i,end)
                if tempt == 'error':
                    error_information.append([line, now, now + end, code[i:i + end], 'error'])
                else:
                    token_information.append([line, now, now + end, code[i:i + end], tempt])
                i += end
                now += end
            elif code[i] == '/':
                tempt, end = recognized_note(code[i:])
                #                print(code[i:i+end])
                if tempt != 'note':
                    token_information.append([line, now, now + end, code[i:i + end], tempt])
                elif code[i:i + end].count('\n') > 0:  # 注释
                    line += code[i:i + end].count('\n')
                    i += end
                    now = len(code[i:i + end].split('\n')[-1])
                    end = 0
                i += end
                now += end
            elif code[i] == '\'':
                #                print('code:',i,code[i:])
                tempt, end = recognized_char(code[i:])
                #                print(i,end)
                if tempt == 'error' or len(eval(code[i:i + end])) != 1:
                    error_information.append([line, now, now + end, code[i:i + end], 'error'])
                else:
                    token_information.append([line, now, now + end, code[i:i + end], tempt])
                i += end
                now += end
            elif code[i] == '\"':
                tempt, end = recognized_str(code[i:])
                #                print(i,end)
                if tempt == 'error':
                    error_information.append([line, now, now + end, code[i:i + end], 'error'])
                else:
                    token_information.append([line, now, now + end, code[i:i + end], tempt])
                i += end
                now += end
            elif code[i] in other_token.keys() or code[i:i + 2] in other_token.keys():
                tempt, end = recognized_other(code[i:])
                token_information.append([line, now, now + end, code[i:i + end], tempt])
                i += end
                now += end
            else:
                error_information.append([line, now, now + 1, code[i:i + 1], 'error'])
                i += 1
                now += 1
    return token_information, error_information


def recognized_identifer(line):
    state = '0'
    for end, ch in enumerate(line):
        if state == '0':
            if ch.isalpha() or ch == '_':
                state = '1'
        elif state == '1':
            if ch.isalnum() or ch == '_':
                state = '1'
            else:
                state = '2'
                break
    if line[:end] in keyword_token.keys():
        return keyword_token[line[:end]], end
    else:
        return 700, end


def recognized_value(line):
    state = '0'
    next_ident = list(set([x[0] for x in other_token.keys()])) + [' ', '\n']
    for end, ch in enumerate(line):
        if state == '0':
            if ch in [str(x) for x in range(1, 10)]:
                state = '1'
            elif ch == '0':
                state = '3'
        elif state == '1':
            if ch in [str(x) for x in range(0, 10)]:
                state = '1'
            elif ch == '.':
                state = '8'
            elif ch in ['E', 'e']:
                state = '10'
            elif ch in next_ident:
                return 400, end  # 十进制整数
            else:
                state = 'error'
                break
        elif state == '3':
            if ch in [str(x) for x in range(0, 8)]:
                state = '3`'
            elif ch == 'x' or ch == 'X':
                state = '5'
            elif ch == '.':
                state = '8'
            elif ch in next_ident:
                return 400, end  # 十进制整数
            else:
                state = 'error'
                break
        elif state == '3`':
            if ch in [str(x) for x in range(0, 8)]:
                state = '3`'
            elif ch == '.':
                state = '8'
            elif ch in next_ident:
                return 400, end  # 八进制整数（或十进制）
            else:
                state = 'error'
                break
        elif state == '5':
            if ch in ([str(x) for x in range(0, 10)] + [chr(x) for x in range(65, 71)] + [chr(x) for x in
                                                                                          range(97, 103)]):
                state = '6'
            else:
                state = 'error'
                break
        elif state == '6':
            if ch in ([str(x) for x in range(0, 10)] + [chr(x) for x in range(65, 71)] + [chr(x) for x in
                                                                                          range(97, 103)]):
                state = '6'
            elif ch in next_ident:
                return 400, end  # 十六进制整数
            else:
                state = 'error'
                break
        elif state == '8':
            if ch in [str(x) for x in range(0, 10)]:
                state = '9'
            else:
                state = 'error'
                break
        elif state == '9':
            if ch in [str(x) for x in range(0, 10)]:
                state = '9'
            elif ch in ['E', 'e']:
                state = '10'
            elif ch in next_ident:
                return 800, end  # 实数
            else:
                state = 'error'
                break
        elif state == '10':
            if ch in [str(x) for x in range(0, 10)]:
                state = '12'
            elif ch in ['+', '-']:
                state = '11'
            else:
                state = 'error'
                break
        elif state == '11':
            if ch in [str(x) for x in range(0, 10)]:
                state = '12'
            else:
                state = 'error'
                break
        elif state == '12':
            if ch in [str(x) for x in range(0, 10)]:
                state = '12'
            elif ch in next_ident:
                return 800, end  # 实数
            else:
                state = 'error'
                break
    if state == 'error':
        for end, ch in enumerate(line):
            if ch in [' ', '\n'] or ch in other_token.keys():
                return 'error', end
    return 'error', end


def recognized_note(line):
    state = '0'
    for end, ch in enumerate(line):
        if state == '0':
            if ch == '/':
                state = '1'
        elif state == '1':
            if ch == '/':
                state = '2'
            elif ch == '*':
                state = '3'
            else:
                state = '4'  # 除号
                break
        elif state == '2':  # 找\n
            if ch == '\n':
                state = '5'  # 单行注释
        #                break
        elif state == '3':
            if ch == '*':
                state = '3`'  # 多行注释
        elif state == '3`':
            if ch == '/':
                state = '6'  # 多行注释
            #                break
            else:
                state = '3'
        elif state == '5' or state == '6':
            break
    if state == '4':
        return 207, end
    else:
        return 'note', end  # 结尾无*/也可，有问题


def recognized_char(line):
    state = '0'
    for end, ch in enumerate(line):
        if state == '0':
            if ch == '\'':
                state = '1'
        elif state == '1':
            if ch == '\'':
                state = '2'
            elif ch == '\n':
                state = '3'
                break
        elif state == '2':
            break
    #    print(state)
    if state == '3':
        return 'error', end
    elif state == '2':
        return 500, end


def recognized_str(line):  # eval
    state = '0'
    for end, ch in enumerate(line):
        if state == '0':
            if ch == '\"':
                state = '1'
        elif state == '1':
            if ch == '\"':
                state = '2'
            elif ch == '\n':
                state = '3'
                break
        elif state == '2':
            break
    if state == '3':
        return 'error', end
    elif state == '2':
        return 600, end


def recognized_other(line):  # 多位
    if line[:2] in other_token.keys():
        return other_token[line[:2]], 2
    elif line[:1] in other_token.keys():
        return other_token[line[:1]], 1


if __name__ == '__main__':
    code = open('test2_1.txt').read()
    token_information, error_information = recognizedID(code)
    print('行|列|词|token值')
    for i in token_information:
        print(i[0], '|', i[1], '|', i[3], '|', i[4])
    print('行|列|error')
    for i in error_information:
        print(i[0], '|', i[1], '|', i[3])
