from First_Follow import Get_First_Follow
from Auto import Auto
from graphviz import Digraph

g = Digraph('G', filename='C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv')
sentences = []
errorLists = None
nodeNum = 0
First = None
Follow = None
first = None
FLAG = True
errors = None
MISS = [12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 30, 35, 41, 42, 43, 45]


def init():
    global First
    global Follow
    global first
    global FLAG
    global nodeNum
    global g
    global errorLists
    global errors
    if FLAG:
        with open("C:/Users/YL139/Desktop/byyl/test/byxt/may_error1.txt", "r", encoding="utf-8") as file1:
            errorLists = file1.readlines()
        with open("C:/Users/YL139/Desktop/byyl/test/byxt/wenfa.txt", "r", encoding="utf-8") as file2:
            files = file2.readlines()
        for i in files:
            s2 = i.replace("\n", "")
            s3 = s2.split("->")
            s4 = s3[1].split("|")
            for j in s4:
                temp = [s3[0]]
                s5 = j.strip().split(" ")
                for k in s5:
                    temp.append(k)
                sentences.append(temp)
        r = Get_First_Follow(sentences)
        First, first, Follow = r.GetResult()
        FLAG = False
        with open("C:/Users/YL139/Desktop/byyl/test/byxt/may_error.txt", "r", encoding="utf-8") as file3:
            errors = file3.readlines()
    nodeNum = 0
    g.clear()


#  生成边
def createEdge(root):
    if not root:
        return
    child = root.first_son
    while child:
        g.edge(str(root.num), str(child.num))
        child = child.brother


# 跳转到下个;或类型处
def jump_1(tokenList, index):
    while index < len(tokenList):
        if tokenList[index].number == 303:
            return index + 1
        elif tokenList[index].number in [101, 102, 103, 107] or tokenList[index].String == "main":
            return index
        index += 1
    return index


# 结点
class node:
    def __init__(self, value):
        global nodeNum
        self.num = nodeNum  # 唯一编号
        self.value = value  # 值
        self.brother = None  # 兄弟结点
        self.first_son = None  # 第一个孩子结点
        g.node(str(nodeNum), label=value)  # 添加结点
        nodeNum += 1


#  语法分析
class GramAnalyzer:
    def __init__(self, token):
        init()
        self.tokenList = token
        self.INDEX = 0
        self.FIRST, self.FOLLOW = First, Follow
        self.errorList = []
        self.isTure = True

    # 获取下一个值
    def getNextToken(self):
        if self.INDEX < len(self.tokenList):
            return self.tokenList[self.INDEX]
        return None

    def match(self):
        self.INDEX += 1

    def isInFirst(self, ID):
        token = self.getNextToken()
        if token:
            if token.String in self.FIRST[ID]:
                return True
            elif token.number == 700:  # Identify
                if "iden" in self.FIRST[ID]:
                    return True
            elif token.number in [400, 800, 900, 1000]:  # Integer，RealNumber，hex，oal
                if "num_con" in self.FIRST[ID]:
                    return True
            elif token.number in [500, 600]:  # Character，string
                if "char_con" in self.FIRST[ID]:
                    return True
        return

    def isInFollow(self, ID):
        if "ε" in self.FIRST[ID]:
            token = self.getNextToken()
            if token:
                if token.String in self.FOLLOW[ID]:
                    return True
                elif token.number == 700:
                    if "iden" in self.FOLLOW[ID]:
                        return True
                elif token.number in [400, 800]:
                    if "num_con" in self.FOLLOW[ID]:
                        return True
                elif token.number in [500, 600]:
                    if "char_con" in self.FOLLOW[ID]:
                        return True
        return

    # 错误处理
    def SyntaxError(self, num):
        token = self.tokenList[self.INDEX - 1]
        error = "行号：" + str(token.ROW) + "  内容：" + token.String + " 说明: " + errors[num - 1]
        self.errorList.append(error)
        self.isTure = False
        if num in MISS:
            self.INDEX = jump_1(self.tokenList, self.INDEX)

    # 生成语法树
    def Begin(self):
        root = node("PROGRAM")  # 根结点
        token = self.getNextToken()
        if token is None:  # 只有根结点
            createEdge(root)
            g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
            return
        rightBro = None
        while token.String != "main":
            son = None
            if token.String == "const":  # 处理常量声明
                son = self.CON_DEC()
            elif token.number in [102, 101, 103, 107]:  # int char float void
                self.match()
                token = self.getNextToken()
                if token is None:
                    self.SyntaxError(45)
                    createEdge(root)
                    g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
                    return
                if token.number != 700:  # 标识符
                    self.SyntaxError(10)
                else:
                    self.match()
                token = self.getNextToken()
                if token is None:
                    self.SyntaxError(45)
                    createEdge(root)
                    g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
                    return
                self.INDEX = self.INDEX - 2
                if token.number == 201:  # (
                    son = self.FUN_DEC()
                elif token.number in [219, 303, 304]:  # = ,
                    son = self.VAR_DEC()
                else:
                    self.SyntaxError(44)
            else:
                self.SyntaxError(16)
            if rightBro:
                rightBro.brother = son
            else:
                root.first_son = son
            rightBro = son
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(45)
                createEdge(root)
                g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
                return
        self.match()
        main_ = node("main")
        if rightBro:
            rightBro.brother = main_
        else:
            root.first_son = main_
        rightBro = main_
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
            return
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden = node(" ")
        else:
            self.match()
            iden = node("(")
        rightBro.brother = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            createEdge(main_)
            createEdge(root)
            g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
            return
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node(")")
        iden.brother = iden1
        son = self.COM_SEN()
        main_.first_son = son
        createEdge(main_)
        token = self.getNextToken()
        if token is None:
            createEdge(root)
            g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
            return
        while True:  # [102, 101, 103, 107]
            if token is None or token.String == "#":
                createEdge(root)
                g.render('C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv', view=False)
                return
            son = self.FUN_DEF()
            if son:
                rightBro.brother = son
                rightBro = son
            token = self.getNextToken()

    # <函数声明> -> <函数类型><标识符>(<函数声明形参列表>);
    # FUN_DEC->FUN_TYPE iden ( FUN_DEC_PARA_LIST ) ;
    def FUN_DEC(self):
        root = node("FUN_DEC")
        fun_type = self.FUN_TYPE()
        root.first_son = fun_type
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(9)
            createEdge(root)
            return root
        if token.number != 700:  # 不是标识符
            self.SyntaxError(9)
            iden = node(" ")
        else:
            self.match()
            iden = node(token.String)
        fun_type.brother = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            return root
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node("(")
        iden.brother = iden1
        fdpl = self.FUN_DEC_PARA_LIST()
        iden1.brother = fdpl
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            createEdge(root)
            return root
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden2 = node(" ")
        else:
            self.match()
            iden2 = node(")")
        fdpl.brother = iden2
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:  # ;
            self.SyntaxError(1)
            iden3 = node(";")
        else:
            self.match()
            iden3 = node(";")
        iden2.brother = iden3
        createEdge(root)
        return root

    # <变量声明> -> <变量类型><变量声明表>
    # VAR_DEC->VAR_TYPE VAR_DEC_TABLE
    def VAR_DEC(self):
        root = node("VAR_DEC")
        var_type = self.VAR_TYPE()
        root.first_son = var_type
        var_dec_table = self.VAR_DEC_TABLE()
        var_type.brother = var_dec_table
        createEdge(root)
        return root

    # <函数定义> -> <函数类型><标识符>(<函数定义形参列表>)<复合语句>
    # FUN_DEF->FUN_TYPE iden ( FUN_DEF_LIST ) COM_SEN
    def FUN_DEF(self):
        root = node("FUN_DEF")
        fun_type = self.FUN_TYPE()
        root.first_son = fun_type
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(9)
            createEdge(root)
            return root
        if token.number != 700:
            self.SyntaxError(9)
            iden = node(" ")
        else:
            self.match()
            iden = node(token.String)
        fun_type.brother = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            return root
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node("(")
        iden.brother = iden1
        fdl = self.FUN_DEF_LIST()
        iden1.brother = fdl
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            createEdge(root)
            return root
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden2 = node(" ")
        else:
            self.match()
            iden2 = node(")")
        fdl.brother = iden2
        com_sen = self.COM_SEN()
        iden2.brother = com_sen
        createEdge(root)
        return root

    # <函数类型> -> int | char | float | void
    # FUN_TYPE->int|char|float|void
    def FUN_TYPE(self):
        root = node("FUN_TYPE")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(12)
            return root
        if token not in ['int', 'void', 'char', 'float']:
            self.SyntaxError(12)
            return root
        self.match()
        iden = node(token.String)
        root.first_son = iden
        createEdge(root)
        return root

    # <函数定义形参列表> -> <函数定义形参> | ε
    # FUN_DEF_LIST->FUN_DEF_PARA|ε
    def FUN_DEF_LIST(self):
        root = node("FUN_DEF_LIST")
        if self.isInFirst("FUN_DEF_PARA"):
            fdp = self.FUN_DEF_PARA()
            root.first_son = fdp
            createEdge(root)
            return root
        elif self.isInFollow("FUN_DEF_LIST"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(41)
        return root

    # <函数定义形参> -> <变量类型><变量类型1>
    # FUN_DEF_PARA->VAR_TYPE FUN_DEF_PARA_1
    def FUN_DEF_PARA(self):
        root = node("FUN_DEF_PARA")
        vt = self.VAR_TYPE()
        root.first_son = vt
        fdp = self.FUN_DEF_PARA_1()
        vt.brother = fdp
        createEdge(root)
        return root

    # <函数定义形参1>-><标识符><标识符1>
    # FUN_DEF_PARA_1->iden IDEN
    def FUN_DEF_PARA_1(self):
        root = node("FUN_DEF_PARA_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(10)
            return root
        if token.number != 700:
            self.SyntaxError(10)
            iden = node(" ")
        else:
            self.match()
            iden = node(token.String)
        root.first_son = iden
        iden1 = self.IDEN()
        iden.brother = iden1
        createEdge(root)
        return root

    # <标识符1>->ε |,<函数定义形参>
    # IDEN->ε|, FUN_DEF_PARA
    def IDEN(self):
        root = node("IDEN")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(4)
            return root
        if token.number == 304:
            self.match()
            iden = node(",")
            root.first_son = iden
            son = self.FUN_DEF_PARA()
            iden.brother = son
            createEdge(root)
            return root
        elif self.isInFollow("IDEN"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        self.SyntaxError(4)
        return root

    # <语句> -> <声明语句> | <执行语句>
    # SENTENCE->DEC_STA|EXE_STA
    def SENTENCE(self):
        root = node("SENTENCE")
        if self.isInFirst("EXE_STA"):
            son = self.EXE_STA()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFirst("DEC_STA"):
            son = self.DEC_STA()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFollow("SENTENCE"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        return root

    # <声明语句> -> <常量声明> | <变量声明> | ε
    # DEC_STA->CON_DEC|VAR_DEC|ε
    def DEC_STA(self):
        root = node("DEC_STA")
        if self.isInFirst("CON_DEC"):
            son = self.CON_DEC()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFirst("VAR_DEC"):
            son = self.VAR_DEC()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFollow("DEC_STA"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(16)
        return root

    # CON_DEC->const CON_TYPE CON_DEC_TABLE
    # <常量声明> -> const<常量类型><常量声明表>
    # CON_DEC->const CON_TYPE CON_DEC_TABLE
    def CON_DEC(self):
        root = node("CON_DEC")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(8)
            return root
        if token.number != 105:  # const
            self.SyntaxError(8)
            iden = node(" ")
        else:
            self.match()
            iden = node("const")
        root.first_son = iden
        son = self.CON_TYPE()
        iden.brother = son
        son1 = self.CON_DEC_TABLE()
        son.brother = son1
        createEdge(root)
        return root

    # <常量类型> -> int | char | float
    # CON_TYPE->int|char|float
    def CON_TYPE(self):
        root = node("CON_TYPE")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(18)
            return root
        if token.number not in [101, 102, 103]:
            self.SyntaxError(18)
            return root
        iden = node(token.String)
        root.first_son = iden
        self.match()
        createEdge(root)
        return root

    # <常量声明表> -> <标识符>=<常量> <常量声明表1>
    # CON_DEC_TABLE->iden = CONSTANT CON_DEC_TABLE_1
    def CON_DEC_TABLE(self):
        root = node("CON_DEC_TABLE")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(19)
            return root
        if token.number != 700:
            self.SyntaxError(19)
            iden = node(" ")
        else:
            iden = node("iden")
            self.match()
        root.first_son = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(5)
            createEdge(root)
            return root
        if token.number != 219:  # =
            self.SyntaxError(5)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node("=")
        iden.brother = iden1
        son = self.CONSTANT()
        iden1.brother = son
        son1 = self.CON_DEC_TABLE_1()
        son.brother = son1
        createEdge(root)
        return root

    # <常量>-><数值型常量>|<字符型常量>
    # CONSTANT->num_con|char_con
    def CONSTANT(self):
        root = node("CONSTANT")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(20)
            return root
        if token.number not in [400, 500, 600, 800, 900, 1000]:  # 数值型常量或字符型常量
            self.SyntaxError(20)
            return root
        iden = node(token.String)
        root.first_son = iden
        self.match()
        createEdge(root)
        return root

    # <常量声明表1>->;|,<常量声明表>
    # CON_DEC_TABLE_1->;|, CON_DEC_TABLE
    def CON_DEC_TABLE_1(self):
        root = node("CON_DEC_TABLE_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(21)
            return root
        if token.number == 303:  # ;
            self.match()
            iden = node(";")
            root.first_son = iden
            createEdge(root)
            return root
        elif token.number == 304:  # ,
            self.match()
            iden = node(";")
            root.first_son = iden
            son = self.CON_DEC_TABLE()
            iden.brother = son
            createEdge(root)
            return root
        else:
            self.SyntaxError(21)
        return root

    # <变量声明表> -> <单变量声明><单变量声明1>
    # VAR_DEC_TABLE->iden VAR_1 SIN_VAR_DEC_1
    def VAR_DEC_TABLE(self):
        root = node("VAR_DEC_TABLE")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(17)
            return root
        if token.number == 700:
            self.match()
            iden = node(token.String)
            root.first_son = iden
            son = self.VAR_1()
            iden.brother = son
            son1 = self.SIN_VAR_DEC_1()
            son.brother = son1
            createEdge(root)
            return root
        else:
            self.SyntaxError(17)
        return root

    # <单变量声明1>->; | ,<变量声明表>
    # SIN_VAR_DEC_1->;|, VAR_DEC_TABLE
    def SIN_VAR_DEC_1(self):
        root = node("SIN_VAR_DEC_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(21)
            return root
        if token.number == 303:  # ;
            iden = node(";")
            root.first_son = iden
            createEdge(root)
            self.match()
            return root
        elif token.number == 304:  # ,
            self.match()
            iden = node(",")
            root.first_son = iden
            son = self.VAR_DEC_TABLE()
            iden.brother = son
            createEdge(root)
            return root
        else:
            self.SyntaxError(21)
        return root

    # <变量1>->ε | =<表达式>
    # VAR_1->ε|= ARI_EXPRESSION
    def VAR_1(self):
        root = node("VAR_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(5)
            return root
        if token.number == 219:  # =
            self.match()
            iden = node("=")
            root.first_son = iden
            son = self.ARI_EXPRESSION()
            iden.brother = son
            createEdge(root)
            return root
        elif self.isInFollow("VAR_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(5)
        return root

    # <变量类型> -> int | char |float
    # VAR_TYPE->int|char|float
    def VAR_TYPE(self):
        root = node("VAR_TYPE")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(22)
            return root
        if token.number not in [101, 102, 103]:
            self.SyntaxError(22)
            return root
        iden = node(token.String)
        root.first_son = iden
        createEdge(root)
        self.match()
        return root

    # <函数声明形参列表> -> <函数声明形参> | ε
    # FUN_DEC_PARA_LIST->FUN_DEC_PARA|ε
    def FUN_DEC_PARA_LIST(self):
        root = node("FUN_DEC_PARA_LIST")
        if self.isInFirst("FUN_DEC_PARA"):
            son = self.FUN_DEC_PARA()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFollow("FUN_DEC_PARA_LIST"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(42)
        return root

    # <函数声明形参> -> <变量类型> <变量类型1>
    # FUN_DEC_PARA->VAR_TYPE VAR_TYPE_1
    def FUN_DEC_PARA(self):
        root = node("FUN_DEC_PARA")
        son = self.VAR_TYPE()
        root.first_son = son
        son1 = self.VAR_TYPE_1()
        son.brother = son1
        createEdge(root)
        return root

    # <变量类型1>->ε | ,<函数声明形参>
    # VAR_TYPE_1->ε|, FUN_DEC_PARA
    def VAR_TYPE_1(self):
        root = node("VAR_TYPE_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(4)
            return root
        if token.number == 304:  # ,
            self.match()
            iden = node(",")
            root.first_son = iden
            son = self.FUN_DEC_PARA()
            iden.brother = son
            createEdge(root)
            return root
        elif self.isInFollow("VAR_TYPE_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(4)
        return root

    # <执行语句> -> <数据处理语句> | <控制语句> | <复合语句>
    # EXE_STA->DATA_PRO_STA|CON_STA|COM_SEN
    def EXE_STA(self):
        root = node("EXE_STA")
        if self.isInFirst("COM_SEN"):
            son = self.COM_SEN()
        elif self.isInFirst("CON_STA"):
            son = self.CON_STA()
        elif self.isInFirst("DATA_PRO_STA"):
            son = self.DATA_PRO_STA()
        else:
            return root
        root.first_son = son
        createEdge(root)
        return root

    # <数据处理语句> -> <变量><数据处理语句1>
    # DATA_PRO_STA->iden DATA_PRO_STA_1
    def DATA_PRO_STA(self):
        root = node("DATA_PRO_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(10)
            return root
        if token.number == 700:  # iden
            self.match()
            iden = node(token.String)
            root.first_son = iden
            son = self.DATA_PRO_STA_1()
            iden.brother = son
            createEdge(root)
            return root
        else:
            self.SyntaxError(10)
        return root

    # <数据处理语句1>->-<表达式>;|(<实参列表>);
    # DATA_PRO_STA_1->= ARI_EXPRESSION ;|( ARG_LIST ) ;
    def DATA_PRO_STA_1(self):
        root = node("DATA_PRO_STA_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(23)
            return root
        if token.number == 219:  # =
            self.match()
            iden1 = node("=")
            root.first_son = iden1
            iden = self.ARI_EXPRESSION()
            iden1.brother = iden
        elif token.number == 201:  # (
            self.match()
            iden1 = node("(")
            root.first_son = iden1
            son = self.ARG_LIST()
            iden1.brother = son
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(6)
                createEdge(root)
                return root
            if token.number != 202:  # )
                self.SyntaxError(6)
                iden = node(" ")
            else:
                iden = node(")")
                self.match()
            son.brother = iden
        else:
            self.SyntaxError(23)
            return root
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:  # ;
            self.SyntaxError(1)
            iden2 = node(" ")
        else:
            iden2 = node(";")
            self.match()
        iden.brother = iden2
        createEdge(root)
        return root

    # <控制语句> -> <if语句> | <for语句> |  <while语句> | <do while语句> | <return语句> |<break语句> |<continue语句>
    # CON_STA->IF_STA|FOR_STA|WHILE_STA|DO_WHILE_STA|RETURN_STA|BREAK_STA|CONTINUE_STA
    def CON_STA(self):
        root = node("CON_STA")
        if self.isInFirst("IF_STA"):
            son = self.IF_STA()
        elif self.isInFirst("FOR_STA"):
            son = self.FOR_STA()
        elif self.isInFirst("WHILE_STA"):
            son = self.WHILE_STA()
        elif self.isInFirst("DO_WHILE_STA"):
            son = self.DO_WHILE_STA()
        elif self.isInFirst("RETURN_STA"):
            son = self.RETURN_STA()
        elif self.isInFirst("BREAK_STA"):
            son = self.BREAK_STA()
        elif self.isInFirst("CONTINUE_STA"):
            son = self.CONTINUE_STA()
        else:
            return root
        root.first_son = son
        createEdge(root)
        return root

    # <复合语句> -> {<语句表>}
    # COM_SEN->{ STA_TABLE }
    def COM_SEN(self):
        root = node("COM_SEN")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(3)
            return root
        if token.number != 301:  # {
            self.SyntaxError(3)
            iden = node(" ")
        else:
            self.match()
            iden = node("{")
        root.first_son = iden
        son = self.STA_TABLE()
        iden.brother = son
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(2)
            createEdge(root)
            return root
        if token.number != 302:  # }
            self.SyntaxError(2)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node("}")
        son.brother = iden1
        createEdge(root)
        return root

    # <语句表> -> <语句> <语句1>
    # STA_TABLE->SENTENCE SENTENCE_1
    def STA_TABLE(self):
        root = node("STA_TABLE")
        son = self.SENTENCE()
        root.first_son = son
        son1 = self.SENTENCE_1()
        son.brother = son1
        createEdge(root)
        return root

    # <语句1> -> ε | <语句表>
    # SENTENCE_1->ε|STA_TABLE
    def SENTENCE_1(self):
        root = node("SENTENCE_1")
        if self.isInFirst("STA_TABLE"):
            son = self.STA_TABLE()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFollow("SENTENCE_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(43)
        return root

    # <if语句> ->  if(<表达式>)<语句> <if语句1>
    # IF_STA->if ( BOOL_EXP ) SENTENCE IF_STA_1
    def IF_STA(self):
        root = node("IF_STA")
        token = self.getNextToken()
        if token.number != 111:  # if
            self.SyntaxError(24)
            iden = node(" ")
        else:
            iden = node("if")
            self.match()
        root.first_son = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            return root
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden1 = node(" ")
        else:
            iden1 = node("(")
            self.match()
        iden.brother = iden1
        son = self.BOOL_EXP()
        iden1.brother = son
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            return root
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden2 = node(" ")
        else:
            iden2 = node(")")
            self.match()
        son.brother = iden2
        son1 = self.SENTENCE()
        iden2.brother = son1
        son2 = self.IF_STA_1()
        son1.brother = son2
        createEdge(root)
        return root

    # <if语句1> -> else<语句> | ε
    # IF_STA_1->else SENTENCE|ε
    def IF_STA_1(self):
        root = node("IF_STA_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(40)
            return root
        if token.number == 112:  # else
            self.match()
            iden = node("else")
            root.first_son = iden
            son = self.SENTENCE()
            iden.brother = son
            createEdge(root)
            return root
        elif self.isInFollow("IF_STA_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(40)
        return root

    # <for语句> -> for(<表达式>;<表达式>;<表达式>)<循环语句>
    # FOR_STA->for ( ASSIGN_EXP ; BOOL_EXP ; ASSIGN_EXP ) LOOP_STA
    def FOR_STA(self):
        root = node("FOR_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(25)
            return root
        if token.number != 113:  # for
            self.SyntaxError(25)
            iden1 = node(" ")
        else:
            iden1 = node("for")
            self.match()
        root.first_son = iden1
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            return root
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden2 = node(" ")
        else:
            iden2 = node("(")
            self.match()
        iden1.brother = iden2
        son = self.ASSIGN_EXP()
        iden2.brother = son
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:  # ;
            self.SyntaxError(1)
            iden3 = node(" ")
        else:
            iden3 = node(";")
            self.match()
        son.brother = iden3
        son1 = self.BOOL_EXP()
        iden3.brother = son1
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:  # ;
            self.SyntaxError(1)
            iden4 = node(" ")
        else:
            iden4 = node(";")
            self.match()
        son1.brother = iden4
        son2 = self.ASSIGN_EXP()
        iden4.brother = son2
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            createEdge(root)
            return root
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden5 = node(" ")
        else:
            iden5 = node(")")
            self.match()
        son2.brother = iden5
        son3 = self.SENTENCE()
        iden5.brother = son3
        createEdge(root)
        return root

    # <while语句> -> while(<表达式>)<循环语句>
    # WHILE_STA->while ( BOOL_EXP ) SENTENCE
    def WHILE_STA(self):
        root = node("WHILE_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(26)
            return root
        if token.number != 110:  # while
            self.SyntaxError(26)
            iden = node(" ")
        else:
            iden = node("while")
            self.match()
        root.first_son = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            return root
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden1 = node(" ")
        else:
            iden1 = node("(")
            self.match()
        iden.brother = iden1
        son = self.BOOL_EXP()
        iden1.brother = son
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            createEdge(root)
            return root
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden2 = node(" ")
        else:
            iden2 = node(")")
            self.match()
        son.brother = iden2
        son1 = self.SENTENCE()
        iden2.brother = son1
        createEdge(root)
        return root

    # <do while语句> -> do<循环用复合语句>while(<表达式>);
    # DO_WHILE_STA->do SENTENCE while ( BOOL_EXP ) ;
    def DO_WHILE_STA(self):
        root = node("DO_WHILE_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(27)
            return root
        if token.number != 109:  # do
            self.SyntaxError(27)
            iden = node(" ")
        else:
            iden = node("do")
            self.match()
        root.first_son = iden
        son = self.SENTENCE()
        iden.brother = son
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(26)
            createEdge(root)
            return root
        if token.number != 110:  # while
            self.SyntaxError(26)
            iden1 = node(" ")
        else:
            iden1 = node("while")
            self.match()
        son.brother = iden1
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            createEdge(root)
            return root
        if token.number != 201:  # (
            self.SyntaxError(7)
            iden2 = node(" ")
        else:
            iden2 = node("(")
            self.match()
        iden1.brother = iden2
        son1 = self.BOOL_EXP()
        iden2.brother = son1
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(6)
            createEdge(root)
            return root
        if token.number != 202:  # )
            self.SyntaxError(6)
            iden3 = node(" ")
        else:
            iden3 = node(")")
            self.match()
        son1.brother = iden3
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:  # ;
            self.SyntaxError(1)
            iden4 = node(" ")
        else:
            iden4 = node(";")
            self.match()
        iden3.brother = iden4
        createEdge(root)
        return root

    # <return语句>->return<return语句1>
    # RETURN_STA->return RETURN
    def RETURN_STA(self):
        root = node("RETURN_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(39)
            return root
        if token is None:
            self.SyntaxError(39)
            return root
        if token.number == 106:
            self.match()
            iden = node("return")
            root.first_son = iden
            son = self.RETURN()
            iden.brother = son
            createEdge(root)
            return root
        else:
            self.SyntaxError(39)
        return root

    # <return语句1>->;|<表达式>;
    # RETURN->;|ARI_EXPRESSION ;
    def RETURN(self):
        root = node("RETURN")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            return root
        if token.number == 303:
            self.match()
            iden = node(";")
            root.first_son = iden
            createEdge(root)
            return root
        elif self.isInFirst("ARI_EXPRESSION"):
            son = self.ARI_EXPRESSION()
            root.first_son = son
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(1)
                return root
            if token.number != 303:
                self.SyntaxError(1)
                iden = node(" ")
            else:
                self.match()
                iden = node(";")
            son.brother = iden
            createEdge(root)
            return root
        else:
            self.SyntaxError(1)
        return root

    # <break语句>->break;
    # BREAK_STA->break ;
    def BREAK_STA(self):
        root = node("BREAK_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(28)
            return root
        if token.number != 104:
            self.SyntaxError(28)
            iden = node(" ")
        else:
            iden = node("break")
            self.match()
        root.first_son = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:
            self.SyntaxError(1)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node(";")
        iden.brother = iden1
        createEdge(root)
        return root

    # <continue语句>->continue;
    # CONTINUE_STA->continue ;
    def CONTINUE_STA(self):
        root = node("CONTINUE_STA")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(29)
            return root
        if token.number != 108:
            self.SyntaxError(29)
            iden = node(" ")
        else:
            iden = node("break")
            self.match()
        root.first_son = iden
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(1)
            createEdge(root)
            return root
        if token.number != 303:
            self.SyntaxError(1)
            iden1 = node(" ")
        else:
            self.match()
            iden1 = node(";")
        iden.brother = iden1
        createEdge(root)
        return root

    # iden = 算术表达式
    # ASSIGN_EXP->iden = ARI_EXPRESSION
    def ASSIGN_EXP(self):
        root = node("ASSIGN_EXP")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(10)
            return root
        if token.number == 700:
            self.match()
            iden = node(token.String)
            root.first_son = iden
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(5)
                createEdge(root)
                return root
            if token.number == 219:
                self.match()
                iden1 = node("=")
            else:
                iden1 = node(" ")
                self.SyntaxError(5)
            iden.brother = iden1
            son = self.ARI_EXPRESSION()
            iden1.brother = son
            createEdge(root)
            return root
        else:
            self.SyntaxError(10)
        return root

    # <布尔表达式>-><布尔项><布尔项1>
    # BOOL_EXP->BOOL_TERM BOOL_TERM_1
    def BOOL_EXP(self):
        root = node("BOOL_EXP")
        son = self.BOOL_TERM()
        root.first_son = son
        son1 = self.BOOL_TERM_1()
        son.brother = son1
        createEdge(root)
        return root

    # <关系运算符>->>|<|>=|<=|==|!=
    # RELA_OP->>|<|>=|<=|==|!=
    def RELA_OP(self):
        root = node("RELA_OP")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(30)
            return root
        if token.number not in [211, 212, 213, 214, 215, 216]:
            self.SyntaxError(30)
            return root
        iden = node(token.String)
        self.match()
        root.first_son = iden
        createEdge(root)
        return root

    # <布尔项1>->||<布尔表达式>|ε
    # BOOL_TERM_1->|| BOOL_TERM BOOL_TERM_1|ε
    def BOOL_TERM_1(self):
        root = node("BOOL_TERM_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(38)
            return root
        if token.number == 218:  # ||
            self.match()
            iden = node("||")
            root.first_son = iden
            son = self.BOOL_TERM()
            iden.brother = son
            son1 = self.BOOL_TERM_1()
            son.brother = son1
            createEdge(root)
            return root
        elif self.isInFollow("BOOL_TERM_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(38)
        return root

    # <布尔项>-><布尔因子><布尔因子1>
    # BOOL_TERM->BOOL_FAC BOOL_FAC_1
    def BOOL_TERM(self):
        root = node("BOOL_TERM")
        son = self.BOOL_FAC()
        root.first_son = son
        son1 = self.BOOL_FAC_1()
        son.brother = son1
        createEdge(root)
        return root

    # <布尔因子>-><算术表达式><算数表达式1>|!<布尔表达式>
    # BOOL_FAC->ARI_EXPRESSION ARI_EXPRESSION_1|! BOOL_EXP
    def BOOL_FAC(self):
        root = node("BOOL_FAC")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(31)
            return root
        if token.number == 205:  # !
            self.match()
            iden = node("!")
            root.first_son = iden
            son = self.BOOL_EXP()
            iden.brother = son
            createEdge(root)
            return root
        elif self.isInFirst("ARI_EXPRESSION"):
            son = self.ARI_EXPRESSION()
            root.first_son = son
            son1 = self.ARI_EXPRESSION_1()
            son.brother = son1
            createEdge(root)
            return root
        else:
            self.SyntaxError(31)
        return root

    # <布尔因子1>->&&<布尔项>|ε
    # BOOL_FAC_1->&& BOOL_FAC BOOL_FAC_1|ε
    def BOOL_FAC_1(self):
        root = node("BOOL_FAC_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(32)
            return root
        if token.number == 217:  # &&
            self.match()
            iden = node("&&")
            root.first_son = iden
            son = self.BOOL_FAC()
            iden.brother = son
            son1 = self.BOOL_FAC_1()
            son.brother = son1
            createEdge(root)
            return root
        elif self.isInFollow("BOOL_FAC_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(32)
        return root

    # <算数表达式1>-><关系运算符><算数表达式>|ε
    # ARI_EXPRESSION_1->RELA_OP ARI_EXPRESSION|ε
    def ARI_EXPRESSION_1(self):
        root = node("ARI_EXPRESSION_1")
        if self.isInFirst("RELA_OP"):
            son = self.RELA_OP()
            root.first_son = son
            son1 = self.ARI_EXPRESSION()
            son.brother = son1
            createEdge(root)
            return root
        elif self.isInFollow("ARI_EXPRESSION_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(33)
        return root

    # <算术表达式>-><项><项1>
    # ARI_EXPRESSION->ITEM ITEM_1
    def ARI_EXPRESSION(self):
        root = node("ARI_EXPRESSION")
        son = self.ITEM()
        root.first_son = son
        son1 = self.ITEM_1()
        son.brother = son1
        createEdge(root)
        return root

    # <项>-><因子><因子1>
    # ITEM->FACTOR FACTOR_1
    def ITEM(self):
        root = node("ITEM")
        son = self.FACTOR()
        root.first_son = son
        son1 = self.FACTOR_1()
        son.brother = son1
        createEdge(root)
        return root

    # <项1>->+<算术表达式>|-<算术表达式>|ε
    # ITEM_1->+ ITEM ITEM_1|- ITEM ITEM_1|ε
    def ITEM_1(self):
        root = node("ITEM_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(34)
            return root
        if token.number == 209 or token.number == 210:  # - +
            self.match()
            iden = node(token.String)
            root.first_son = iden
            son = self.ITEM()
            iden.brother = son
            son1 = self.ITEM_1()
            son.brother = son1
            createEdge(root)
            return root
        elif self.isInFollow("ITEM_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(34)
        return root

    # <因子>->(<算数表达式>)|<常量>|<变量>|<函数调用>
    # FACTOR->( ARI_EXPRESSION )|CONSTANT|VAR|FUN_CALL
    # <因子>->(<算数表达式>)|<常量>|<变量><变量1>
    # FACTOR->( ARI_EXPRESSION )|- num_con|- iden|num_con|char_con|iden IDEN1
    def FACTOR(self):
        root = node("FACTOR")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(37)
            return root
        if token.number == 201:  # (
            self.match()
            iden = node("(")
            root.first_son = iden
            son = self.ARI_EXPRESSION()
            iden.brother = son
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(6)
                createEdge(root)
                return root
            if token.number != 202:  # )
                self.SyntaxError(6)
                iden1 = node(" ")
            else:
                iden1 = node(")")
                self.match()
            son.brother = iden1
            createEdge(root)
            return root
        elif token.number == 210:  # -
            self.match()
            iden = node("-")
            root.first_son = iden
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(20)
                createEdge(root)
                return root
            if token.number in [400, 700, 800, 900, 1000]:  # 数值型常量或字符型常量
                self.match()
                iden1 = node(token.String)
            else:
                self.SyntaxError(20)
                iden1 = node(" ")
            iden.brother = iden1
            createEdge(root)
            return root
        elif token.number in [400, 500, 600, 800, 900, 1000]:  # 数值型常量或字符型常量
            self.match()
            iden = node(token.String)
            root.first_son = iden
            createEdge(root)
            return root
        elif token.number == 700:
            self.match()
            iden = node(token.String)
            root.first_son = iden
            son = self.IDEN1()
            iden.brother = son
            createEdge(root)
            return root
        else:
            self.SyntaxError(37)
        return root

    # <变量1>->(<实参列表>)|ε
    # IDEN1->( ARG_LIST )|ε
    def IDEN1(self):
        root = node("IDEN1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(7)
            return root
        if token.number == 201:  # (
            self.match()
            iden = node("(")
            root.first_son = iden
            son = self.ARG_LIST()
            iden.brother = son
            token = self.getNextToken()
            if token is None:
                self.SyntaxError(6)
                createEdge(root)
                return root
            if token.number != 202:  # )
                self.SyntaxError(6)
                iden1 = node(" ")
            else:
                iden1 = node(")")
                self.match()
            son.brother = iden1
            createEdge(root)
            return root
        elif token.number in [225, 226]:  # ++ --
            self.match()
            iden = node(token.String)
            root.first_son = iden
            createEdge(root)
            return root
        elif self.isInFollow("IDEN1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(7)
        return root

    # <实参列表>-><实参>| ε
    # ARG_LIST->ARG|ε
    def ARG_LIST(self):
        root = node("ARG_LIST")
        if self.isInFirst("ARG"):
            son = self.ARG()
            root.first_son = son
            createEdge(root)
            return root
        elif self.isInFollow("ARG_LIST"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(35)
        return root

    # <实参>-><实参1><实参2>
    # ARG->ARI_EXPRESSION ARG1
    def ARG(self):
        root = node("ARG")
        son = self.ARI_EXPRESSION()
        root.first_son = son
        son1 = self.ARG1()
        son.brother = son1
        createEdge(root)
        return root

    # ARG1->, ARG|ε
    def ARG1(self):
        root = node("ARG1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(4)
            return root
        if token.number == 304:  # ,
            self.match()
            iden = node(",")
            root.first_son = iden
            son = self.ARG()
            iden.brother = son
            createEdge(root)
            return root
        elif self.isInFollow("ARG1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(4)
        return root

    # <因子1>->*<项>|/<项>|%<项>|ε
    # FACTOR_1->* FACTOR FACTOR_1|/ FACTOR FACTOR_1|% FACTOR FACTOR_1|ε
    def FACTOR_1(self):
        root = node("ITEM_1")
        token = self.getNextToken()
        if token is None:
            self.SyntaxError(36)
            return root
        if token.number in [206, 207, 208]:  # * / %
            self.match()
            iden = node(token.String)
            root.first_son = iden
            son = self.FACTOR()
            iden.brother = son
            son1 = self.FACTOR_1()
            son.brother = son1
            createEdge(root)
            return root
        elif self.isInFollow("FACTOR_1"):
            null = node("ε")
            root.first_son = null
            createEdge(root)
            return root
        else:
            self.SyntaxError(36)
        return root


if __name__ == '__main__':
    with open("C:/Users/YL139/Desktop/byyl/test/byxt/zjdm_example/test0.1.txt", "r", encoding="utf-8") as file:
        files = file.read()
    result = Auto(files)
    tokenList, errorList = result.GetResult()
    re = GramAnalyzer(tokenList)
    re.Begin()
    # Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/yffx_error.txt', mode='w', encoding='UTF-8')
    # for i in re.errorList:
    #     Note.write(str(i))
    #     # print(i)
    # Note.close()
