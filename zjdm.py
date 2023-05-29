from cffx import Lexer, MESSAGE, Error, SignTable
from PyQt5.QtCore import pyqtSignal


class Zjdmsc(MESSAGE):
    sinOut = pyqtSignal(list, Error, SignTable, dict)

    def __init__(self, filename='', text=''):
        super(Zjdmsc, self).__init__(filename, text)
        lexer = Lexer(filename, text)
        try:
            lexer.run()
        except Exception as e:
            print('lxer run', e)

        self.token = lexer.token  # token串
        self.index = 0
        self.error = lexer.error
        self.token_len = self.token.__len__()
        self.sign_table = lexer.sign_table  # 符号表的五元式
        self.log_info = []
        self.tab = 0
        self.quaternary = {}  # 四元式列表
        self.now_scope = ''  # 现在的范围
        self.now_quaternary = []  # 现在的四元式列表
        self.quaternary_list = []

    # 符号表
    def signtable(self, c):
        if c in [self.code['id'], self.code['string'], self.code['charRealNum'], self.code['constNum']]:
            return True
        return False

    def is_define(self, w, p, type_p='id'):
        result = False
        for i in self.sign_table:
            if i[0] == w and (i[2] == p or i[2] == 'global') and type_p == i[1]:
                result = True
                break
        return result

    # 获取下一个token值
    def token_next(self, back_num=1):
        line, word, code = None, None, None
        try:
            line, word, code = self.token[self.index]
        except KeyError:
            word = ''
        self.index += 1
        if back_num == 1:
            return word
        else:
            return line, word, code

    # 返回到上一token
    def token_redo(self):
        if self.index > 0:
            self.index -= 1

    # 合并链
    def merge(self, p1, p2):
        self.now_quaternary[p2][3] = p1
        return p2

    # 回填函数
    def backpatch(self, p, t):
        while self.now_quaternary[p][3] != 0:
            m = self.now_quaternary[p][3]
            self.now_quaternary[p][3] = t
            p = m
        self.now_quaternary[p][3] = t

    # 匹配下一个token是否为c,是返回True， 否则返回False,返回到上一token值
    def match_next(self, match_c, do_error=False, juge_other=False, log=True, pre_=False):
        result = ''
        line, word, code = self.token_next(3)
        s = "{:->" + str(self.tab + 2) + "s} match  {:s}\t(Line: {:d})"
        if word:
            if juge_other:
                if code == self.code[match_c]:
                    result = word
            else:
                if word == match_c:
                    result = word
        else:
            line = self.token[self.token_len - 1][0]
        if not result:
            if do_error:
                self._error("match error on %s not %s" % (word, match_c))
            self.token_redo()
        else:
            if log:
                self.log_info.append(s.format("", str(match_c), line))
        return result

    # 出错处理
    def _error(self, error_type=""):
        try:
            s = "Zjdmsc Error in %d Line (%s) after token %s" % (
                self.token[self.index - 2][0], error_type, self.token[self.index - 2][1])
            self.error.append(s)
        except Exception as e:
            print(e)

    # 修饰词
    def Modifier(self):
        c = self.token_next()
        if c not in self.modifier:  # 'const', 'static', 'register', 'auto', 'volatile', 'unsigned'
            self.token_redo()
            return False
        return True

    # 数据类型
    def sjlx(self, do_error=False):
        c = self.token_next()
        if c not in self.s_type:  # 'char', 'int', 'double', 'float', 'short', 'long', 'void'
            if do_error:
                self._error("match error on %s not type" % c)
            self.token_redo()
            return ''
        return c

    Temp_index = 0

    # 获取新结果，四元式的第四位
    def new_temp(self):
        result = '$___t' + str(self.Temp_index)
        self.Temp_index += 1
        return result

    # 表达式  <表达式> -> <因子> <项>
    def bds(self):
        result = self.yinzi()
        if result:
            result2 = self.item(result)
            if result2:
                return result2
        return result

    # <因子> -> <因式> <因式递归>
    def yinzi(self):
        result = self.yinshi()
        if result:
            result2 = self.yinshidigui(result)
            if result2:
                return result2
        return result

    # < 项 > -> + < 因子 > < 项 > | - < 因子 > < 项 > | ε
    def item(self, c):
        result = ''
        if self.match_next('+', pre_=True) or self.match_next('-', pre_=True):
            w = self.token[self.index - 1][1]  # 运算符
            result = self.yinzi()  # 运算对象2
            temp_ = self.new_temp()  # 结果
            self.now_quaternary.append([w, c, result, temp_])
            result = temp_
            result2 = self.item(result)
            if result2:
                return result2
        return result

    # < 因式 > -> ( < 表达式 > ) | < id > | < 数字 >| <fun_use>
    def yinshi(self):
        l, w, c = self.token_next(3)
        result = ''
        if c == self.code['id']:
            # 检查是否定义， 不存在报错
            if self.match_next('('):
                self.hssycslb()
                self.match_next(')')
                result = 'f_' + w
                self.now_quaternary.append(['CALL', w, '_', result])
                if not self.is_define(w, self.now_scope, 'fun'):
                    self._error("not define fun %s in %s" % (w, self.now_scope))
            else:
                if not self.is_define(w, self.now_scope):
                    self._error("not define %s in %s" % (w, self.now_scope))
            result = w
        elif self.signtable(c):  # 常量
            result = w
        else:
            if w == '(':
                result = self.bds()
                self.match_next(')', True)
            else:
                self._error("no exp")
                self.token_redo()
        return result

    # <因式递归> -> * <因式> <因式递归> | / <因式> <因式递归> | ε
    def yinshidigui(self, c):
        result = ''
        if self.match_next('*', pre_=True) or self.match_next('/', pre_=True):
            w = self.token[self.index - 1][1]
            result = self.yinshi()
            temp_ = self.new_temp()
            self.now_quaternary.append([w, c, result, temp_])
            result = temp_
            result2 = self.yinshidigui(result)
            if result2:
                return result2
        return result

    # < 右值 > -> < 表达式 > | { < 多个数据 >}
    def youzhi(self):
        return self.bds()

    # <赋初值> -> = <右值> | $
    def fuchuzhi(self, c):
        if self.match_next('=', pre_=True):
            self.now_quaternary.append(['=', self.youzhi(), '_', c])

    # < 声明 > -> < 修饰词 > < 类型 > < id > < 赋初值 >
    def declare(self):
        type_ = self.sjlx(self.Modifier())
        if type_:
            self.exp_whole(type_)
            self.many_declare(type_)
            return True
        return False

    def exp_whole(self, type_):
        w = self.match_next('id', True, True)
        self.fuchuzhi(w)
        if w:
            if self.is_define(w, self.now_scope):
                self._error("%s defined repeatedly in %s" % (w, self.now_scope))
            else:
                for index, i in enumerate(self.sign_table):
                    if i[0] == w and i[1] == 'id':
                        self.sign_table[index][3] = type_
                        self.sign_table[index][2] = self.now_scope
        self.many_declare(type_)

    #  {, exp_whole}
    def many_declare(self, type_):
        if self.match_next(',', pre_=True):
            self.exp_whole(type_)
            self.many_declare(type_)

    # < 声明语句 > -> < 声明 >;
    def smyj(self):
        if self.declare():
            self.match_next(';', True)
            return True
        return False

    # < 声明语句闭包 > -> < 声明语句 > < 声明语句闭包 > | ε
    def smyjbb(self):
        if self.smyj():
            self.smyjbb()

    # 函数定义， 函数声明， <函数声明>→<函数类型><标识符>(<函数声明形参列表>)
    def fun(self):
        type_ = self.sjlx(self.Modifier())
        if type_:
            w = self.match_next('id', do_error=True, juge_other=True)
            self.match_next('(', True)
            par_list = self.hssmcslb()
            for index, i in enumerate(self.sign_table):
                if i[0] == w and i[1] == 'id':
                    self.sign_table[index][1] = 'fun'
                    self.sign_table[index][2] = 'global'
                    self.sign_table[index][3] = type_
                    self.sign_table[index][4] = par_list
                    break
            self.match_next(')', True)
            if self.match_next('{'):  # 函数定义
                for index, i in enumerate(self.sign_table):
                    for j in par_list:
                        if i[0] == j[1] and i[1] == 'id':
                            self.sign_table[index][2] = self.now_scope
                            self.sign_table[index][3] = j[0]
                        break
                self.hsk()
                self.match_next('}', do_error=True)
                self.now_quaternary.append(['sys', '_', '_', '_'])
            else:
                if self.is_define(w, self.now_scope, 'fun'):
                    self._error("%s defined repeatedly in %s" % (w, self.now_scope))
                self.match_next(';', True)  # 函数声明

    # 函数使用参数列表
    def hssycslb(self):
        line, word, code = self.token_next(3)
        if self.signtable(code):
            if self.match_next(','):
                self.hssycslb()
                return True
        else:
            self.token_redo()
            return False

    # 函数声明参数列表 par {<desc><type><*><id><[num]><value init><，闭包>}
    def hssmcslb(self):
        type_ = self.sjlx(do_error=self.Modifier())
        list_p = []
        if type_:
            w = self.match_next('id', True, True)
            self.fuchuzhi(w)
            list_p = [(type_, w)]
            list_p += self.hssmcslbbb()
        return list_p

    # 函数声明参数列表闭包， {， par}
    def hssmcslbbb(self):
        list_p = []
        if self.match_next(',', pre_=True):
            list_p.append(self.hssmcslb())
            list_p += self.hssmcslbbb()
        return list_p

    # 函数块 :: <数据定义>  <其他语句> <return>
    def hsk(self):
        self.smyjbb()
        self.statement()

    # 语句
    def statement(self):
        while self.index < self.token_len:
            t = self.match_next('}')
            if t:  # {}内没有东西
                self.token_redo()
                break
            self.end_with_div()
            self.if_sta()
            self.for_sta()
            self.while_sta()
            self.do_while_sta()

    # 以分号结尾的语句
    def end_with_div(self):
        ind_old = self.index
        if self.match_next('id', juge_other=True, pre_=False):
            if self.match_next('('):
                self.index = ind_old
                self.hsdy()
            else:
                self.index = ind_old
                self.fzyj()
        else:
            # return 语句
            if self.match_next('return', pre_=False):
                result = self.bds()
                temp_ = self.new_temp()
                self.now_quaternary.append(['=', temp_, '_', result])
            self.match_next(';')

    # 函数调用
    def hsdy(self):
        w = self.match_next('id', True, True)
        self.match_next('(', True)
        temp = self.token_next()
        self.hssycslb()
        self.match_next(')', True)
        self.match_next(';', True)
        if not self.is_define(w, self.now_scope, 'fun'):
            self._error("not defien fun %s in %s" % (w, self.now_scope))
        temp_ = self.new_temp()
        # self.now_quaternary.append(['para', temp, '_', '_'])
        self.now_quaternary.append(['call', w, '_', temp])
        return temp

    # 赋值语句 <*><id><[]><value_init>;
    def fzyj(self):
        w = self.match_next('id', juge_other=True)
        if w:
            if not self.is_define(w, self.now_scope):
                self._error('not define %s in %s' % (w, self.now_scope))
            self.fuchuzhi(w)
            self.match_next(';', True)

    # if语句 if(bool_exp){statement}<else{statement}>
    def if_sta(self):
        if self.match_next('if', pre_=False):
            self.match_next('(', True)
            ok_pos, err_pos = self.bool_bds()
            self.match_next(')', True)
            self.match_next('{', True)
            self.now_quaternary[ok_pos][3] = len(self.now_quaternary)
            self.statement()
            self.match_next('}', True)
            self.now_quaternary[err_pos][3] = 1 + len(self.now_quaternary)
            if self.match_next('else', pre_=False):
                self.now_quaternary.append(['J', '_', '_', err_pos])
                l = len(self.now_quaternary)
                self.match_next('{', True)
                self.statement()
                self.match_next('}', True)
                self.now_quaternary[l - 1][3] = len(self.now_quaternary)

    #  # while 语句 while(bool_exp){statement} or while(bool_exp);
    def while_sta(self):
        if self.match_next('while', pre_=True):
            self.match_next('(', True)
            bool_start = len(self.now_quaternary)
            ok_pos, err_pos = self.bool_bds()
            self.now_quaternary[ok_pos][3] = len(self.now_quaternary)
            self.match_next(')', True)
            if self.match_next('{'):
                self.statement()
                self.match_next('}', True)
                self.now_quaternary.append(['J', '_', '_', bool_start])
                self.now_quaternary[err_pos][3] = len(self.now_quaternary)
            else:
                self.now_quaternary.append(['J', '_', '_', bool_start])
                self.now_quaternary[err_pos][3] = len(self.now_quaternary)
                self.match_next(';', True)

    def do_while_sta(self):
        if self.match_next('do', pre_=True):
            l = len(self.now_quaternary)
            if self.match_next('{'):
                self.statement()
                self.match_next('}', True)
                a = len(self.now_quaternary)
                if self.match_next('while', pre_=True):
                    self.match_next('(', True)
                    ok_pos, err_pos = self.bool_bds()
                    self.now_quaternary[ok_pos][3] = l
                    self.now_quaternary[err_pos][3] = len(self.now_quaternary)
                    self.match_next(')', True)
                    self.match_next(';', True)
                else:
                    self.now_quaternary.append(['j', '_', '_', a])
            else:
                self.now_quaternary.append(['j', '_', '_', l])
                self.match_next(';', True)

    # for 语句 for(<赋值语句><,赋值语句闭包>;<bool_exp>;<后缀表达式>){statement}
    def for_sta(self):
        if self.match_next('for', pre_=True):
            self.match_next('(', True)
            self.for_1()
            bool_start = len(self.now_quaternary)
            self.match_next(';', True)
            ok_pos, err_pos = self.bool_bds()
            self.match_next(';', True)
            start_pos = len(self.now_quaternary)
            self.for_1()
            self.now_quaternary.append(['J', '_', '_', bool_start])  # 跳转到BOOL表达式
            self.match_next(')', True)
            self.match_next('{', True)
            self.now_quaternary[ok_pos][3] = len(self.now_quaternary)  # bool表达式正确进入循环
            self.statement()
            self.now_quaternary.append(['J', '_', '_', start_pos])  # 跳转到后缀表达式开始
            self.now_quaternary[err_pos][3] = len(self.now_quaternary)  # bool表达式错误跳出循环
            self.match_next('}', True)

    # for语句中的第一部分
    def for_1(self):
        w = self.match_next('id', juge_other=True, pre_=True)
        if w:
            self.fuchuzhi(w)
            # self.for_1_bb()

    # for语句中的第一部分闭包
    def for_1_bb(self):
        if self.match_next(';', pre_=True):
            self.for_1()

    # 多个bool表达式 && <bool_exp> or || <bool_exp>
    def bool_bdss(self, ok_pos, err_pos):
        l = len(self.now_quaternary)
        if self.match_next('&&', pre_=True) or self.match_next('||', pre_=True):
            if self.token[self.index - 1][1] == '&&':
                self.now_quaternary[l - 1][3] = err_pos
                self.now_quaternary[l - 2][3] = ok_pos
                self.now_quaternary[ok_pos][3] = l
                ok_pos = l
                ok_pos, err_pos = self.bool_bds(ok_pos, err_pos)
            else:
                self.now_quaternary[l - 2][3] = ok_pos
                self.now_quaternary[l - 1][3] = err_pos
                self.now_quaternary[err_pos][3] = l
                err_pos = l + 1
                ok_pos, err_pos = self.bool_bds(ok_pos, err_pos)
        return ok_pos, err_pos

    # bool 表达式 :: <exp> <>|<|==|!=|> <exp>
    def bool_bds(self, ok_pos=0, err_pos=0):  # ok_pos,err_pos当前四元式的NXQ（第几条四元式）
        have_k = False
        have_not = False
        if self.match_next('!', pre_=True):
            have_not = True
        if self.match_next('(', pre_=True):
            have_k = True
        result1 = self.bds()  # 四元式第二位
        w = self.token_next()
        if w in self.logic_sign:  # '>', '<', '==', '!=', '>=', '<=', '&&', '||'
            result2 = self.bds()  # 四元式第三位
            if have_k:
                self.match_next(')', True)
            self.now_quaternary.append(['J' + w, result1, result2, ok_pos])
        else:
            self.token_redo()
            self.now_quaternary.append(['JNZ', result1, '_', ok_pos])
        self.now_quaternary.append(['J', '_', '_', err_pos])
        if ok_pos == 0 and err_pos == 0:
            ok_pos = len(self.now_quaternary) - 2
            err_pos = len(self.now_quaternary) - 1
        if have_not:
            ok_pos, err_pos = err_pos, ok_pos
        ok_pos_, err_pos_ = self.bool_bdss(ok_pos, err_pos)
        return ok_pos_, err_pos_

    def zjdm_start(self):
        while self.index < self.token_len - 1:
            self.now_quaternary = []
            self.tab = 0
            if self.match_next(';', log=False):
                continue
            ind_old = self.index
            if self.sjlx(self.Modifier()):
                w = self.match_next('id', True, True, log=False)
                #  <desc><type><*>id
                if self.match_next('(', log=False):  # 函数
                    self.index = ind_old
                    self.now_scope = w
                    self.fun()
                    self.quaternary.update({self.now_scope: self.now_quaternary})
                    self.quaternary_list.append(self.now_quaternary)
                else:  # 数据定义s
                    self.index = ind_old
                    self.now_scope = 'global'
                    self.smyj()
                    self.quaternary.update({self.now_scope: self.now_quaternary})
                    self.quaternary_list.append(self.now_quaternary)

    def run(self):  # 捕获异常
        try:
            self.zjdm_start()
            self.sinOut.emit(self.log_info, self.error, self.sign_table, self.quaternary)
        except Exception as e:
            print("run", e)


if __name__ == '__main__':
    zjdm = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/csyl/test1.4.txt")
    zjdm.run()

    quaternary_list = zjdm.now_quaternary
    Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/zjdm.txt', mode='w', encoding='UTF-8')
    for i, k in enumerate(quaternary_list):
        Note.write(str(i))
        Note.write('\t')
        Note.write(str(k))
        Note.write('\n')
        print(k)
    Note.close()

    # print(zjdm.sign_table)
    fhb = zjdm.sign_table
    Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/sign_table.txt', mode='w', encoding='UTF-8')
    for j, l in enumerate(fhb):
        Note1.write(str(l))
        Note1.write('\n')
    Note1.close()

    # keys = list(zjdm.quaternary.keys())
    # for k in keys:  # 输出四元式
    #     for index, i in enumerate(zjdm.quaternary[k]):
    #         print(index, '\t', i)
