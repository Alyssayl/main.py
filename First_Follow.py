class Get_First_Follow:
    def __init__(self, sentences):
        self.sentences = sentences
        self.FOLLOW = {}
        self.FIRST = {}  # 记录非终结符的FIRST集
        self.first = {}  # 记录非终结符某产生式的first集

    def GetResult(self):
        self.initial()
        self.getFirst()
        for i in range(130):
            self.setFirst()
        for i in range(130):
            self.setFollow()
        return self.FIRST, self.first, self.FOLLOW

    def Print(self):
        PrintList(self.FIRST, self.first, self.FOLLOW)

    def isLl1(self):
        isLL1(self.FIRST, self.first, self.FOLLOW)

    # 初始化first集和follow集字典中的值为空
    def initial(self):
        for str in self.sentences:
            self.FIRST[str[0]] = []
            self.FOLLOW[str[0]] = []
            s = getStr(str)  # 记录str的长度
            self.first[s] = []  # 非终结符产生式first的集合
        self.FOLLOW[self.sentences[0][0]] = ["#"]  # 规则1

    # 求first集 中第一部分针对 A->a  直接推出第一个字符为终结符 部分 规则1与2
    def getFirst(self):
        for str in self.sentences:
            if not str[1].isupper():
                re = self.FIRST.get(str[0])
                re.append(str[1])
                self.FIRST[str[0]] = re
                s = getStr(str)
                re1 = self.first.get(s)
                re1.append(str[1])
                self.first[s] = re1

    # 求first第二部分 针对 A -> B型  把B的first集加到A 的first集合中 规则3
    def getFirst_1(self):
        for str in self.sentences:
            s = getStr(str)
            if str[1].isupper():
                # 如果型如A ->BC 则把B的first集非空元素加到A的first集中去
                self.FIRST[str[0]] = add(self.FIRST.get(str[0]), self.FIRST.get(str[1]), True)
                self.first[s] = add(self.first.get(s), self.FIRST.get(str[1]), True)
                # 如果型如A ->X1X2X3...Xka
                flag = True
                pre = str[1]
                # 当X1X2X3...Xi为空1<=i<k，将Xi..Xk的非空元素加入A
                for i in str[2:]:
                    # pre不能推出空，后面元素不用看了
                    if 'ε' not in self.FIRST.get(pre):
                        flag = False  # A->BCD且B不能=>ε
                        break
                    # pre有空，但是当前的元素是终结符，加入A，后面不用看了
                    if not i.isupper():
                        re = self.FIRST[str[0]]
                        re.append(i)
                        self.FIRST[str[0]] = re
                        re1 = self.first[s]
                        re1.append(i)
                        self.first[s] = re1
                        flag = False
                        break
                    # pre有空，且当前元素Xi是非终结符，将Xi的非空first集加入A
                    self.FIRST[str[0]] = add(self.FIRST.get(str[0]), self.FIRST.get(i), True)
                    self.first[s] = add(self.first.get(s), self.FIRST.get(i), True)
                    pre = i
                # X1X2X3...Xk全推出空，将a的first加入A，包括非空元素
                if flag and str[-1].isupper():
                    self.FIRST[str[0]] = add(self.FIRST.get(str[0]), self.FIRST.get(str[-1]), False)
                    self.first[s] = add(self.first.get(s), self.FIRST.get(str[-1]), False)

    def setFirst(self):
        self.getFirst_1()
        # 去除重复项
        for i, j in self.FIRST.items():
            temp = []
            for word in list(set(j)):
                temp.append(word)
            self.FIRST[i] = temp
        for i, j in self.first.items():
            temp = []
            for word in list(set(j)):
                temp.append(word)
            self.first[i] = temp

    def setFollow(self):
        self.getFollow()
        # 去除重复项
        for i, j in self.FOLLOW.items():
            temp = []
            for word in list(set(j)):
                temp.append(word)
            self.FOLLOW[i] = temp

    # 计算follow集的第一部分，先计算 S -> Ab 类型的
    def getFollow(self):
        for str in self.sentences:
            # 如果是 A->a或A->B
            if len(str) == 2:
                if str[1].isupper():
                    self.FOLLOW[str[1]] = add(self.FOLLOW.get(str[1]), self.FOLLOW.get(str[0]), True)
                continue
            # 否则执行下面的操作
            else:
                # 将->后面的分开再倒序
                temp = []
                for i in str[1:]:
                    temp.append(i)
                temp.reverse()
                # 如果非终结符在句型的末端 规则4
                if temp[0].isupper():
                    # B->aA 或B->aAb且b=>ε Follow(A) = Follow(A) + Follow(B)
                    self.FOLLOW[temp[0]] = add(self.FOLLOW.get(temp[0]), self.FOLLOW.get(str[0]), True)
                pre = temp[0]
                flag = True
                for i in temp[1:]:
                    if not i.isupper():  # i是终结符
                        flag = False
                    else:  # i是非终结符
                        if pre.isupper():  # B->aAXb Follow(A) = Follow(A) + First(Xb\ε)
                            self.FOLLOW[i] = add(self.FOLLOW.get(i), self.FIRST.get(pre), True)
                            if flag and 'ε' not in self.FIRST.get(pre):
                                flag = False  # 或B->aAb且b不能=>ε
                            if flag:  # B->aAb且b=>ε
                                self.FOLLOW[i] = add(self.FOLLOW.get(i), self.FOLLOW.get(str[0]), True)
                        else:
                            re = self.FOLLOW[i]
                            re.append(pre)
                            self.FOLLOW[i] = re
                    pre = i


def PrintList(FIRST, first, FOLLOW):
    for i, j in FIRST.items():
        print("FIRST(" + i + ")" + " = " + str(j))
    print()
    for i, j in first.items():
        print("first(" + i + ")" + " = " + str(j))
    print()
    for i, j in FOLLOW.items():
        print("FOLLOW(" + i + ")" + " = " + str(j))


def getStr(str):
    s = ""
    for i in str:
        s += i
        s += "`"
    s = s.rstrip("`")
    return s


def add(start, end, flag):
    if start == end:
        return start
    for i in end:
        if i != "ε":
            start.append(i)
        elif not flag:
            start.append(i)
    return start


def isLL1(FIRST, first, FOLLOW):
    for i in FIRST:
        if "ε" in FIRST[i]:
            re = []
            for j in FIRST[i]:
                re.append(j)
            for k in FOLLOW[i]:
                re.append(k)
            if len(list(set(re))) != len(re):
                print(i + "有ε，FIRST 与 FOLLOW相交")
    for s in FIRST:
        temp = findExp(first, s)
        if len(temp) != len(FIRST[s]):
            print(s + "的候选式first集有交集")


def findExp(first, sentence):
    re = []
    for i in first:
        s = i.split("`")[0]
        if s == sentence:
            for j in first.get(i):
                re.append(j)
    return re


# if __name__ == '__main__':
#     sentences = [
#         ['E', 'T', 'G'],
#         ['G', '+', 'T', 'G'],
#         ['G', '-', 'T', 'G'],
#         ['G', 'ε'],
#         ['T', 'F', 'S'],
#         ['S', '*', 'F', 'S'],
#         ['S', '/', 'F', 'S'],
#         ['S', '%', 'F', 'S'],
#         ['S', 'ε'],
#         ['F', '(', 'E', ')'],
#         ['F', 'i']
#     ]
#     result = Get_First_Follow(sentences)
#     result.GetResult()
#     result.Print()
