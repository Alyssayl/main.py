from lexical import recognizedID, keyword_token, other_token
from cffx import Lexer
import time

token_map = {**keyword_token, **other_token}  # 函数形参
token_map = dict(zip(token_map.values(), token_map.keys()))  # 存储
# print(token_map)
# print('2222222222')
token_map.update({400: 'int', 800: 'float', 700: 'ident', 500: 'char', 600: 'str'})  # 更新键值对
token_map[114] = 'ident'
token_map[118] = 'ident'

syntax_tree = []

type_compatible = {'int': ['int'], 'float': ['float'], 'char': ['char'], 'str': ['str'],
                   'most': ['int', 'float', 'char', 'str']}
type_len = {'int': 4, 'float': 4, 'char': 1, 'str': 8}
return_value = {'int': ['int', '394'], 'char': ['char', 'A'], 'float': ['float', '4.026'], 'void': ['None', 'None']}

# [名：长度，类型，值]#，地址]
symbol_constant_list = {}
# [名：[同名变量表]]
# 同名变量表：[作用域路径：是否初始化了0|1，长度，类型，值]#，地址]
symbol_variable_list = {}
# [名：[同名函数表]]
# 同名函数表：作用域路径：是否初始化了0|1，返回值类型，参数个数，依次参数类型
symbol_function_list = {'write': {'/0': [1, 'int', 1, 'most']}, 'read': {'/0': [1, 'most', 0]}}
function_param_list = {}
function_param = []

now_memory_value = {'post': '/0', 'function': None, 'function_param': [], 'return': None, 'return_value': None,
                    'variable': None, 'variable_type': [], 'operation': [], 'operation_result': [], 'scope_num': 0}
# 需要分配地址就加一个变量用于地址移动，加一个变量记录地址空间情况

###############################################################################

quaternion_list = [['OP', 'ARG1', 'ARG2', 'RESULT'], ['main', '_', '_', '_']]
temp_t_list = []  # 类型，值


# 声明的常量名不能相同|数据类型需匹配
def constant_insert(name):
    if name not in symbol_constant_list.keys():
        if name in symbol_variable_list.keys() and now_memory_value['post'] in symbol_variable_list[name].keys():
            error('变量已存在', 1)
            return
        if name in symbol_function_list.keys() and now_memory_value['post'] in symbol_function_list[name].keys():
            error('函数已存在', 1)
            return
        if now_memory_value['variable_type'][1] == now_memory_value['operation_result'][1] and \
                now_memory_value['variable_type'][0] >= now_memory_value['operation_result'][0]:
            symbol_constant_list[name] = now_memory_value['variable_type'] + [now_memory_value['operation_result'][-1]]
        else:
            error('数据类型不匹配', 1)
    else:
        error('常量已存在', 1)
    return


# 常量不能更新，调用时看是否找得到
def constant_seek(name):
    if name in symbol_constant_list.keys():
        return True
    else:
        return False


# 同作用域下，声明的变量名不能相同
def variable_insert(name):
    if name not in symbol_variable_list.keys():
        symbol_variable_list[name] = {}
    if now_memory_value['post'] in symbol_variable_list[name].keys():
        error('变量已存在', 1)
    else:
        if name in symbol_constant_list.keys() and now_memory_value['post'] == '/0':  # 未测试
            error('常量已存在', 1)
            return
        if name in symbol_function_list.keys() and now_memory_value['post'] in symbol_function_list[name].keys():
            error('函数已存在', 1)
            return
        symbol_variable_list[name][now_memory_value['post']] = [0] + now_memory_value['variable_type'] + [None]


# 在作用域内找是否找得到变量|查找范围从深到浅
def variable_seek(name):
    if name in symbol_variable_list.keys():
        post = now_memory_value['post']
        while len(post):
            if post in symbol_variable_list[name].keys():
                return post
            else:
                post = '/'.join(post.split('/')[0:-1])
    return False


# 初始化的变量要定义了，是否类型对|赋值时是否类型对（向下兼容）
def variable_update(name):
    if variable_seek(name):
        post = variable_seek(name)
        if not now_memory_value['operation_result']:  # 中间变量函数未解决
            return
        if now_memory_value['operation_result'][1] in type_compatible[symbol_variable_list[name][post][2]] and \
                symbol_variable_list[name][post][1] >= now_memory_value['operation_result'][0]:
            symbol_variable_list[name][post][3] = now_memory_value['operation_result'][-1]
            symbol_variable_list[name][post][0] = 1
        else:
            error('数据类型不匹配', 1,
                  now_memory_value['operation_result'][1] + ',' + symbol_variable_list[name][post][2])
        now_memory_value['operation_result'] = []
        return
    now_memory_value['operation_result'] = []
    error('变量不存在', 1)


# 变量使用时是否初始化，返回长度、类型、值
def variable_call(name):
    if variable_seek(name):
        post = variable_seek(name)
        if symbol_variable_list[name][post][0] == 0:
            error('变量未初始化', 1, name)
        return symbol_variable_list[name][post][1:]
    elif constant_seek(name):
        return symbol_constant_list[name]
    # print(name, now_memory_value['post'], variable_seek(name), constant_seek(name), '????????????????????')
    error('变量或常量不存在', 1, name)
    return ['None', 'None', 'None']  # 返回未知值#检测到可立即停止运算


def arg2var(arg):
    if arg[0] == '#':
        var = temp_t_list[int(arg[1:])]  # 类型，值
    else:
        var = recognizedID(arg)[0][0]
        if var[-1] != 700:
            var = [token_map[var[-1]], eval(var[-2])]
        else:
            var = variable_call(arg)[1:]
    return var


# 运算函数,运算类型要匹配
def calculated_value(OP, ARG1, ARG2, RESULT):
    if OP == '@':
        opv = [0, 0, 1, '-', 210]
    else:
        opv = recognizedID(OP)[0][0]
    if opv[-2] in ['j', 'jnz', 'jz', 'para', 'call']:
        return
    if opv[-2] in ['call']:
        temp_t_list[int(RESULT[1:])] = return_value[now_memory_value['return']]
    elif ARG1 == '_' or ARG2 == '_':
        if ARG1 == '_':
            arg = ARG2
        elif ARG2 == '_':
            arg = ARG1
        var = arg2var(arg)
        if not var:  # 中间变量函数未解决
            return
        if str(var[1]) == 'None':
            if arg[0] != '#':
                error('运算值类型不匹配', 1, arg)
            now_memory_value['operation_result'] = ['None', 'None', 'None']
        else:
            if opv[-2] == '=':
                pass
            elif opv[-2] == '-':
                var[-1] = -var[-1]
            now_memory_value['operation_result'] = [type_len[var[0]]] + var
        if RESULT[0] == '#':
            temp_t_list[int(RESULT[1:])] = var
    elif ARG1 != '_' and ARG2 != '_':
        var1 = arg2var(ARG1)
        var2 = arg2var(ARG2)
        if str(var1[1]) == 'None' or str(var2[1]) == 'None':
            if ARG1[0] != '#' and ARG2[0] != '#':
                error('运算值类型不匹配', 1, ARG1 + ',' + ARG2)
            elif ARG1[0] != '#':
                error('运算值类型不匹配', 1, ARG1)
            elif ARG2[0] != '#':
                error('运算值类型不匹配', 1, ARG2)
            now_memory_value['operation_result'] = ['None', 'None', 'None']
        # elif opv[-2] == '/' and eval(var2[1]) == 0:
        #     error('除数不能为0', 1)
        #     now_memory_value['operation_result'] = ['None', 'None', 'None']
        elif opv[-2] == '%' and (type(eval(str(var1[1]))) == float or type(eval(str(var2[1]))) == float):
            error('浮点数不能参与%运算', 1)
            now_memory_value['operation_result'] = ['None', 'None', 'None']
        else:
            if var1[0] in type_compatible[var2[0]]:
                var = [var2[0], eval(str(var1[1]) + opv[-2] + str(var2[1]))]
                now_memory_value['operation_result'] = [type_len[var[0]]] + var
            elif var2[0] in type_compatible[var1[0]]:
                var = [var1[0], eval(str(var1[1]) + opv[-2] + str(var2[1]))]
                now_memory_value['operation_result'] = [type_len[var[0]]] + var
            else:
                var = '无'
                error('运算值类型不匹配', 1, str(var1[1]) + ',' + str(var2[1]))
                now_memory_value['operation_result'] = ['None', 'None', 'None']
        if RESULT[0] == '#':
            temp_t_list[int(RESULT[1:])] = now_memory_value['operation_result'][1:]


# 函数声明时使用，变量名不能相同
def function_insert(name):
    if name not in symbol_function_list.keys():
        symbol_function_list[name] = {}
    if now_memory_value['post'] in symbol_function_list[name].keys():
        error('函数已存在', 1)
    else:
        if name in symbol_constant_list.keys() and now_memory_value['post'] == '/0':  # 未测试
            error('常量已存在', 1)
            return
        if name in symbol_variable_list.keys() and now_memory_value['post'] in symbol_variable_list[name].keys():
            error('变量已存在', 1)
            return
        symbol_function_list[name][now_memory_value['post']] = [0, now_memory_value['return'], 0]


# 在作用域内找是否找得到函数|查找范围从深到浅，返回最近作用域
def function_seek(name):
    if name in symbol_function_list.keys():
        post = now_memory_value['post']
        while len(post):
            if post in symbol_function_list[name].keys():
                return post
            else:
                post = '/'.join(post.split('/')[0:-1])
    return False


# 函数声明时使用
def function_update(name):
    if function_seek(name):
        for param in now_memory_value['function_param']:
            symbol_function_list[name][now_memory_value['post']].append(param)
            symbol_function_list[name][now_memory_value['post']][2] += 1
    else:
        error('函数名不匹配', 1)
    now_memory_value['function_param'] = []


# 函数调用时检查是否声明（存在），是否匹配参数，返回长度、类型、值
def function_call_semantics(name):
    if function_seek(name):
        post = function_seek(name)
        params = symbol_function_list[name][post][3:]
        if len(params) == len(now_memory_value['function_param']):
            for i, param in enumerate(params):
                if param != now_memory_value['function_param'][i]:
                    error('调用参数类型不匹配', 1)
                    return [type_len[symbol_function_list[name][post][1]], symbol_function_list[name][post][1], None]
            return [type_len[symbol_function_list[name][post][1]], symbol_function_list[name][post][1], None]
        else:
            error('调用参数数量不匹配', 1)
            return [type_len[symbol_function_list[name][post][1]], symbol_function_list[name][post][1], None]
    error('调用函数不存在', 1)
    return ['None', 'None', 'None']  # 返回未知值#检测到可立即停止运算


# 函数函数初始化时是否已初始化，是否匹配参数
def function_init(name):
    if function_seek(name):
        post = function_seek(name)
        if symbol_function_list[name][post][0] == 0:
            params = symbol_function_list[name][post][3:]
            if len(params) == len(now_memory_value['function_param']):
                for i, param in enumerate(params):
                    if param != now_memory_value['function_param'][i]:
                        now_memory_value['function_param'] = []
                        error('初始化参数类型不匹配', 1)
                        return
                symbol_function_list[name][post][0] = 1  # 匹配的才会初始化成功
                return
            else:
                error('初始化参数数量不匹配', 1)
                return
        else:
            error('函数已初始化', 1)
            return
    error('初始化函数不存在', 1)
    return


def gencode(OP, ARG1, ARG2, RESULT):
    quaternion_list.append([OP, ARG1, ARG2, RESULT])
    calculated_value(OP, ARG1, ARG2, RESULT)
    if RESULT in symbol_variable_list.keys():
        variable_update(RESULT)


ti = 0


def newtemp():
    global ti
    res = '#' + str(ti)
    ti += 1
    temp_t_list.append([])
    return res


def entry(i):
    variable_call(i)
    if variable_seek(i) or constant_seek(i):
        return i
    else:
        return i


def merge(p1, p2):
    quaternion_list[p2][3] = p1
    return p2


# 回填函数
def backpatch(p, t):
    while quaternion_list[p][3] != 0:
        m = quaternion_list[p][3]
        quaternion_list[p][3] = t
        p = m
    quaternion_list[p][3] = t


# 语义错误
semantic_error_list = []
# 语法错误
error_list = []


def error(info, semantic=0, detail=None):
    global token, i
    line_s = i
    while token_information[line_s - 1][0] == token_information[i][0]:
        line_s -= 1
    if token_information[i][-2] == '#end#' and semantic == 0:
        error_list.append([token_information[i - 1][0] + 1, 0, info])
        return
    line_v = [token_information[i][0], token_information[i][1], '']
    if detail:
        line_v[2] = detail + '|' + info
    else:
        while token_information[line_s][0] <= token_information[i][0] and token_information[line_s][-2] != '#end#':
            line_v[2] += token_information[line_s][-2] + ' '
            line_s += 1
        line_v[2] += '|' + info
    if semantic == 1 and detail:
        semantic_error_list.append(line_v)
    elif semantic == 1:
        line_v[2] = token_information[i][-2] + '|' + line_v[2].split('|')[-1]
        semantic_error_list.append(line_v)
    else:
        error_list.append(line_v)


def skip(line=1, is_line=1):
    global token, i
    if is_line:
        old_line = token_information[i][0]
        while token_information[i][0] < old_line + line:
            i += 1
            token = token_information[i][-1]
    else:
        now_s = 0
        while now_s < line:
            now_s += 1
            i += 1
            token = token_information[i][-1]


string = ''


def match(value):
    global token, i, string
    i += 1
    token = token_information[i][-1]


# 缺少<函数调用>，标识符是否已声明的判定
def factor_(deep):
    PLACE_factor_ = '_'
    if token_map[token] == '(':
        match(token)
        PLACE_boolean_expression = boolean_expression(deep)
        if token_map[token] == ')':
            match(token_map[token])
            PLACE_factor_ = newtemp()
            PLACE_factor_ = PLACE_boolean_expression
        else:
            error('缺少 )')
    elif token_map[token] in ['int', 'float', 'char', 'str']:
        PLACE_factor_ = token_information[i][-2]
        match(token_map[token])
    elif token_map[token] in ['ident']:
        PLACE_factor_ = newtemp()
        var_name = token_information[i][-2]
        F_id = token_information[i][-2]
        match(token_map[token])
        if token_map[token] == '(':
            match(token_map[token])
            return_value = function_call(deep)
            if token in token_map.keys() and token_map[token] in [')']:
                match(token_map[token])
                gencode('call', F_id, '_', return_value)
                PLACE_factor_ = return_value
        else:
            PLACE_factor_ = entry(var_name)
    else:
        error('值错误')
    return PLACE_factor_


def factor(deep):
    PLACE_factor = '_'
    if token_map[token] in '-':
        PLACE_factor = newtemp()
        match(token_map[token])
        PLACE_factor_ = factor_(deep)
        gencode('@', PLACE_factor_, '_', PLACE_factor)
    else:
        PLACE_factor_ = factor_(deep)
        PLACE_factor = PLACE_factor_
    return PLACE_factor


def term_(deep, PLACE_term):
    PLACE_term_ = '_'
    if token in token_map.keys() and token_map[token] in ['*', '/', '%']:
        PLACE_term_ = newtemp()
        op = token_map[token]
        match(token_map[token])
        PLACE_factor = factor(deep)
        gencode(op, PLACE_term, PLACE_factor, PLACE_term_)
        temp = term_(deep, PLACE_term_)
        if temp:
            PLACE_term_ = temp
        return PLACE_term_


def term(deep):
    PLACE_term = '_'
    PLACE_factor = factor(deep)
    PLACE_term = PLACE_factor
    temp = term_(deep, PLACE_term)
    if temp:
        PLACE_term = temp
    return PLACE_term


def arithmetic_expression_(deep, PLACE_arithmetic_expression):
    PLACE_arithmetic_expression_ = '_'
    if token in token_map.keys() and token_map[token] in ['+', '-']:
        PLACE_arithmetic_expression_ = newtemp()
        op = token_map[token]
        match(token_map[token])
        PLACE_term = term(deep)
        gencode(op, PLACE_arithmetic_expression, PLACE_term, PLACE_arithmetic_expression_)
        temp = arithmetic_expression_(deep, PLACE_arithmetic_expression_)
        if temp:
            PLACE_arithmetic_expression_ = temp
        return PLACE_arithmetic_expression_


def arithmetic_expression(deep):
    PLACE_arithmetic_expression = '_'
    PLACE_term = term(deep)
    PLACE_arithmetic_expression = PLACE_term
    temp = arithmetic_expression_(deep, PLACE_arithmetic_expression)
    if temp:
        PLACE_arithmetic_expression = temp
    return PLACE_arithmetic_expression


def relationship_expression(deep, PLACE_boolean_factor):
    PLACE_relationship_expression = '_'
    if token in token_map.keys() and token_map[token] in ['<', '<=', '>', '>=', '==', '!=']:
        rop = token_map[token]
        PLACE_relationship_expression = newtemp()
        match(token_map[token])
        PLACE_arithmetic_expression = arithmetic_expression(deep)
        gencode(rop, PLACE_boolean_factor, PLACE_arithmetic_expression, PLACE_relationship_expression)
        return PLACE_relationship_expression


def boolean_factor(deep):
    PLACE_boolean_factor = '_'
    if token in token_map.keys() and token_map[token] in ['!']:
        PLACE_boolean_factor = newtemp()
        match(token_map[token])
        PLACE_boolean_expression = boolean_expression(deep)
        gencode('!', PLACE_boolean_expression, '_', PLACE_boolean_factor)
    elif token in token_map.keys() and token_map[token] in ['true', 'false']:
        #        print('-'*deep+'布尔因子分析<BF>->b')
        PLACE_boolean_factor = token_map[token]
        match(token_map[token])
    else:
        #        print('-'*deep+'布尔因子分析<BF>->EG')
        PLACE_arithmetic_expression = arithmetic_expression(deep)
        PLACE_boolean_factor = PLACE_arithmetic_expression
        temp = relationship_expression(deep, PLACE_boolean_factor)
        if temp:
            PLACE_boolean_factor = temp
    return PLACE_boolean_factor


def boolean_term_(deep, PLACEo_boolean_term):
    #    print('BT_',token_information[i])
    if token in token_map.keys() and token_map[token] in ['&&']:
        #        print('-'*deep+'布尔项分析<BT`>->&&<BT>')
        PLACE_boolean_term_ = newtemp()
        rop = token_map[token]
        match(token_map[token])
        PLACE_boolean_term = boolean_term(deep)
        gencode(rop, PLACEo_boolean_term, PLACE_boolean_term, PLACE_boolean_term_)
        return PLACE_boolean_term_


def boolean_term(deep):
    #    print('BT',token_information[i])
    #    print('-'*deep+'布尔项分析<BT>-><BF><BT`>')
    PLACE_boolean_factor = boolean_factor(deep)
    PLACE_boolean_term = PLACE_boolean_factor
    temp = boolean_term_(deep, PLACE_boolean_term)
    if temp:
        PLACE_boolean_term = temp
    return PLACE_boolean_term


def boolean_expression_(deep, PLACEo_boolean_expression):
    #    print('BE_',token_information[i])
    if token in token_map.keys() and token_map[token] in ['||']:
        PLACE_boolean_expression_ = newtemp()
        rop = token_map[token]
        #        print('-'*deep+'布尔表达式分析<BE`>->||<BE>')
        match(token_map[token])
        PLACE_boolean_expression = boolean_expression(deep)
        gencode(rop, PLACEo_boolean_expression, PLACE_boolean_expression, PLACE_boolean_expression_)
        return PLACE_boolean_expression_


def boolean_expression(deep):
    #    print('BE',token_information[i])
    #    print('-'*deep+'布尔表达式分析')
    PLACE_boolean_term = boolean_term(deep)
    PLACE_boolean_expression = PLACE_boolean_term
    temp = boolean_expression_(deep, PLACE_boolean_expression)
    if temp:
        PLACE_boolean_expression = temp
    return PLACE_boolean_expression


#    print('-'*deep+'布尔表达式分析结束')

def assignment_expression(deep):
    #    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    if token in token_map.keys() and token_map[token] in ['ident']:
        #        print('-'*deep+'赋值表达式分析<AE>-><ident>=EG')
        ident = token_information[i][-2]
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['=']:
            op = token_map[token]
            match(token_map[token])
            PLACE_assignment_expression = arithmetic_expression(deep)
            temp = relationship_expression(deep, PLACE_assignment_expression)
            if temp:
                PLACE_assignment_expression = temp
            gencode(op, PLACE_assignment_expression, '_', ident)
            return ident


def assignment_statement(deep):
    #    print('-'*deep+'赋值语句分析')
    assignment_expression(deep)
    if token in token_map.keys() and token_map[token] in [';']:
        match(token_map[token])


#    print('-'*deep+'赋值语句分析结束')

def variable_type(deep):
    #    print('-'*deep+'VT')
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float']:
        now_memory_value['variable_type'] = [type_len[token_map[token]], token_map[token]]  # 语义
        match(token_map[token])


def constant_declaration_list_(deep):
    #    print('-'*deep+'CDT_')
    if token_map[token] in [';']:
        match(token_map[token])
    elif token_map[token] in [',']:
        match(token_map[token])
        constant_declaration_list(deep)


def constant_declaration_list(deep):  # 常量声明表
    #    print('-'*deep+'CDT')
    if token_map[token] in ['ident']:
        now_memory_value['variable'] = token_information[i][-2]  # 语义
        match(token_map[token])
        if token_map[token] in ['=']:
            match(token_map[token])
            if token_map[token] in ['int', 'float', 'char', 'str']:
                now_memory_value['operation_result'] = [type_len[token_map[token]], token_map[token],
                                                        token_information[i][-2]]  # 语义
                match(token_map[token])
                constant_insert(now_memory_value['variable'])  # 语义
                constant_declaration_list_(deep)
            else:
                error('赋值错误')
                skip(1)


def variable_declaration_(deep, ident):
    #    print('-'*deep+'VD_')
    if token_map[token] in ['=']:
        variable_insert(now_memory_value['variable'])  # 语义
        op = token_map[token]
        match(token_map[token])
        #        print(token_information[i][-2],'var')
        PLACE_boolean_expression = boolean_expression(deep)
        #        print(op,type(PLACE_boolean_expression),'_',ident)
        gencode(op, PLACE_boolean_expression, '_', ident)
    elif token_map[token] in ['(']:
        #        print('函数')
        now_memory_value['function'] = token_information[i - 1][-2]  # 语义
        function_insert(now_memory_value['function'])  # 语义
        match(token_map[token])
        function_declaration_parameter_list(deep)
        if token_map[token] in [')']:
            match(token_map[token])
    #            if token_map[token] in [';']:
    #                match(token_map[token])
    elif token_map[token] in [';', ',']:
        variable_insert(now_memory_value['variable'])  # 语义


def variable_declaration(deep):
    #    print('-'*deep+'VD',token_map[token])
    if token_map[token] in ['ident']:  # 加函数变量
        #        print('-'*deep+'VdD')
        now_memory_value['variable'] = token_information[i][-2]  # 语义
        ident = token_information[i][-2]
        match(token_map[token])
        variable_declaration_(deep, ident)


def variable_declaration_list_(deep):
    #    print('-'*deep+'VDL_')
    if token_map[token] in [';']:
        match(token_map[token])
    elif token_map[token] in [',']:
        match(token_map[token])
        variable_declaration_list(deep)


def variable_declaration_list(deep):  # 变量声明
    #    print('-'*deep+'VDL')
    variable_declaration(deep)
    #    time.sleep(5)
    variable_declaration_list_(deep)


def function_declaration_parameter_(deep):
    #    print('-'*deep+'FDP_')
    #    time.sleep(5)
    if token in token_map.keys() and token_map[token] in [',']:
        match(token_map[token])
        function_declaration_parameter(deep)
    elif token_map[token] not in [')']:
        error('缺少 )')


def function_declaration_parameter(deep):
    #    print('-'*deep+'FDP')
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float']:
        now_memory_value['function_param'].append(token_map[token])  # 语义
        match(token_map[token])
        if token_map[token] in ['ident']:
            match(token_map[token])
            function_declaration_parameter_(deep)
        elif token in token_map.keys() and token_map[token] in [',']:
            function_declaration_parameter_(deep)


def function_declaration_parameter_list(deep):  # 函数参数
    #    print('-'*deep+'FDPL')
    if token_map[token] not in [')']:
        function_declaration_parameter(deep)


def declarative_statement(deep):  # 声明语句
    #    print('-'*deep+'DS')
    if token in token_map.keys() and token_map[token] in ['const']:
        #        print('-'*deep+'常量')
        match(token_map[token])
        variable_type(deep)
        constant_declaration_list(deep)
    elif token in token_map.keys() and token_map[token] in ['int', 'char', 'float']:
        now_memory_value['return'] = token_map[token]  # 语义
        now_memory_value['variable_type'] = [type_len[token_map[token]], token_map[token]]  # 语义
        match(token_map[token])
        #        time.sleep(5)
        if token_map[token] in ['ident']:
            #            print(token_information[i][-2],token_information[i+1][-2] in ['('])
            #            time.sleep(5)
            if token_information[i + 1][-2] in ['(']:  # 应该进不来，没在main中声明过函数(解决)
                #                print('-'*deep+'函数')
                now_memory_value['function'] = token_information[i][-2]  # 语义
                function_insert(now_memory_value['function'])  # 语义
                match(token_map[token])
                match(token_map[token])
                function_declaration_parameter_list(deep)
                if token_map[token] in [')']:
                    match(token_map[token])
                    function_update(now_memory_value['function'])  # 语义
                    if token_map[token] in [';']:
                        match(token_map[token])
            else:
                #                print('-'*deep+'变量')
                variable_declaration_list(deep)
    elif token in token_map.keys() and token_map[token] in ['void']:
        match(token_map[token])
        if token_map[token] in ['ident']:
            match(token_map[token])
            if token_map[token] in ['(']:
                #                print('-'*deep+'函数')
                match(token_map[token])
                function_declaration_parameter_list(deep)
                #                time.sleep(5)
                if token_map[token] in [')']:
                    match(token_map[token])
                    if token_map[token] in [';']:
                        match(token_map[token])


def statement(deep):  # <语句>
    #    print('-'*deep+'语句')
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float', 'void', 'const']:
        syntax_tree.append('-' * deep + '声明语句')
        declarative_statement(deep)
    #        print('-'*deep+'声明语句结束')
    elif token in token_map.keys() and token_map[token] in ['ident', '{', 'if', 'for', 'while', 'do', 'return']:
        #        print('-'*deep+'执行语句分析')
        execution_statement(deep)
    #        print('-'*deep+'执行语句分析结束')
    else:
        error('语句错误')
        skip(1)


def statement_list_(deep):
    if token in token_map.keys() and token_map[token] not in ['}']:
        statement_list(deep)


def statement_list(deep):  # 语句表
    statement(deep + 4)
    statement_list_(deep)


def compound_statement(deep):  # 复合语句
    #    print('-'*deep+'复合语句分析')
    if token in token_map.keys() and token_map[token] not in ['{']:
        error('缺少 {')
        while token in token_map.keys() and token_map[token] not in ['{']:
            skip(1, 0)
    now_memory_value['scope_num'] += 1  # 语义
    now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
    match(token_map[token])
    statement_list(deep)
    if token in token_map.keys() and token_map[token] in ['}']:
        now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
        match(token_map[token])
    else:
        error('缺少 }')


#####################################

def function_call_(deep):
    if token in token_map.keys() and token_map[token] in [',']:
        match(token_map[token])
        if token_map[token] in [')']:
            error('函数调用错误')
            skip(1)
        function_call(deep)
    elif token_map[token] not in [')']:
        error('缺少 )')


def function_call(deep):  # 函数调用
    if token_map[token] in ['ident', 'int', 'float', 'char', 'str']:
        f_type = token_information[i - 1][-2]
        return_value = newtemp()
        if token_information[i + 1][-2] in ['(']:
            F_id = token_information[i][-2]
            match(token_map[token])  # 函数名
            match(token_map[token])  # 括号
            return_value1 = function_call(deep)
            if token in token_map.keys() and token_map[token] in [')']:
                match(token_map[token])
                now_memory_value['return'] = f_type
                gencode('call', F_id, '_', return_value1)
                # 少一节para
                gencode('para', return_value1, '_', '_')
        else:
            F_id = boolean_expression(deep)
            gencode('para', F_id, '_', '_')
        function_call_(deep)
        return return_value
    elif token_map[token] in [')']:
        return_value = newtemp()
        return return_value


def data_processing_statement_(deep, ident):
    if token in token_map.keys() and token_map[token] in ['(']:
        #        print('-'*deep+'函数调用语句分析<DPS`>-><>')
        match(token_map[token])
        return_value = function_call(deep)
        if token in token_map.keys() and token_map[token] in [')']:
            match(token_map[token])
            if token in token_map.keys() and token_map[token] in [';']:
                match(token_map[token])
                gencode('call', ident, '_', return_value)
    elif token in token_map.keys() and token_map[token] in ['=']:
        #        print('-'*deep+'赋值语句分析<DPS`>-><BE>')
        match(token_map[token])
        PLACE_boolean_expression = boolean_expression(deep)
        gencode('=', PLACE_boolean_expression, '_', ident)
        if token in token_map.keys() and token_map[token] in [';']:
            match(token_map[token])
        else:
            error('赋值错误')
            skip(1)


def data_processing_statement(deep):
    if token in token_map.keys() and token_map[token] in ['ident']:
        #        print('-'*deep+'数据处理语句分析<DPS>-><DPS`>')
        ident = token_information[i][-2]
        match(token_map[token])
        data_processing_statement_(deep, ident)


def if_statement__(deep, C_CHAIN, T_CHAIN):
    #    print('-'*deep+'IFS__')
    #    print(token_information[i])
    if token in token_map.keys() and token_map[token] in ['if']:
        syntax_tree.append('-' * deep + 'else if')
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['(']:
            match(token_map[token])
            PLACE_boolean_expression = boolean_expression(deep)
            if token in token_map.keys() and token_map[token] in [')']:
                #                E_TC=len(quaternion_list)
                #                gencode('jnz',PLACE_boolean_expression,'_',0)
                E_FC = len(quaternion_list)
                gencode('jz', PLACE_boolean_expression, '_', 0)
                #                backpatch(E_TC,len(quaternion_list))
                C1_CHAIN = merge(C_CHAIN, E_FC)
                match(token_map[token])
                if token in token_map.keys() and token_map[token] in ['{']:  # while不用改
                    compound_statement(deep)
                else:
                    now_memory_value['scope_num'] += 1  # 语义
                    now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
                    statement(deep + 4)
                    now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
                #                print(token_information[i])
                tempf, tempt = if_statement_(deep, C1_CHAIN, T_CHAIN)
                if tempf != 'None':
                    C1_CHAIN = tempf
                T1_CHAIN = T_CHAIN
                if tempt != 'None':
                    T1_CHAIN = tempt
                S1_CHAIN = len(quaternion_list)
                gencode('j', '_', '_', 0)
                if tempf == 'None' and tempt != 'None':
                    S_CHAIN = S1_CHAIN
                else:
                    S_CHAIN = merge(C1_CHAIN, S1_CHAIN)  # this
        #                backpatch(S_CHAIN,len(quaternion_list))
        return S_CHAIN, T1_CHAIN
    else:
        syntax_tree.append('-' * deep + 'else')
        #        q=len(quaternion_list)
        #        gencode('j','_','_',0)
        backpatch(C_CHAIN, len(quaternion_list))
        #        T_CHAIN=merge(S1_CHAIN,q)
        #        T_CHAIN=q
        if token in token_map.keys() and token_map[token] in ['{']:  # while不用改
            compound_statement(deep)
        else:
            now_memory_value['scope_num'] += 1  # 语义
            now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
            statement(deep + 4)
            #            print(quaternion_list,token_information[i])
            now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
        return 'None', T_CHAIN


def if_statement_(deep, C_CHAIN, T_CHAIN=0):
    if token in token_map.keys() and token_map[token] in ['else']:
        C1_CHAIN = len(quaternion_list)
        gencode('j', '_', '_', 0)
        if T_CHAIN != 0:
            C1_CHAIN = merge(T_CHAIN, C1_CHAIN)
        match(token_map[token])
        return if_statement__(deep, C_CHAIN, C1_CHAIN)
    else:
        return 'None', 'None'


def if_statement(deep):
    syntax_tree.append('-' * deep + 'if语句')
    if token in token_map.keys() and token_map[token] in ['if']:
        #        print('-'*deep+'if语句分析<IFS>->if(<BE>)<S><IFS`>')
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['(']:
            match(token_map[token])
            PLACE_boolean_expression = boolean_expression(deep)
            if token in token_map.keys() and token_map[token] in [')']:
                #                E_TC=len(quaternion_list)
                #                gencode('jnz',PLACE_boolean_expression,'_',0)
                E_FC = len(quaternion_list)
                gencode('jz', PLACE_boolean_expression, '_', 0)
                #                print(quaternion_list[E_FC])
                #                backpatch(E_TC,len(quaternion_list))
                C_CHAIN = E_FC
                match(token_map[token])
                #                print(token_information[i],token in token_map.keys() and token_map[token] in ['{'])
                if token in token_map.keys() and token_map[token] in ['{']:  # while不用改
                    compound_statement(deep)
                else:
                    now_memory_value['scope_num'] += 1  # 语义
                    now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
                    statement(deep + 4)
                    now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
                tempf, tempt = if_statement_(deep, C_CHAIN)
                if tempf != 'None':
                    C_CHAIN = tempf
                #                if tempt:
                #                    T1_CHAIN=tempt
                #                S1_CHAIN=len(quaternion_list)
                #                gencode('j','_','_',0)
                #                S_CHAIN=merge(C_CHAIN,S1_CHAIN)
                if quaternion_list[E_FC][-1] == 0:
                    backpatch(C_CHAIN, len(quaternion_list))
                elif tempf != 'None':
                    backpatch(tempf, len(quaternion_list))
                if tempt != 'None':
                    backpatch(tempt, len(quaternion_list))
        syntax_tree.append('-' * deep + 'if语句结束')
        return len(quaternion_list)


def control_statement(deep):
    #    print('-'*deep+'CS')
    if token in token_map.keys() and token_map[token] in ['if']:
        #        print('-'*deep+'控制语句分析<CS>-><IFS>')
        if_statement(deep)
    #        time.sleep(5)
    elif token in token_map.keys() and token_map[token] in ['for']:
        for_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['while']:
        while_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['do']:
        do_while_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['return']:
        return_statement(deep)


def execution_statement(deep):
    #    print('-'*deep+'ES')
    if token in token_map.keys() and token_map[token] in ['ident']:
        syntax_tree.append('-' * deep + '数据处理')
        data_processing_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['{']:
        compound_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['if', 'for', 'while', 'do', 'return']:
        #        print('-'*deep+'执行语句分析<ES>-><CS>')
        control_statement(deep)


################################################################################

def return_statement_(deep):
    if token in token_map.keys() and token_map[token] in [';']:
        match(token_map[token])
        #        now_memory_value['return_value']=None
        gencode('ret', '_', '_', '_')
    else:
        PLACE_boolean_expression = boolean_expression(deep)
        gencode('ret', PLACE_boolean_expression, '_', '_')
        #        now_memory_value['return_value']=PLACE_boolean_expression
        if token in token_map.keys() and token_map[token] in [';']:
            match(token_map[token])


def return_statement(deep):
    syntax_tree.append('-' * deep + 'return')
    if token in token_map.keys() and token_map[token] in ['return']:
        match(token_map[token])
        return_statement_(deep)


#    print('-'*deep+'return语句分析结束')

def break_statement(deep):
    syntax_tree.append('-' * deep + 'break')
    if token in token_map.keys() and token_map[token] in ['break']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in [';']:
            match(token_map[token])


#    print('-'*deep+'break语句分析结束')

def continue_statement(deep):
    syntax_tree.append('-' * deep + 'continue')
    if token in token_map.keys() and token_map[token] in ['continue']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in [';']:
            match(token_map[token])


#    print('-'*deep+'continue语句分析结束')

def loop_statement_list_(deep, BRK, CHAIN):
    if token in token_map.keys() and token_map[token] in ['}']:
        return BRK, CHAIN
    else:
        BRK1, CHAIN1 = loop_statement_list(deep)
        if BRK == 'None':
            rBRK = BRK1
        else:
            rBRK = merge(BRK, BRK1)
        if CHAIN == 'None':
            rCHAIN = CHAIN1
        else:
            rCHAIN = merge(CHAIN, CHAIN1)
        return rBRK, rCHAIN


def loop_statement_list(deep):
    BRK, CHAIN = loop_statement(deep)
    loop_statement_list_(deep, BRK, CHAIN)
    return BRK, CHAIN


def loop_compound_statement(deep):
    #    print('-'*deep+'循环复合语句分析')
    if token in token_map.keys() and token_map[token] in ['{']:
        now_memory_value['scope_num'] += 1  # 语义
        now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
        match(token_map[token])
        BRK, CHAIN = loop_statement_list(deep + 4)
        if token in token_map.keys() and token_map[token] in ['}']:
            now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
            match(token_map[token])
            return BRK, CHAIN


def loop_execution_statement(deep):
    #    print('-'*deep+'循环执行语句分析')
    BRK, CHAIN = 'None', 'None'
    if token in token_map.keys() and token_map[token] in ['if']:
        loop_if_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['for']:
        for_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['while']:
        while_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['do']:
        do_while_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['return']:
        return_statement(deep)
    elif token in token_map.keys() and token_map[token] in ['break']:
        break_statement(deep)
        BRK = len(quaternion_list)
        gencode('j', '_', '_', 0)
    elif token in token_map.keys() and token_map[token] in ['continue']:
        continue_statement(deep)
        CHAIN = len(quaternion_list)
        gencode('j', '_', '_', 0)
    return BRK, CHAIN


def loop_statement(deep):
    #    print('-'*deep+'循环语句分析')
    S1_BRK, S1_CHAIN = 'None', 'None'
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float', 'void', 'const']:
        now_memory_value['scope_num'] += 1  # 语义
        now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
        syntax_tree.append('-' * deep + '声明语句')
        declarative_statement(deep + 4)
        now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
    elif token in token_map.keys() and token_map[token] in ['if', 'for', 'while', 'do', 'return', 'break', 'continue']:
        now_memory_value['scope_num'] += 1  # 语义
        now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
        S1_BRK, S1_CHAIN = loop_execution_statement(deep + 4)
        now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
    elif token in token_map.keys() and token_map[token] in ['{']:
        S1_BRK, S1_CHAIN = loop_compound_statement(deep + 4)
    elif token in token_map.keys() and token_map[token] in ['ident']:
        now_memory_value['scope_num'] += 1  # 语义
        now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
        data_processing_statement(deep)  # 原没有
        now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
    return S1_BRK, S1_CHAIN


def loop_if_statement__(deep, C_CHAIN, T_CHAIN):
    #    print('-'*deep+'循环if语句分析')
    if token in token_map.keys() and token_map[token] in ['if']:
        syntax_tree.append('-' * deep + 'else if')
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['(']:
            match(token_map[token])
            PLACE_boolean_expression = boolean_expression(deep)
            if token in token_map.keys() and token_map[token] in [')']:
                E_FC = len(quaternion_list)
                gencode('jz', PLACE_boolean_expression, '_', 0)
                C1_CHAIN = merge(C_CHAIN, E_FC)
                match(token_map[token])
                if token in token_map.keys() and token_map[token] in ['{']:  # while不用改
                    loop_compound_statement(deep)
                else:
                    now_memory_value['scope_num'] += 1  # 语义
                    now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
                    loop_statement(deep)
                    now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
                tempf, tempt = loop_if_statement_(deep, C1_CHAIN, T_CHAIN)
                if tempf != 'None':
                    C1_CHAIN = tempf
                T1_CHAIN = T_CHAIN
                if tempt != 'None':
                    T1_CHAIN = tempt
                S1_CHAIN = len(quaternion_list)
                gencode('j', '_', '_', 0)
                if tempf == 'None' and tempt != 'None':
                    S_CHAIN = S1_CHAIN
                else:
                    S_CHAIN = merge(C1_CHAIN, S1_CHAIN)
        return S_CHAIN, T1_CHAIN
    else:
        syntax_tree.append('-' * deep + 'else')
        backpatch(C_CHAIN, len(quaternion_list))
        if token in token_map.keys() and token_map[token] in ['{']:  # while不用改
            compound_statement(deep)
        else:
            now_memory_value['scope_num'] += 1  # 语义
            now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
            loop_statement(deep)
            now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
        return 'None', T_CHAIN


def loop_if_statement_(deep, C_CHAIN, T_CHAIN=0):
    if token in token_map.keys() and token_map[token] in ['else']:
        C1_CHAIN = len(quaternion_list)
        gencode('j', '_', '_', 0)
        if T_CHAIN != 0:
            C1_CHAIN = merge(T_CHAIN, C1_CHAIN)
        match(token_map[token])
        return loop_if_statement__(deep, C_CHAIN, C1_CHAIN)
    else:
        return 'None', 'None'


def loop_if_statement(deep):
    syntax_tree.append('-' * deep + 'if语句')
    if token in token_map.keys() and token_map[token] in ['if']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['(']:
            match(token_map[token])
            PLACE_boolean_expression = boolean_expression(deep)
            if token in token_map.keys() and token_map[token] in [')']:
                E_FC = len(quaternion_list)
                gencode('jz', PLACE_boolean_expression, '_', 0)
                C_CHAIN = E_FC
                match(token_map[token])

                if token in token_map.keys() and token_map[token] in ['{']:  # while不用改
                    loop_compound_statement(deep)
                else:
                    now_memory_value['scope_num'] += 1  # 语义
                    now_memory_value['post'] += '/' + str(now_memory_value['scope_num'])  # 语义
                    loop_statement(deep)
                    now_memory_value['post'] = '/'.join(now_memory_value['post'].split('/')[0:-1])  # 语义
                tempf, tempt = loop_if_statement_(deep, C_CHAIN)
                if tempf != 'None':
                    C_CHAIN = tempf
                if quaternion_list[E_FC][-1] == 0:
                    backpatch(C_CHAIN, len(quaternion_list))
                elif tempf != 'None':
                    backpatch(tempf, len(quaternion_list))
                if tempt != 'None':
                    backpatch(tempt, len(quaternion_list))
        syntax_tree.append('-' * deep + 'if语句结束')
        return len(quaternion_list)


def for_statement(deep):
    syntax_tree.append('-' * deep + 'for语句')
    if token in token_map.keys() and token_map[token] in ['for']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['(']:
            match(token_map[token])
            E1_PLACE = assignment_expression(deep)  # 有其他合法格式就写判断
            if token in token_map.keys() and token_map[token] in [';']:
                F_TEST = len(quaternion_list)
                match(token_map[token])
                E2_PLACE = boolean_expression(deep)  # 布尔表达式
                if token in token_map.keys() and token_map[token] in [';']:
                    A_CHAIN = len(quaternion_list)
                    gencode('jz', E2_PLACE, '_', 0)
                    A_RIGHT = len(quaternion_list)
                    gencode('j', '_', '_', 0)
                    A_INC = len(quaternion_list)
                    A_TEST = F_TEST
                    match(token_map[token])
                    assignment_expression(deep)  # 有其他合法格式就写判断
                    if token in token_map.keys() and token_map[token] in [')']:
                        gencode('j', '_', '_', A_TEST)
                        backpatch(A_RIGHT, len(quaternion_list))
                        B_CHAIN = A_CHAIN
                        B_INC = A_INC
                        match(token_map[token])
                        S1_BRK, S1_CHAIN = loop_statement(deep)
                        if S1_CHAIN != 'None':
                            backpatch(S1_CHAIN, len(quaternion_list))
                        gencode('j', '_', '_', B_INC)
                        S_CHAIN = B_CHAIN
                        backpatch(S_CHAIN, len(quaternion_list))  # 原没有
    syntax_tree.append('-' * deep + 'for语句结束')
    return S_CHAIN


def while_statement(deep):
    syntax_tree.append('-' * deep + 'while语句')
    if token in token_map.keys() and token_map[token] in ['while']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['(']:
            match(token_map[token])
            E_PLACE = len(quaternion_list)
            PLACE_boolean_expression = boolean_expression(deep)  # 布尔表达式
            if token in token_map.keys() and token_map[token] in [')']:
                E_FC = len(quaternion_list)
                gencode('jz', PLACE_boolean_expression, '_', 0)
                match(token_map[token])
                loop_statement(deep)
                gencode('j', '_', '_', E_PLACE)
                backpatch(E_FC, len(quaternion_list))
    syntax_tree.append('-' * deep + 'while语句结束')
    return E_FC


def do_while_statement(deep):
    syntax_tree.append('-' * deep + 'do while语句')
    if token in token_map.keys() and token_map[token] in ['do']:
        match(token_map[token])
        D_HEAD = len(quaternion_list)
        loop_compound_statement(deep)
        if token in token_map.keys() and token_map[token] in ['while']:
            match(token_map[token])
            if token in token_map.keys() and token_map[token] in ['(']:
                match(token_map[token])
                PLACE_boolean_expression = boolean_expression(deep)  # 布尔表达式
                if token in token_map.keys() and token_map[token] in [')']:
                    gencode('jnz', PLACE_boolean_expression, '_', D_HEAD)
                    E_FC = len(quaternion_list)
                    gencode('j', '_', '_', 0)
                    match(token_map[token])
                    if token in token_map.keys() and token_map[token] in [';']:
                        match(token_map[token])
                    backpatch(E_FC, len(quaternion_list))
    syntax_tree.append('-' * deep + 'do while语句结束')
    return E_FC


def function_definition_parameter_(deep):
    if token in token_map.keys() and token_map[token] in [',']:
        match(token_map[token])
        function_definition_parameter(deep)


def function_definition_parameter(deep):
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float']:
        now_memory_value['function_param'].append(token_map[token])  # 语义
        VT_type = token_map[token]
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['ident']:
            function_param.append(token_information[i][-2])
            now_memory_value['variable'] = token_information[i][-2]  # 语义
            variable_insert(now_memory_value['variable'])  # 语义
            match(token_map[token])
            function_definition_parameter_(deep)


def function_definition_parameter_list(deep):
    if token in token_map.keys() and token_map[token] not in [')']:
        function_definition_parameter(deep)


def function_definition(deep):
    global function_param
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float', 'void']:
        now_memory_value['return'] = token_map[token]  # 语义
        FT_type = token_map[token]
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['ident']:
            now_memory_value['function'] = token_information[i][-2]  # 语义
            fun_name = now_memory_value['function']
            syntax_tree.append('-' * deep + fun_name)
            gencode(token_information[i][-2], '_', '_', '_')
            match(token_map[token])
            if token in token_map.keys() and token_map[token] in ['(']:
                match(token_map[token])
                function_definition_parameter_list(deep)
                if token in token_map.keys() and token_map[token] in [')']:
                    function_param_list[fun_name] = function_param
                    function_param = []
                    function_init(now_memory_value['function'])  # 语义
                    match(token_map[token])
                    compound_statement(deep)  # 复合语句
    syntax_tree.append('-' * deep + fun_name + '结束')


def function_block(deep):
    if token in token_map.keys() and token_map[token] in ['int', 'char', 'float', 'void']:
        function_definition(deep)
        function_block(deep)


def program_(deep):
    if token in token_map.keys() and token_map[token] in ['(']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in [')']:
            match(token_map[token])
            compound_statement(deep)  # 复合语句
            syntax_tree.append('main结束')
            quaternion_list.append(['sys', '_', '_', '_'])
            function_block(deep)


def program(deep):  # ok
    # print('-' * deep + '程序分析开始')
    while token in token_map.keys() and not ((token_map[token] in ['main'] or (
            token_map[token] in ['int', 'char', 'float', 'void'] and token_information[i + 1][-2] == 'main'))):
        syntax_tree.append('声明语句')
        declarative_statement(deep)
    if token in token_map.keys() and token_map[token] in ['main']:
        match(token_map[token])
        syntax_tree.append('main')
        program_(deep)
    elif token_map[token] in ['int', 'char', 'float', 'void']:
        match(token_map[token])
        if token in token_map.keys() and token_map[token] in ['main']:
            match(token_map[token])
            syntax_tree.append('main')
            program_(deep)
    if token_information[i][-2] != '#end#':
        error('语句错误')
        skip(1)
    # print('-' * deep + '程序分析结束')


def quaternion_optimize():
    optimize_list = {}
    for line in quaternion_list:
        for temp in line:
            if str(temp)[0] == '#' and str(temp) not in optimize_list:
                optimize_list[temp] = len(optimize_list)
    for i, line in enumerate(quaternion_list):
        for j, temp in enumerate(line):
            if str(temp)[0] == '#' and str(temp) in optimize_list:
                quaternion_list[i][j] = '$___t' + str(optimize_list[quaternion_list[i][j]])


def get_syntax_result(token_in):
    global token, i, ti, token_information, error_list, semantic_error_list, now_memory_value
    global quaternion_list, symbol_constant_list, symbol_variable_list, symbol_function_list, function_param_list, syntax_tree
    token_information = token_in
    token_information.append([token_information[-1][0] + 1, 0, 0, '#end#', -1])
    error_list = []
    semantic_error_list = []
    syntax_tree = []
    quaternion_list = [['OP', 'ARG1', 'ARG2', 'RESULT'], ['main', '_', '_', '_']]
    symbol_constant_list = {}
    symbol_variable_list = {}
    symbol_function_list = {'write': {'/0': [1, 'int', 1, 'most']}, 'read': {'/0': [1, 'most', 0]}}
    function_param_list = {}
    now_memory_value = {'post': '/0', 'function': None, 'function_param': [], 'return': None, 'return_value': None,
                        'variable': None, 'variable_type': [], 'operation': [], 'operation_result': [], 'scope_num': 0}
    ti = 0
    i = 0
    token = token_information[i][-1]
    program(0)
    quaternion_optimize()
    result = [error_list, semantic_error_list, quaternion_list, symbol_constant_list, symbol_variable_list,
              symbol_function_list, function_param_list, syntax_tree]
    return result


if __name__ == '__main__':
    code = open('C:/Users/YL139/Desktop/byyl/test/byxt/yffx_example/test0.1.txt', encoding='UTF-8').read()
    token_information, error_information = recognizedID(code)
    token_information.append([token_information[-1][0] + 1, 0, 0, '#end#', -1])
    global token, i
    start = 0
    i = 0
    token = token_information[i][-1]
    program(0)

    quaternion_optimize()
    [print(i, k) for i, k in enumerate(quaternion_list)]
    Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/zjdm.txt', mode='w', encoding='UTF-8')
    for i, k in enumerate(quaternion_list):
        # Note.write(str(i))
        # Note.write("\t")
        Note.write(str(k))
        # Note.write("\n")
    Note.close()

    # print(token_map)
