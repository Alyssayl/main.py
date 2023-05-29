from PyQt5.QtCore import QThread, pyqtSignal


#  Token串
class Token(list):
    """
    (LineNo, word, code)  # code 种别码
    """
    def __init__(self, seq=()):
        super(Token, self).__init__(seq)
        pass


#  符号表
class SignTable(list):
    """
    (word, type_p, scope, type, others)
    """

    def __init__(self, seq=()):
        super(SignTable, self).__init__(seq)

    def append(self, object_p):
        item = list(object_p)

        t = 5-len(item)
        for i in range(0, t):
            item += ['']
        try:
            self.remove(item)
        except ValueError:
            pass
        super(SignTable, self).append(item)


class Error(list):
    def __init__(self, seq=()):
        super(Error, self).__init__(seq)


class MESSAGE(QThread):
    code = {  # 内码表
        'char': 1,
        'double': 2,
        'enum': 3,
        'float': 4,
        'int': 5,
        'long': 6,
        'short': 7,
        'signed': 8,
        'struct': 9,
        'union': 10,
        'unsigned': 11,
        'void': 12,
        'for': 13,
        'do': 14,
        'while': 15,
        'continue': 16,
        'if': 17,
        'else': 18,
        'goto': 19,
        'switch': 20,
        'case': 21,
        'default': 22,
        'return': 23,
        'auto': 24,
        'extern': 25,
        'register': 26,
        'static': 27,
        'const': 28,
        'sizeof': 29,
        'typdef': 30,
        'volatile': 31,
        'break': 32,  # 关键字
        '+': 33,
        '-': 34,
        '*': 35,
        '/': 36,
        '=': 37,
        '|': 38,
        '&': 39,
        '!': 40,
        '>': 41,
        '<': 42,
        '&&': 43,
        '++': 44,
        '--': 45,
        '+=': 46,
        '-=': 47,
        '*=': 48,
        '/=': 49,
        '==': 50,
        '|=': 51,
        '&=': 52,
        '!=': 53,
        '>=': 54,
        '<=': 55,
        '>>=': 56,
        '<<=': 57,
        '||': 58,
        '%': 59,  # 运算符
        '>>': 60,
        '<<': 61,
        ',': 62,
        '(': 63,
        ')': 64,
        '{': 65,
        '}': 66,
        '[': 67,
        ']': 68,
        ';': 69,
        '//': 70,
        '/*': 71,
        '*/': 72,
        ':': 73,
        '.': 74,
        '\\': 75,  # 界符
        'constNum': 76,
        'charRealNum': 77,
        'string': 78,
        'id': 79
    }
    basic_arithmetic_operator = {  # 符号表
        '+', '-', '*', '=', '|', '&', '>', '<', '!', '%'
    }
    delimiters = {  # 界符表
        ';', ',', ':', '(', ')', '{', '}', '[', ']', '<', '>', '.', '\\'
    }
    error_type = ['miss', 'more', 'no_code', 'no_type', 'no_keyWord']
    error_info = {  # 错误信息格式列表
        error_type[0]: "错误 %d: 第 %d 行缺少  %s  ;",
        error_type[1]: "错误 %d: 第 %d 行多余  %s  ;",
        error_type[2]: "错误 %d: 第 %d 行不能识别的字符  %s  ;",
        error_type[3]: "错误 %d: 第 %d 行没有 %s 的类型",
        error_type[4]: ""
    }
    modifier = ['const', 'static', 'register', 'auto', 'volatile', 'unsigned']
    s_type = ['char', 'int', 'double', 'float', 'short', 'long']
    logic_sign = ['>', '<', '==', '!=', '>=', '<=', '&&', '||']
    last_keyword_code = 32
    sinOut = pyqtSignal(Token, Error, SignTable)

    def __init__(self, filename='', text=''):
        super(MESSAGE, self).__init__()
        if filename:
            self.file_name = filename
            self.__load_file()
        elif text:
            self.wenjian = text.strip()
        else:
            raise Exception("No Anything to complier")
        self.neicun_len = len(self.wenjian)  # 内存长度
        self.token = Token()  # Token表
        self.error = Error()  # 错误信息
        self.sign_table = SignTable()  # 符号表

    # 读取文件内容到 wenjian
    def __load_file(self):
        with open(self.file_name, "r", encoding='utf8') as f:
            self.wenjian = f.read()

    def run(self):
        pass

    def _exit_message(self):
        try:
            self.sinOut.emit(self.token, self.error, self.sign_table)
        except Exception as e:
            raise e


# 词法分析
class Lexer(MESSAGE):
    def __init__(self, filename='', text=''):
        super(Lexer, self).__init__(filename, text)
        self.current_line = 1
        self.current_row = 0

    def Start_with_alpha(self):
        index = self.current_row
        while self.current_row < self.neicun_len:
            ch = self.wenjian[self.current_row]
            if not (ch.isalpha() or ch.isdigit() or ch == '_'):  # 其他字符
                break
            self.current_row += 1
        word = self.wenjian[index: self.current_row]
        try:
            t = self.code[word]  # 关键字
        except KeyError:
            t = self.code['id']
            self.sign_table.append((word, 'id'))
        self.token.append((self.current_line, word, t))

        self.current_row -= 1

    def START_with_number(self):
        index = self.current_row

        # 获取下一个
        def get_next_char():
            if (self.current_row + 1) < self.neicun_len:
                self.current_row += 1
                return self.wenjian[self.current_row]
            return None

        # 是否为数字
        def isnum(STATE):
            if STATE == 1:
                while STATE == 1:
                    c = get_next_char()
                    if c:
                        if c.isdigit():
                            pass
                        elif c == '.':
                            STATE = 2
                        elif c == 'e' or c == 'E':
                            STATE = 4
                        else:
                            STATE = 7
                    else:
                        self.current_row += 1
                        STATE = 7
            if STATE == 2:
                while STATE == 2:
                    c = get_next_char()
                    if c.isdigit():
                        STATE = 3
                    else:
                        STATE = 11  # . 多余
            if STATE == 3:
                while STATE == 3:
                    c = get_next_char()
                    if c.isdigit():
                        pass
                    elif (c == 'e') or (c == 'E'):
                        STATE = 4
                    else:
                        STATE = 7
            if STATE == 4:
                while STATE == 4:
                    c = get_next_char()
                    if c.isdigit():
                        STATE = 6
                    elif (c == '+') or (c == '-'):
                        STATE = 5
                    else:
                        STATE = 12
            if STATE == 5:
                while STATE == 5:
                    c = get_next_char()
                    if c.isdigit():
                        STATE = 6
                    else:
                        STATE = 13
            if STATE == 6:
                while STATE == 6:
                    c = get_next_char()
                    if not c.isdigit():
                        STATE = 7
            if STATE == 9:
                while STATE == 9:
                    c = get_next_char()
                    if c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f'):
                        STATE = 10
                    else:
                        STATE = 14
            if STATE == 10:
                while STATE == 10:
                    c = get_next_char()
                    if not (c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f')):
                        STATE = 7
            # 错误判断
            if STATE == 7:
                return True  # 没有错误
            elif STATE == 11:  # error . 多余
                self.error.append((1, self.current_line, '.'))
                self.current_row -= 1
                pass
            elif STATE == 12:  # error E/e 多余
                self.error.append((1, self.current_line, 'E/e'))
                self.current_row -= 1
                pass
            elif STATE == 13:  # error +/- 多余
                self.error.append((1, self.current_line, '+/-'))
                self.current_row -= 1
                pass
            elif STATE == 14:  # error x/X 多余
                self.error.append((1, self.current_line, 'x/X'))
                self.current_row -= 1
            return False

        if self.wenjian[self.current_row] == '0':
            ch = get_next_char()
            if (ch == 'x') or (ch == 'X'):  # 0x 0X
                state = 9
            elif ch.isdigit():
                state = 1
            else:
                state = 7  # 结束
        else:
            state = 1
        isnum(state)
        word = self.wenjian[index:self.current_row]
        self.token.append((self.current_line, word, self.code['constNum']))
        self.sign_table.append((word, 'constNum'))
        self.current_row -= 1

    def SIGN_char(self):
        if (self.current_row + 1) < self.neicun_len:
            word = self.wenjian[self.current_row + 1]  # 超前检测
            if word != '\n' and self.current_row < self.neicun_len - 2:
                if self.wenjian[self.current_row + 2] == '\'':  # 超前 2位 检测
                    self.token.append((self.current_line, word, self.code['charRealNum']))
                    word = word
                    self.sign_table.append((word, 'char'))
                    self.current_row += 2
                else:
                    self.error.append((0, self.current_line, '\''))
                    # 错误 缺少 ’
            else:
                pass
                self.error.append((1, self.current_line, '\''))
                # 错误 多余 ‘
        else:
            pass

    def SIGN_string(self):
        self.current_row += 1
        index = self.current_row
        flag = 0
        while self.current_row < self.neicun_len:
            if self.wenjian[self.current_row] == '\"':
                word = self.wenjian[index:self.current_row]
                self.token.append((self.current_line, word, self.code['string']))
                word = word
                self.sign_table.append((word, 'string'))
                break
            elif self.wenjian[self.current_row] == '\n':
                flag = 1
                break
            else:
                self.current_row += 1
        if flag == 1:
            # 错误 多余"
            self.error.append((1, self.current_line, '\"'))
            self.current_row = index  # 回到原来位置

    def SIGN_multi(self):
        self.current_row += 1
        ch = self.wenjian[self.current_row]
        if ch == '*':  # /*
            while self.current_row < self.neicun_len - 1:
                if self.wenjian[self.current_row] == '\n':
                    self.current_line += 1
                # 超前检测
                if not (self.wenjian[self.current_row] == '*' and self.wenjian[self.current_row + 1] == '/'):
                    self.current_row += 1
                else:
                    self.current_row += 1
                    break
        elif ch == '/':  # //
            while self.current_row < self.neicun_len - 1:
                if self.wenjian[self.current_row + 1] != '\n':  # 超前检测
                    self.current_row += 1
                else:
                    break
        elif ch == '=':  # /=
            word = self.wenjian[self.current_row - 1:self.current_row + 1]
            self.token.append((self.current_line, word, self.code['/=']))
        else:  # / 除法
            self.current_row -= 1
            word = self.wenjian[self.current_row]
            self.token.append((self.current_line, word, self.code['/']))

    def START_with_ssysf(self):
        ch = self.wenjian[self.current_row]
        index = self.current_row

        def next_is_sign(c):
            if self.current_row + 1 < self.neicun_len:
                if self.wenjian[self.current_row + 1] == c:
                    self.current_row += 1
                    return True
            return False

        if ch == '%':
            next_is_sign('=')
        elif ch == '!':
            next_is_sign('=')
        elif ch == '=':
            next_is_sign(ch)
        elif (ch == '+') or (ch == '-'):
            if next_is_sign('=') or next_is_sign(ch):
                pass
        elif ch == '*':
            next_is_sign('=')
        elif ch == '|':
            if next_is_sign('=') or next_is_sign("|"):
                pass
        elif ch == '&':
            if next_is_sign('=') or next_is_sign("&"):
                pass
        elif ch == '>':
            if next_is_sign('=') or (next_is_sign(">") and next_is_sign("=")):
                pass
        elif ch == '<':
            if next_is_sign('=') or (next_is_sign('<') and next_is_sign('=')):
                pass
        else:
            return
        word = self.wenjian[index:self.current_row + 1]
        self.token.append((self.current_line, word, self.code[word]))

    def START_with_pre(self):
        # 预编译 替换字符串
        index = self.current_row
        while self.wenjian[self.current_row] != ' ':
            self.current_row += 1
        word = self.wenjian[index:self.current_row]
        self.token.append((self.current_line, word, self.ISCHAR))
        self.sign_table.append((word, 'pre'))

    def START_with_delimiter(self):  # 分隔符
        word = self.wenjian[self.current_row]
        self.token.append((self.current_line, word, self.code[word]))

    def Scanner(self):
        self.current_row = 0
        while self.current_row < len(self.wenjian):
            ch = self.wenjian[self.current_row]
            if not (ch == ' ' or ch == '\t'):
                if ch == '\n' or ch == '\r\n':
                    self.current_line += 1
                elif ch.isalpha() or ch == '_':  # 关键字 标识符
                    self.Start_with_alpha()
                elif ch.isdigit():  # 数字
                    self.START_with_number()
                elif ch == '/':  # 注释 或 除法
                    self.SIGN_multi()
                elif ch == '#':  # #
                    pass
                elif ch == '\'':  # 字符
                    self.SIGN_char()
                elif ch == '\"':  # 字符串
                    self.SIGN_string()
                elif ch in self.basic_arithmetic_operator:  # 算数运算符
                    self.START_with_ssysf()
                elif ch in self.delimiters:
                    self.START_with_delimiter()
                else:
                    self.error.append((2, self.current_line, ch))
                    # 错误 无法识别的符号
            self.current_row += 1

    def run(self):
        self.Scanner()
        self._exit_message()
        self.quit()


if __name__ == '__main__':
    lexer = Lexer(filename="C:/Users/YL139/Desktop/byyl/test/byxt/zjdm_example/test1.3.txt")
    lexer.run()
    Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/cffxjg.txt', mode='w', encoding='UTF-8')
    for i, k in enumerate(lexer.token):
        Note.write(str(k))
        Note.write('\n')
        print(k)
    Note.close()
    error = 'This code has no errors!'
    if lexer.error:
        Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/cffx_error.txt', mode='w', encoding='UTF-8')
        for i, k in enumerate(lexer.error):
            print(k)
            Note1.write(str(k))
            Note1.write('\n')
        Note1.close()
    else:
        Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/cffx_error.txt', mode='w', encoding='UTF-8')
        Note1.write(str(error))
        Note1.close()
