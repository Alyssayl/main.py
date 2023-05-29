from zjdm import Zjdmsc

es_idx = -2


# 转换参数形式，isidentifier()判断是否为有效字符
def transfer(arg1, arg2, arg3):
    if str(arg1).isidentifier():
        arg1 = 'DS:[_{}]'.format(arg1)
    if str(arg2).isidentifier():
        arg2 = 'DS:[_{}]'.format(arg2)
    if str(arg3).isidentifier():
        arg3 = 'DS:[_{}]'.format(arg3)
    return arg1, arg2, arg3


# 生成一条汇编代码（四元式，变量）
def huibian(code, idx):
    global es_idx
    if code[0] == '+':
        # 加法
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tADD AX,{}\n\tMOV {},AX;\n'.format(arg1, arg2, res)

    elif code[0] == '-':
        # 减法
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tSUB AX,{}\n\tMOV {},AX\n'.format(arg1, arg2, res)

    elif code[0] == '*':
        # 乘法
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tMOV BX,{}\n\tMUL BX\n\tMOV {},AX\n'.format(arg1, arg2, res)

    elif code[0] == '/':
        # 除法
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tMOV DX,0\n\tMOV BX,{}\n\tDIV BX\n\tMOV {},AX\n'.format(arg1, arg2, res)

    elif code[0] == '%':
        # 求余数
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tMOV DX,0\n\tMOV BX,{}\n\tDIV BX\n\tMOV {},DX\n'.format(arg1, arg2, res)

    elif code[0] == '<':
        # 小于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,{}\n\tJB _LT\n\tMOV DX,0\n\t_LT:MOV {},DX\n'.format(arg1, arg2,
                                                                                                            res)

    elif code[0] == '>=':
        # 不小于把 res 置为 0， 否则为 1
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,{}\n\tJNB _GE\n\tMOV DX,0\n\t_GE:MOV {},DX\n'.format(arg1, arg2,
                                                                                                             res)

    elif code[0] == '>':
        # 大于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,{}\n\tJA _GT\n\tMOV DX,0\n\t_GT:MOV {},DX\n'.format(arg1, arg2,
                                                                                                            res)

    elif code[0] == '<=':
        # 不大于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,{}\n\tJNA _LE\n\tMOV DX,0\n\t_LE:MOV {},DX\n'.format(arg1, arg2,
                                                                                                             res)

    elif code[0] == '==':
        # 等于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,{}\n\tJE _EQ\n\tMOV DX,0\n\t_EQ:MOV {},DX\n'.format(arg1, arg2,
                                                                                                            res)

    elif code[0] == '!=':
        # 不等于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,{}\n\tJNE _NE\n\tMOV DX,0\n\t_NE:MOV {},DX\n'.format(arg1, arg2,
                                                                                                             res)

    elif code[0] == '&&':
        # 等于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,0\n\tMOV AX,{}\n\tCMP AX,0\n\tJE _AND\n\tMOV AX,{}\n\tCMP AX,0\n\tJE _' \
                     'AND\n\tMOV DX,1\n\t_AND:MOV {},DX\n'.format(arg1, arg2, res)

    elif code[0] == '||':
        arg1, arg2, T = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,0\n\tJNE _OR\n\tMOV AX,{}\n\tCMP AX,0\n\t' \
                     'JNE _OR\n\tMOV DX,0\n\t_OR:MOV {},DX\n'.format(arg1, arg2, T)

    elif code[0] == '!':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV DX,1\n\tMOV AX,{}\n\tCMP AX,0\n\tJE _NOT\n\tMOV DX,0\n\t_NOT:MOV {},DX\n'.format(arg1, res)

    elif code[0] == 'J':  # (j,,,P)
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tJMP far ptr {}\n'.format(res)

    elif code[0] == 'Jz':  # (jz,A,,P)
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tMOV AX,{}\n\tCMP AX,0\n\tJNE _NE\n\tJMP far ptr {}\n\t_NE:NOP\n'.format(arg1, res)

    elif code[0] == 'Jnz':  # (jnz,A,,P)
        # 等于把 res 置为 1， 否则为 0
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + res
        assem_code = '\tMOV AX,{}\n\tCMP AX,0\n\tJE _EZ\n\tJMP far ptr {}\n\t_EZ:NOP\n'.format(arg1, res)

    elif code[0] == 'para':  # (para,A,,)
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tPUSH AX\n'.format(arg1)

    elif code[0] == 'call':  # (call,fun,,A)
        arg1, arg2, res = code[1], code[2], code[3]
        assem_code = '\tCALL {}\n'.format(res)

    elif code[0] == 'ret':  # (ret,,,A)/(ret,,,)
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        if res != '':
            assem_code = '\tMOV AX,{}\n\tMOV SP,BP\n\tPOP BP\n\tRET\n'.format(res)
        else:
            assem_code = '\tMOV SP,BP\n\tPOP BP\n\tRET\n'

    elif code[0] == 'fun':  # (fun,,,)
        assem_code = '\tPUSH BP\n\tMOV BP,SP\n\tSUB SP'

    elif code[0] == 'J>':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tMOV AX,{}\n\tCMP AX,{}\n\tJG {}\n'.format(arg1, arg2, res)

    elif code[0] == 'J>=':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tMOV AX,{}\n\tCMP AX,{}\n\tJGE {}\n'.format(arg1, arg2, res)

    elif code[0] == 'J==':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tMOV AX,{}\n\tCMP AX,{}\n\tJE {}\n'.format(arg1, arg2, res)

    elif code[0] == 'J<':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tMOV AX,{}\n\tCMP AX,{}\n\tJL {}\n'.format(arg1, arg2, res)

    elif code[0] == 'J<=':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        res = '_' + str(res)
        assem_code = '\tMOV AX,{}\n\tCMP AX,{}\n\tJLE {}\n'.format(arg1, arg2, res)

    elif code[0] == '=':
        arg1, arg2, res = transfer(code[1], code[2], code[3])
        assem_code = '\tMOV AX,{}\n\tMOV {}, AX\n'.format(arg1, res)

    elif code[0] == 'sys':  # 结束
        assem_code = '\tMOV AH, 4CH\n\tint 21h\n'
        # assem_code = 'code ends\nend start\n'

    elif str(code[0]).isidentifier() and code[0] != 'main':
        idx = code[0]
        assem_code = '\tPUSH BP\n\tMOV BP,SP\n\tSUB SP\n'

    else:
        assem_code = ''
    if assem_code != '':
        assem_code = '_' + str(idx) + ':\n' + assem_code

    return assem_code


# 生成目标代码（中间代码生成的四元式）
def assemcodes(codes):
    global es_idx
    es_idx = -2
    assem_codes = []
    for i, code in enumerate(codes):
        assem_code = huibian(code, i)
        # if code[0] == 'para' and codes[i - 1][0] == 'call':
        #     assem_code = assem_code.replace('DS:[_{}]'.format(code[1]), 'ES:[{}]'.format(es_idx))
        assem_codes.append(assem_code)
    # assem_codes.append('code ends\nend start\n')

    return assem_codes


if __name__ == '__main__':
    syner = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/zjdm_example/test0.1.txt")
    syner.run()
    quaternion_list = enumerate(syner.quaternary_list)
    for i, k in enumerate(syner.quaternary_list):
        quaternion_list = k
    result = assemcodes(quaternion_list)
    Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/mbdm.txt', mode='w', encoding='UTF-8')
    for i, k in enumerate(result):
        print(k)
        Note.write(str(k))
    Note.close()
