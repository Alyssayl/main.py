CodeDic = {
    "char": 101,
    "int": 102,
    "float": 103,
    "break": 104,
    "const": 105,
    "return": 106,
    "void": 107,
    "continue": 108,
    "do": 109,
    "while": 110,
    "if": 111,
    "else": 112,
    "for": 113,
    "define": 114,
    "include": 115,
    "{": 301,
    "}": 302,
    ";": 303,
    ",": 304,
    "Integer": 400,
    "Character": 500,
    "String": 600,
    "Identify": 700,
    "RealNumber": 800,
    "hex": 900,
    "oal": 1000,
    "(": 201,
    ")": 202,
    "[": 203,
    "]": 204,
    "!": 205,
    "*": 206,
    "/": 207,
    "%": 208,
    "+": 209,
    "-": 210,
    "<": 211,
    "<=": 212,
    ">": 213,
    ">=": 214,
    "==": 215,
    "!=": 216,
    "&&": 217,
    "||": 218,
    "=": 219,
    ".": 220,
    ":": 221,
    "?": 222,
    "#": 223,
    "&": 224,
    "++": 225,
    "--": 226,
    "+=": 227,
    "-=": 228
}

# 哈哈哈哈哈哈哈哈哈哈哈哈或或或
class token:
    def __init__(self, ROW, number, String):
        self.ROW = ROW  # 行号
        self.String = String  # 内容
        self.number = number  # 种别码


class Auto:

    def __init__(self, String):
        self.INDEX = 0  # 当前识别字符串字符的下标
        self.ROW = 1  # 当前识别字符串字符的行
        self.tokenList = []  # 保存token串对象
        self.errorList = []  # 保存出错误信息
        self.String = String

    def GetResult(self):
        self.recognizeWord()
        self.tokenList.append(token(self.ROW, 223, "#"))
        return self.tokenList, self.errorList

    def recognizeWord(self):
        othernum = ['(', ')', '[', ']', '*', '%',
                    '.', '{', '}', ',', ';', '?', ':', '#']
        comWords = ['>', '<', '=', '!', '&', '|', '+', '-']
        while len(self.String) > self.INDEX:
            if self.String[self.INDEX] == ' ' or self.String[self.INDEX] == '\t':  # 空格或Tab跳过
                self.INDEX += 1
                continue
            elif self.String[self.INDEX] == '\n':  # 回车换行
                self.ROW += 1
            elif self.String[self.INDEX].isalpha() or self.String[self.INDEX] == '_':  # 字母下划线进入判断标识符
                self.recognizeIndntify()
            elif self.String[self.INDEX].isdigit():  # 数字进入数字判断
                self.recognizeInteger()
            elif self.String[self.INDEX] in othernum:  # 识别界符
                self.recognizeOther()
            elif self.String[self.INDEX] == '/':  # 识别除号或者注释
                self.recognizeTran()
            elif self.String[self.INDEX] in comWords:  # 识别运算符
                self.recognizeCom()
            elif self.String[self.INDEX] == '\'':  # 识别字符常量
                self.recognizeChar()
            elif self.String[self.INDEX] == '\"':  # 识别字符串常量
                self.recognizeselfString()
            else:
                self.errorList.append(str(self.ROW) + "行出错，非法字符: " + self.String[self.INDEX])
                print(str(self.ROW) + "行出错，非法字符: " + self.String[self.INDEX])
            self.INDEX += 1

    # 识别字符常量
    def recognizeChar(self):
        state = 0
        start = self.INDEX
        self.INDEX += 1
        while self.INDEX < len(self.String):
            if self.String[self.INDEX] == '\'':
                state = 1
                break
            self.INDEX += 1
        if self.INDEX < len(self.String) and state == 1:
            if self.INDEX - start <= 2:
                num = CodeDic.get("Character")
                self.tokenList.append(token(self.ROW, num, self.String[start:self.INDEX + 1]))
            else:
                self.errorList.append(str(self.ROW) + "行出错，非字符常量: " + self.String[start:self.INDEX + 1])
                print(str(self.ROW) + "行出错，非字符常量: " + self.String[start:self.INDEX + 1])
        else:
            self.errorList.append(str(self.ROW) + "行出错，字符常量可能缺后单引号: " + self.String[start:self.INDEX])
            print(str(self.ROW) + "行出错，字符常量可能缺后单引号: " + self.String[start:self.INDEX])

    # 识别字符串常量
    def recognizeselfString(self):
        state = 0
        start = self.INDEX
        self.ROW = self.ROW
        self.INDEX += 1
        while self.INDEX < len(self.String):
            if self.String[self.INDEX] == '\"':
                state = 1
                break
            if self.String[self.INDEX] == '\n':
                self.ROW += 1
            self.INDEX += 1
        if self.INDEX < len(self.String) and state == 1:
            num = CodeDic.get("String")
            self.tokenList.append(token(self.ROW, num, self.String[start:self.INDEX + 1]))
        else:
            self.errorList.append(str(self.ROW) + "行出错，字符串常量可能缺后双引号: " + self.String[start:self.INDEX])
            print(str(self.ROW) + "行出错，字符常量可能缺后单引号: " + self.String[start:self.INDEX])

    # 识别['(', ')', '[', ']', '*', '%', '.', '{', '}', ',', ';', ':', '#']
    def recognizeOther(self):
        num = CodeDic.get(self.String[self.INDEX])
        self.tokenList.append(token(self.ROW, num, self.String[self.INDEX]))

    # 识别['>', '+', '-', '<', '=', '&', '+=', '-=', '==', '>=', '<=', '&&', '||', '!=']
    def recognizeCom(self):
        state = 0
        if self.INDEX + 1 < len(self.String):
            if self.String[self.INDEX] == '>':
                if self.String[self.INDEX + 1] == '=':
                    state = 1  # >=
            elif self.String[self.INDEX] == '<':
                if self.String[self.INDEX + 1] == '=':
                    state = 1  # <=
            elif self.String[self.INDEX] == '=':
                if self.String[self.INDEX + 1] == '=':
                    state = 1  # ==
            elif self.String[self.INDEX] == '!':
                if self.String[self.INDEX + 1] == '=':
                    state = 1  # !=
            elif self.String[self.INDEX] == '+':
                if self.String[self.INDEX + 1] == '=' or self.String[self.INDEX + 1] == '+':
                    state = 1  # +=
            elif self.String[self.INDEX] == '-':
                if self.String[self.INDEX + 1] == '=' or self.String[self.INDEX + 1] == '-':
                    state = 1  # -=
            elif self.String[self.INDEX] == '&':  # &
                if self.String[self.INDEX + 1] == '&':
                    state = 1  # &&
                else:  # &不全
                    self.errorList.append(str(self.ROW) + "行出错: " + self.String[self.INDEX])
                    print(str(self.ROW) + "行出错: " + self.String[self.INDEX])
                    return
            elif self.String[self.INDEX] == '|':
                if self.String[self.INDEX + 1] == '|':
                    state = 1  # ||
                else:  # |不全
                    self.errorList.append(str(self.ROW) + "行出错: " + self.String[self.INDEX])
                    print(str(self.ROW) + "行出错: " + self.String[self.INDEX])
                    return
        if state == 1:
            str1 = self.String[self.INDEX:self.INDEX + 2]
            num = CodeDic.get(str1)
            self.tokenList.append(token(self.ROW, num, str1))
            self.INDEX += 1
        else:
            num = CodeDic.get(self.String[self.INDEX])
            self.tokenList.append(token(self.ROW, num, self.String[self.INDEX]))

    # 识别注释
    def recognizeTran(self):
        if self.String[self.INDEX + 1] == '/':  # 行注释
            while self.INDEX != len(self.String) and self.String[self.INDEX] != '\n':
                self.INDEX += 1
            if self.INDEX != len(self.String):
                if self.String[self.INDEX] == '\n':
                    self.ROW += 1
        elif self.String[self.INDEX + 1] == '*':  # 段注释
            self.INDEX += 1
            state = False
            while self.INDEX != len(self.String):
                if self.String[self.INDEX] == '*':
                    if self.INDEX + 1 < len(self.String):
                        if self.String[self.INDEX + 1] == '/':
                            state = True  # 代表注释正确
                            self.INDEX += 1
                            break
                if self.String[self.INDEX] == '\n':
                    self.ROW += 1
                self.INDEX += 1
            if not state:
                self.errorList.append(str(self.ROW) + "行出错: " + "注释出错")
                print(str(self.ROW) + "行出错: " + "注释出错")
        else:  # 除号
            num = CodeDic.get(self.String[self.INDEX])
            self.tokenList.append(token(self.ROW, num, self.String[self.INDEX]))

    # 识别标识符
    def recognizeIndntify(self):
        state = 0
        start = self.INDEX
        # 标识符后可以跟以下字符
        othernum = [' ', '\t', ';', '(', ')', '%', '{', '>', '<', '=', '.', '!',
                    ',', '&', '|', '+', '-', '*', '/', '?', ':', '[', ']', '\n']
        while len(self.String) > self.INDEX:
            if state == 0:
                if self.String[self.INDEX].isalpha() or self.String[self.INDEX] == '_':  # 接收字母或下划线，进入状态1
                    state = 1
                else:  # 否则退出
                    state = 2
                    break
            elif state == 1:  # 判断是否为数字字母下划线
                if self.String[self.INDEX].isalpha() or self.String[self.INDEX] == '_' or\
                        self.String[self.INDEX].isdigit():
                    state = 1
                elif self.String[self.INDEX] in othernum:
                    state = 3
                    break
                else:
                    self.error(start)
                    state = 2
                    break
            self.INDEX += 1
        self.INDEX -= 1
        if state != 2:
            str1 = self.String[start:self.INDEX + 1]
            num = CodeDic.get(str1)
            if not num:
                num = CodeDic.get('Identify')
            self.tokenList.append(token(self.ROW, num, str1))

    # 识别数值类常数
    def recognizeInteger(self):
        state = 0
        start = self.INDEX
        # num = [4, 7, 13, 14, 15, 16]  # 终结状态
        hexnum = ['0', '1', '2', '3', '4', '5', '6', '7', '8',
                  '9', 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F']  # 十六进制字符
        octnum = ['0', '1', '2', '3', '4', '5', '6', '7']  # 八进制
        othernum = [' ', ',', ';', '}', ')', '+', '-', '*', '/',
                    '=', '!', '<', '>', '%', ']', '&', '|', '?', ':', '\n']
        while len(self.String) > self.INDEX:
            if state == 0:  # 状态为0，等待输入
                if self.String[self.INDEX] == '0':  # 输入为0，进入状态2，判断八进制或十六进制，或0或0.小数
                    state = 2
                elif self.String[self.INDEX].isdigit():  # 输入为1~9，进入状态1，继续判断是否为数字
                    state = 1
                else:  # 输入不是数字，进入状态16，报错
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 1:  # 状态1接收数字0~9
                if self.String[self.INDEX].isdigit():  # 判断是否为0~9，若是则继续状态1
                    state = 1
                elif self.String[self.INDEX] == '.':  # 接收到小数点，进入状态8,判断是否为十进制小数
                    state = 8
                elif self.String[self.INDEX] == 'e' or self.String[self.INDEX] == 'E':  # 科学计数法
                    state = 10
                elif self.String[self.INDEX] in othernum:  # 接收到空符，运算符，界符，为整数
                    state = 15
                    break
                else:  # 否则进入状态16，报错
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 2:  # 状态2接收小数点,数字0~7,x/X
                if self.String[self.INDEX] in octnum:  # 判断是否为0~7，是则进入状态3,判断是否为八进制数
                    state = 3
                elif self.String[self.INDEX] == 'x' or self.String[self.INDEX] == 'X':  # 判断是否为x，是则进入状态5，判断是否为十六进制数
                    state = 5
                elif self.String[self.INDEX] == '.':  # 接收到小数点，进入状态8，判断是否为十进制小数
                    state = 8
                else:  # 若都不是，进入状态15,为整数0
                    state = 15
                    break
            elif state == 3:  # 状态3接收0~7，判断是否为1八进制数
                if self.String[self.INDEX] in octnum:  # 判断是否为0~7，是则保持状态3
                    state = 3
                else:  # 若不是，八进制数结束，进入状态4
                    state = 4
                    break
            elif state == 5:  # 接收数字0~9，字母a~f,A~F
                if self.String[self.INDEX] in hexnum:
                    state = 6
                else:  # 接收参数错，只有0x，报错
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 6:  # 接收0~9，字母a~f,A~F
                if self.String[self.INDEX] in hexnum:  # 判断是否为十六进制
                    state = 6
                else:  # 输入其他，则十六进制数结束
                    state = 7
                    break
            elif state == 8:  # 状态8已接收小数点
                if self.String[self.INDEX].isdigit():  # 若为数字，进入状态9
                    state = 9
                else:  # 接收数不为数字，进入16，报错
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 9:  # 状态9接收数字判断是否为小数
                if self.String[self.INDEX].isdigit():  # 若为数字，保持状态9
                    state = 9
                elif self.String[self.INDEX] == 'e' or self.String[self.INDEX] == 'E':  # 科学计数法
                    state = 10
                elif self.String[self.INDEX] in othernum:  # 接收到空符，运算符，界符，为小数
                    state = 14
                    break
                else:  # 接收数不为数字或e/E或空符，运算符，界符，进入16，报错
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 10:
                if self.String[self.INDEX].isdigit():  # 若为数字，进入状态12
                    state = 12
                elif self.String[self.INDEX] == '+' or self.String[self.INDEX] == '-':  # 接收到正负号，进入状态11
                    state = 11
                else:
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 11:
                if self.String[self.INDEX].isdigit():  # 若为数字，进入状态12
                    state = 12
                else:
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            elif state == 12:
                if self.String[self.INDEX].isdigit():  # 若为数字，保持状态12
                    state = 12
                elif self.String[self.INDEX] in othernum:  # 指数
                    state = 13
                    break
                else:
                    self.error(start)
                    # self.INDEX -= 1
                    state = 16
                    break
            self.INDEX += 1
        self.INDEX -= 1
        if state != 16:
            if state == 4 or state == 3:
                num = CodeDic.get("oal")
            elif state == 7 or state == 6:
                num = CodeDic.get("hex")
            else:
                num = CodeDic.get('RealNumber')
            str1 = self.String[start:self.INDEX + 1]
            self.tokenList.append(token(self.ROW, num, str1))

    def error(self, start):
        self.errorList.append(str(self.ROW) + "行出错: " + self.String[start:self.INDEX + 1])


# if __name__ == '__main__':
#     result = RecognizeWord("int main-")  # 传待分析字符串
#     tokenList, errorList = result.GetResult()  # 返回token串与错误信息
#     for i in tokenList:
#         print('( ' + str(i.ROW) + ', ' + str(i.number) + ', ' + i.String + ' )')
#     print(errorList)
