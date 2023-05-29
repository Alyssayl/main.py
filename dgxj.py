i = 0


def E():  # E->TG
    if T() and G():
        return True
    else:
        return False


def T():  # T->FS
    if F() and S():
        return True
    else:
        return False


def G():  # G->+TG|-TG
    global i
    if line[i] == '+' or line[i] == '-':
        i = i + 1
        if T() and G():
            return True
        else:
            return False
    else:
        return True


def S():  # S->*FS|/FS
    global i
    if line[i] == '*' or line[i] == '/':
        i = i + 1
        if F() and S():
            return True
        else:
            return False
    else:
        return True


def F():  # F->(E)|i
    global i
    if line[i] == 'i':
        i = i + 1
        return True
    if line[i] == '(':
        i = i + 1
        if E() and line[i] == ')':
            i = i + 1
            return True
    return False


if __name__ == "__main__":
    print("---------递归下降分析程序---------")
    while True:
        i = 0
        line = input("输入符号串（包括+-*/()i）: ")
        if line == 'q':
            break
        line = line + '#'
        if E() and line[i] == '#':
            print("输出结果：" + line[0:len(line) - 1] + "为合法符号串")
        else:
            print("输出结果：" + line[0:len(line) - 1] + "为非法的符号串")
            print("参考错误：出错字符位于第" + str(i + 1) + "处, 该字符为 " + line[i])
