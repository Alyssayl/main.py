class cifafenxi:
    def __init__(self, data):
        self.data = data.split('\n')  # 以换行符分出文本，一行一行读入
        self.gjz = {  # 关键字
            'char': 1, 'int': 2, 'float': 3, 'break': 4, 'const': 5, 'return': 6,
            'void': 7, 'continue': 8, 'do': 9, 'while': 10, 'if': 11, 'else': 12,
            'for': 13, 'auto': 14, 'double': 15, 'long': 16, 'short': 17, 'switch': 18,
            'case': 19, 'signed': 20, 'sizeof': 21, 'static': 22, 'typedef': 23, 'volatile': 24,
            'register': 25, 'unsigned': 26, 'default': 27, 'enum': 28, 'struct': 29, 'union': 30,
            'goto': 31, 'extern': 32, 'main': 33
        }
        self.jiefu = {  # 界符
            '{': 201, '}': 202, ';': 203, ',': 204, ':': 206
        }
        self.yunsuanfu = {  # 运算符
            '(': 101, ')': 102, '[': 103, ']': 104, '!': 105, '*': 106, '/': 107, '%': 108,
            '+': 109, '-': 110, '<': 111, '<=': 112, '>': 113, '>=': 114, '==': 115, '!=': 116,
            '&&': 117, '||': 118, '=': 119, '+=': 120, '-=': 121, '*=': 122, '/=': 123,
            '++': 124, '--': 125, '%=': 126, '&': 127, '|': 128, '^': 129
        }
        self.fenge = {
            '\n': 250, '\t': 251, '\r': 252
        }
        """
        十进制数：410
        二进制：402
        八进制数：408
        十六进制数：416
        小数：800
        科学记数法：806
        字符：500
        字符串：600
        标识符：700
        """
        self.error_char = ['@', '$', '#']  # 非法字符
        self.cur_str = ''  # 记录当前识别到的串
        self.status = 0  # 记录当前状态
        self.result = ''  # 保存最后的所有分析结果
        self.error_list = ''  # 保存报错的信息
        self.line_index = 1  # 记录行数
        self.cur_line = 1  # 当前行数
        self.da = 0  # 用来判断{}是否配对
        self.zhong = 0  # 用来判断[]是否配对
        self.xiao = 0  # 用来判断()是否配对
        self.daw = []  # 用来记录{}的位置
        self.zhongw = []  # 用来记录[]的位置
        self.xiaow = []  # 用来记录()的位置

    def gjz_or_bsf(self, bit):
        """
        识别关键词和标识符
        """
        if self.status == 0:
            self.cur_line = self.line_index
        if self.cur_line == self.line_index:  # 在统一代码行内判断
            if 'a' <= bit.lower() <= 'z':
                self.status = 1  # 以字母开头时，状态status==1
                self.cur_str += bit  # 将识别到的字符存入到串中
                return 1
            elif bit == '_':  # 以下划线开头时，状态status==1
                self.status = 1
                self.cur_str += bit  # 将识别到的字符存入到串中
                return 1
            elif self.status == 1:  # 不能以数字开头，所以前提是状态为1（即以字母和下划线开头）
                if '1' <= bit <= '9':
                    self.cur_str += bit  # 将识别到的字符存入到串中
                    return 1
                if bit in self.error_char:
                    self.status = 10  # 识别过程中有含有不能识别的@、$、#时，状态变为10，利于区分
                    self.cur_str += bit  # 将识别到的字符存入到串中
                    return 1
                else:
                    self.status = 0  # 识别完后，将status归零
                    if self.cur_str in list(self.gjz.keys()):  # 识别到的串是关键字时，保存到result中，等待后续输出
                        self.result = self.result + str(self.gjz[self.cur_str]) + '\t' + self.cur_str + '\n'
                    else:  # 识别到的串是任意标识符时，保存到result中，等待后续输出
                        self.result = self.result + '700\t' + self.cur_str + '\n'
                    self.cur_str = ''  # 识别完后，将cur_str归零
                    return 0
        else:
            self.status = 0  # 识别完后，将status归零
            if self.cur_str in list(self.gjz.keys()):  # 识别到的串是关键字时，保存到result中，等待后续输出
                self.result = self.result + str(self.gjz[self.cur_str]) + '\t' + self.cur_str + '\n'
            else:  # 识别到的串是任意标识符时，保存到result中，等待后续输出
                self.result = self.result + '700\t' + self.cur_str + '\n'
            self.cur_str = ''  # 识别完后，将cur_str归零
            return 0

    def zhengshu(self, bit):
        """
        识别整数
        """
        if self.status == 0:
            self.cur_line = self.line_index
        if self.cur_line == self.line_index:
            if bit == '0' and self.status == 0:  # 0单独作为一种情况
                # 如果当前字符是0，并且状态status为0（即前面没有其他字符，开头数字为0）
                self.status = 6  # 将状态status标记为6，跳转到下一个状态进行小数和其他进制数的判断
                self.cur_str += bit
                return 1
            elif '1' <= bit <= '9':  # 若当前字符是1~9的数字，状态记为2
                self.status = 2
                self.cur_str += bit
                return 1
            elif bit in ['e', 'E']:  # 若当前字符是e或E，状态记为2（即出现科学计数法）
                self.status = 2
                self.cur_str += bit
                return 1
            elif bit == '0' and self.status == 2:  # 如果当前字符是0，并且状态status为2（即前面有其他字符）
                self.cur_str += bit
                return 1
            elif self.status == 2:
                if bit == '.':  # 当前字符是小数点时，状态标记为7
                    self.status = 7
                    self.cur_str += bit
                    return 1
                if bit not in [' ', ',', ';'] + list(self.yunsuanfu.keys()) + list(self.jiefu.keys()):  # 数据错误的情况
                    self.cur_str += bit
                    self.status = 8  # 若当前字符不属于空格，逗号，分号，运算符，界符，则状态记为8
                    return 1
                if 'e' in self.cur_str or 'E' in self.cur_str:
                    self.result = self.result + '806\t' + self.cur_str + '\n'
                else:
                    self.result = self.result + '410\t' + self.cur_str + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
        else:
            if 'e' in self.cur_str or 'E' in self.cur_str:
                self.result = self.result + '806\t' + self.cur_str + '\n'
            else:
                self.result = self.result + '410\t' + self.cur_str + '\n'
            self.status = 0
            self.cur_str = ''
            return 0

    def xs_or_kxjsf(self, bit):
        """
        识别小数和科学记数法
        """
        if self.status == 6:  # 开头数字为0
            if bit == '.':  # 整数部分为0的小数
                self.cur_str += bit
                self.status = 7
                return 1
            if bit == 'x':
                self.cur_str += bit
                self.status = 11  # 进行十六进制数的判断，状态为11
                return 1
            if '1' <= bit <= '7':
                self.cur_str += bit
                self.status = 12  # 进行八进制数的判断
                return 1
            if '7' < bit <= '9':  # 小数
                self.cur_str += bit
                self.status = 8
                return 1
            else:  # 单个0的情况
                self.status = 0
                self.result = self.result + '410\t' + self.cur_str + '\n'
                self.cur_str = ''
                return 0
        if self.status == 7:  # 识别小数部分
            if self.cur_line == self.line_index:
                if '0' <= bit <= '9' or bit in ['e', 'E']:
                    self.cur_str += bit
                    return 1
                if bit == '.':
                    self.cur_str += bit
                    self.status = 8
                    return 1
                elif self.cur_str[-1] in ['e', 'E'] and bit in ['+', '-']:
                    self.cur_str += bit
                    return 1
                elif bit not in [' ', ',', ';'] + list(self.yunsuanfu.keys()) + list(self.jiefu.keys()):  # 识别错误
                    self.cur_str += bit
                    self.status = 8
                    return 1
                else:
                    if self.cur_str[-1] == '.':  # 最后一个元素是'.'/小数点
                        self.cur_str += bit
                        self.status = 8
                        return 1
                    if 'e' not in self.cur_str and 'E' not in self.cur_str:
                        self.result = self.result + '800\t' + self.cur_str + '\n'
                    else:
                        self.result = self.result + '806\t' + self.cur_str + '\n'
                    self.cur_str = ''
                    self.status = 0
                    return 0
            else:
                if 'e' not in self.cur_str or 'E' not in self.cur_str:
                    if self.cur_str[-1] == '.':
                        self.error_list = self.error_list + "line " + str(
                            self.line_index) + ", " + self.cur_str + "\tData Error!" + '\n'
                    self.result = self.result + '801\t' + self.cur_str + '\n'
                else:
                    self.result = self.result + '806\t' + self.cur_str + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
        if self.status == 8:  # 识别完整的错误数据并输出提示信息
            if bit not in [' ', ',', ';'] and self.cur_line == self.line_index:
                self.cur_str += bit
                return 1
            else:
                self.error_list = self.error_list + "line " + str(
                    self.line_index) + ", " + self.cur_str + "\tData Error!" + '\n'
                self.cur_str = ''
                self.status = 0
                return 0

    def shiliu_or_ba_or_er(self, bit):
        """
        判断十六进制
        """
        if self.status == 11:
            if self.cur_line == self.line_index:
                if '0' <= bit <= '9' or 'a' <= bit.lower() <= 'f' or 'A' <= bit.lower() <= 'F':  # 十六进制不能超过f/F
                    self.cur_str += bit
                    return 1
                elif bit not in [' ', ',', ';'] + list(self.yunsuanfu.keys()) + list(self.jiefu.keys()):  # 识别错误
                    self.cur_str += bit
                    self.status = 8
                    return 1
                else:  # 十六进制种别码为416
                    self.result = self.result + '416\t' + self.cur_str + '\n'
                    self.status = 0
                    self.cur_str = ''
                    return 0
            else:
                self.result = self.result + '416\t' + self.cur_str + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
        """
        判断八进制和二进制
        """
        if self.status == 12:  # 判断八进制
            if self.cur_line == self.line_index:
                if '0' <= bit <= '7':
                    self.cur_str += bit
                    return 1
                elif bit == '.':
                    self.cur_str += bit
                    self.status = 7  # 小数状态为7
                    return 1
                elif bit not in [' ', ',', ';'] + list(self.yunsuanfu.keys()) + list(self.jiefu.keys()):
                    self.cur_str += bit
                    self.status = 8  # 小数状态为8
                    return 1
                else:
                    count = 0
                    for i in self.cur_str:
                        if i == '0' or i == '1':
                            count += 1
                    if count == len(self.cur_str):
                        self.result = self.result + '402\t' + self.cur_str + '\n'
                        self.status = 0
                        self.cur_str = ''
                        return 0
                    else:
                        self.result = self.result + '408\t' + self.cur_str + '\n'
                        self.status = 0
                        self.cur_str = ''
                        return 0
            else:
                self.result = self.result + '408\t' + self.cur_str + '\n'
                self.status = 0
                self.cur_str = ''
                return 0

    def pdjiefu(self, bit):
        """
        识别界符
        """
        if self.status == 0 and bit in ['{', '}', ';', ',', '"', "'"]:
            if bit == '{':
                self.da += 1
                self.cur_line = self.line_index
                self.daw.append(self.cur_line)
                return 1
            if bit == '}':
                self.da -= 1
                if len(self.daw) > 0:
                    self.daw.pop()
                else:
                    self.error_list = self.error_list + "line " + str(
                        self.line_index) + ", " + self.cur_str + "\tThe previous text lacks' {" \
                                                                 "'corresponding to'} '" + '\n'
                return 1
            if bit == '"':
                self.status = 3
                self.cur_str += bit
                self.cur_line = self.line_index
                return 1
            if bit == "'":
                self.status = 5
                self.cur_str += bit
                self.cur_line = self.line_index
                return 1
            self.result = self.result + str(self.jiefu[bit]) + '\t' + bit + '\n'
            return 1
        if self.status == 3:  # 识别字符串
            if bit == '"':
                self.cur_str += bit
                self.status = 0
                self.result = self.result + '500\t' + self.cur_str + '\n'
                self.cur_str = ''
                return 1
            elif bit == ';':
                self.error_list = self.error_list + "line " + str(
                    self.cur_line) + ", " + self.cur_str + '\tafter " Missing!' + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
            elif self.cur_line != self.line_index:
                self.error_list = self.error_list + "line " + str(
                    self.cur_line) + ", " + self.cur_str + '\tafter " Missing!' + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
            else:
                self.cur_str += bit
                return 1
        if self.status == 5:  # 识别字符
            if bit == "'":
                self.cur_str += bit
                self.status = 0
                self.result = self.result + '600\t' + self.cur_str + '\n'
                self.cur_str = ''
                return 1
            elif bit == ";":
                self.error_list = self.error_list + "line " + str(
                    self.cur_line) + ", " + self.cur_str + "\tafter ' Missing!" + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
            elif self.cur_line != self.line_index:
                self.error_list = self.error_list + "line " + str(
                    self.cur_line) + ", " + self.cur_str + "\tafter ' Missing!" + '\n'
                self.status = 0
                self.cur_str = ''
                return 0
            else:
                self.cur_str += bit
                return 1
        else:
            return 0

    def pdyunsuanfu(self, bit):
        """
        识别运算符
        """
        if self.status == 0:
            self.cur_line = self.line_index
        if self.cur_line == self.line_index:  # 同一行内
            if bit in list(self.yunsuanfu.keys()):
                if self.cur_str + bit == '//':  # 识别到/时，需要考虑为注释符的情况
                    self.cur_str += bit
                    self.status = 100
                    return 1
                if self.cur_str + bit == '/*':  # 识别到/时，需要考虑为注释符的情况
                    self.cur_str += bit
                    self.status = 101
                    return 1
                if bit == '[':
                    self.zhong += 1
                    self.cur_line = self.line_index
                    self.zhongw.append(self.cur_line)
                    return 1
                if bit == ']':
                    self.zhong -= 1
                    self.cur_line = self.line_index
                    if len(self.zhongw) > 0:
                        self.zhongw.pop()
                    else:
                        self.error_list = self.error_list + "line " + str(
                            self.line_index) + ", " + self.cur_str + "\tThe previous text lacks' [" \
                                                                     "'corresponding to'] '" + '\n'
                    return 1
                if bit == '(':
                    self.xiao += 1
                    self.cur_line = self.line_index
                    self.xiaow.append(self.cur_line)
                    return 1
                if bit == ')':
                    self.xiao -= 1
                    if len(self.xiaow) > 0:
                        self.xiaow.pop()
                    else:
                        self.error_list = self.error_list + "line " + str(
                            self.line_index) + ", " + self.cur_str + "\tThe previous text lacks' (" \
                                                                     "'corresponding to') '" + '\n'
                    return 1
                elif self.cur_str + bit in list(self.yunsuanfu.keys()):  # 两三个字符
                    self.status = 4
                    self.cur_str += bit
                    return 1
                else:
                    self.result = self.result + str(self.yunsuanfu[self.cur_str]) + '\t' + self.cur_str + '\n'
                    self.cur_str = ''
                    self.status = 0
                    return 0
            elif self.status == 4:
                if self.cur_str in list(self.yunsuanfu.keys()):
                    self.result = self.result + str(self.yunsuanfu[self.cur_str]) + '\t' + self.cur_str + '\n'
                self.cur_str = ''
                self.status = 0
                return 0
        else:  # 不同一行
            if self.cur_str in list(self.yunsuanfu.keys()):
                self.result = self.result + str(self.yunsuanfu[self.cur_str]) + '\t' + self.cur_str + '\n'
            self.cur_str = ''
            self.status = 0
            return 0

    def zhushi(self, bit):
        """
        识别注释
        """
        if self.status == 100:
            if self.cur_line == self.line_index:
                self.cur_str += bit
                return 1
            else:
                self.cur_line = self.line_index
                self.cur_str = ''
                self.status = 0
                return 0
        if self.status == 101:
            if self.cur_str[-2:] != '*/':
                self.cur_str += bit
                return 1
            else:
                self.cur_str = ''
                self.status = 0
                return 0

    def zhuanyizifu(self, bit):
        """
        识别转义字符
        """
        if self.status == 0 and bit == '\\':
            self.cur_str += bit
            self.status = 9
            return 1
        if self.status == 9:
            if bit in ['n', 't', 'r']:
                self.cur_str += bit
                self.result = self.result + self.fenge[self.cur_str[-2:]] + self.cur_str + '\n'
                self.cur_str = ''
                self.status = 0
                return 1
            else:
                self.cur_str += bit
                self.error_list = self.error_list + "line " + str(
                    self.line_index) + ", " + self.cur_str + "\tERROR!" + '\n'
                self.cur_str = ''
                self.status = 0
                return 1

    def other_char(self, bit):
        """
        识别其他字符
        """
        if self.status == 0 and (bit in self.error_char):
            self.cur_str += bit
            self.status = 10
            return 1
        elif self.status == 10 and bit not in [',', ';', ' ']:
            self.cur_str += bit
            return 1
        elif self.status == 10:
            self.error_list = self.error_list + "line " + str(
                self.line_index) + ", " + self.cur_str + "\tIncorrect identifier!" + '\n'
            self.cur_str = ''
            self.status = 0
            return 0

    def main(self):
        for line in self.data:
            for bit in line:
                if (self.status == 0 or self.status == 1) and self.gjz_or_bsf(bit):
                    continue
                if (self.status == 0 or self.status == 2) and self.zhengshu(bit):
                    continue
                if (self.status == 0 or self.status == 3 or self.status == 5) and self.pdjiefu(bit):
                    continue
                if (self.status == 0 or self.status == 4) and self.pdyunsuanfu(bit):
                    continue
                if (self.status == 6 or self.status == 7 or self.status == 8) and self.xs_or_kxjsf(bit):
                    continue
                if (self.status == 0 or self.status == 9) and self.zhuanyizifu(bit):
                    continue
                if (self.status == 0 or self.status == 10) and self.other_char(bit):
                    continue
                if (self.status == 11 or self.status == 12) and self.shiliu_or_ba_or_er(bit):
                    continue
                if (self.status == 100 or self.status == 101) and self.zhushi(bit):
                    continue

                # 额外进行以下状态的判断，避免漏掉字符
                if (self.status == 0 or self.status == 1) and self.gjz_or_bsf(bit):
                    continue
                if (self.status == 0 or self.status == 2) and self.zhengshu(bit):
                    continue
                if (self.status == 0 or self.status == 3 or self.status == 5) and self.pdjiefu(bit):
                    continue
                if (self.status == 0 or self.status == 4) and self.pdyunsuanfu(bit):
                    continue
                if (self.status == 6 or self.status == 7 or self.status == 8) and self.xs_or_kxjsf(bit):
                    continue
                if (self.status == 0 or self.status == 9) and self.zhuanyizifu(bit):
                    continue
                if (self.status == 0 or self.status == 10) and self.other_char(bit):
                    continue
                if (self.status == 11 or self.status == 12) and self.shiliu_or_ba_or_er(bit):
                    continue
                if (self.status == 100 or self.status == 101) and self.zhushi(bit):
                    continue
            self.line_index += 1
        if self.status == 101:
            self.error_list = self.error_list + "line " + str(
                self.cur_line) + ", " + self.cur_str + "\t'*/' Missing!" + '\n'

        # 括号配对
        if self.da < 0:
            self.error_list = self.error_list + "line " + str(
                self.daw[-1]) + ", " + "}" + "\t'{' Missing!" + '\n'
        if self.da > 0:
            self.error_list = self.error_list + "line " + str(
                self.daw[-1]) + ", " + "{" + "\t'}' Missing!" + '\n'
        if self.zhong < 0:
            self.error_list = self.error_list + "line " + str(
                self.zhongw[-1]) + ", " + "]" + "\t'[' Missing!" + '\n'
        if self.zhong > 0:
            self.error_list = self.error_list + "line " + str(
                self.zhongw[-1]) + ", " + "[" + "\t']' Missing!" + '\n'
        if self.xiao < 0:
            self.error_list = self.error_list + "line " + str(
                self.xiaow[-1]) + ", " + ")" + "\t'(' Missing!" + '\n'
        if self.xiao > 0:
            self.error_list = self.error_list + "line " + str(
                self.xiaow[-1]) + ", " + "(" + "\t')' Missing!" + '\n'

        # 将词法分析的结果存入txt文本中
        Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/cffxjg.txt', mode='w', encoding='UTF-8')
        for i in range(len(self.result)):
            Note1.write(str(self.result[i]))
        Note1.close()
        if self.error_list:
            Note2 = open('C:/Users/YL139/Desktop/byyl/test/byxt/error.txt', mode='w', encoding='UTF-8')
            for i in range(len(self.error_list)):
                Note2.write(str(self.error_list[i]))
            Note2.close()
        else:
            Note2 = open('C:/Users/YL139/Desktop/byyl/test/byxt/error.txt', mode='w', encoding='UTF-8')
            Note2.write('This code has no errors!')
            Note2.close()

        return self.result, self.error_list


# with open('C:/Users/YL139/Desktop/byyl/test/byxt/cffx.txt', 'r', encoding='UTF-8') as f:
#     data = f.read()
# wa = cifafenxi(data)
# result = wa.main()
# print(result[0])
# print(result[1])
