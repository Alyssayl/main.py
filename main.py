import sys
import webbrowser

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTextEdit, QSplitter, QFrame, QHBoxLayout, QWidget, QApplication, QMainWindow, QAction, \
    QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
from cffx import Lexer
from Auto import Auto
from NFA_DFA_zxhdfa_UI import nfa_dfa_zxhdfa_ui
from yffx import GramAnalyzer
from pdf_png import pdf_png
from grammar_tree_ui import grammar_tree_ui
from zjdm import Zjdmsc
from jsq_ui import jsq_ui
from mbdm import assemcodes


class ROOT(QMainWindow):
    def __init__(self):
        super(ROOT, self).__init__()

        self.resize(1000, 700)
        self.setWindowTitle("编译系统")
        self.setmenu()
        self.setchuangkou()

    def setmenu(self):
        # ##制作菜单
        # 获取菜单栏
        bar = self.menuBar()
        # 往菜单栏添加项目“文件”
        file = bar.addMenu("文件")
        # # 给菜单项目添加子项目
        # file.addAction('清空')

        # 往菜单栏添加项目“编辑”
        editfile = bar.addMenu("编辑")
        # 给菜单项目添加子项目
        editfile.addAction('复制')
        editfile.addAction('粘贴')

        # 创建菜单“文件”下的“保存”按钮
        savefileButton = QAction('savefile', self)
        savefileButton.setSeparator(0)
        savefileButton.setShortcut('Ctrl + s')
        savefileButton.setText("保存")
        savefileButton.triggered.connect(self.savefile)

        # 创建菜单“文件”下的“打开”按钮
        openfileButton = QAction('openfile', self)
        openfileButton.setSeparator(0)
        openfileButton.setText("打开")
        openfileButton.triggered.connect(self.openfile)

        # 创建菜单“文件”下的“退出”按钮
        exitButton = QAction('Exit', self)
        # 0或非0有效
        exitButton.setSeparator(0)
        # 设置action的快捷键
        exitButton.setShortcut('Ctrl+Q')
        # 更改action的title
        exitButton.setText("退出")
        # 设置action的信号插槽方法
        exitButton.triggered.connect(self.close)

        # 往菜单栏添加项目“词法分析”
        cffx = bar.addMenu("词法分析")

        # 创建“词法分析”的“手动词法分析”按钮
        sdcffxButton = QAction('sdcffx', self)
        sdcffxButton.setSeparator(0)
        sdcffxButton.setText("手动词法分析")
        sdcffxButton.triggered.connect(self.sdcffx)

        # 创建“词法分析”的“自动词法分析”按钮
        zdcffxButton = QAction('zdcffx', self)
        zdcffxButton.setSeparator(0)
        zdcffxButton.setText("自动词法分析")
        zdcffxButton.triggered.connect(self.zdcffx)

        # 创建“词法分析”的“NFA_DFA_zxhdfa”按钮
        zdjButton = QAction('zdj', self)
        zdjButton.setSeparator(0)
        zdjButton.setText("NFA_DFA_zxhdfa")
        zdjButton.triggered.connect(self.NFA_DFA_zxhdfa_ui)

        # 创建菜单的“语法分析”按钮
        yffxButton = QAction('yffx', self)
        yffxButton.setSeparator(0)
        yffxButton.setText("语法分析")
        yffxButton.triggered.connect(self.yffx)

        # 创建菜单的“中间代码生成”按钮
        zjdmButton = QAction('zjdmsc', self)
        zjdmButton.setSeparator(0)
        zjdmButton.setText("中间代码生成")
        zjdmButton.triggered.connect(self.zjdmsc)

        # 创建菜单的“解释器”按钮
        jsqButton = QAction('jsq', self)
        jsqButton.setSeparator(0)
        jsqButton.setText("解释器")
        jsqButton.triggered.connect(self.go_run)

        # # 创建菜单的“目标代码生成”按钮
        # mbdmButton = QAction('mbdmsc', self)
        # mbdmButton.setSeparator(0)
        # mbdmButton.setText("目标代码生成")
        # mbdmButton.triggered.connect(self.mbdmsc)

        # 创建菜单的“帮助”按钮
        helpButton = QAction('openchm', self)
        helpButton.setSeparator(0)
        helpButton.setText("帮助")
        helpButton.triggered.connect(self.openchm)

        # 开启action状态栏
        self.statusBar()
        # 可以将单个action按钮添加到菜单中：
        file.addAction(openfileButton)
        file.addAction(savefileButton)
        file.addAction(exitButton)
        cffx.addAction(sdcffxButton)
        cffx.addAction(zdcffxButton)
        cffx.addAction(zdjButton)
        bar.addAction(yffxButton)
        bar.addAction(zjdmButton)
        # bar.addAction(mbdmButton)
        bar.addAction(jsqButton)
        bar.addAction(helpButton)

    def setchuangkou(self):
        # ##分割窗口
        # 创建文本分割框
        self.topLeft = QTextEdit()
        self.topRight = QTextEdit()
        self.bottom = QTextEdit()
        # 添加水平分割线
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.topLeft)
        splitter1.addWidget(self.topRight)
        splitter1.setSizes([200, 200])  # 设置水平左右框的初始比例

        # 添加垂直分割线
        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.bottom)
        splitter2.setSizes([500, 200])  # 设置垂直上下框的初始比例

        # 创建水平布局
        layout = QHBoxLayout()
        layout.addWidget(splitter2)

        mainFrame = QWidget()
        mainFrame.setLayout(layout)
        self.setCentralWidget(mainFrame)

    def savefile(self):
        code = self.topLeft.toPlainText()
        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt', mode='w', encoding='UTF-8')
        Note.write(str(code))
        Note.close()

    # 定义打开文件夹目录，并将文件内容读入到topLeft文本框中的函数
    def openfile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'C:/Users/YL139/Desktop/byyl/test/byxt/csyl')
        if fname[0]:
            f = open(fname[0], 'r')
            with f:
                d = f.read()
                self.topLeft.setText(d)
                Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt', mode='w', encoding='UTF-8')
                Note.write(str(d))
                Note.close()

    # 手动词法分析
    def sdcffx(self):
        lexer = Lexer(filename="C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt")
        lexer.run()
        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/cffxjg.txt', mode='w', encoding='UTF-8')
        for i, k in enumerate(lexer.token):
            Note.write(str(k))
            Note.write('\n')
        Note.close()
        Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/cffxjg.txt', 'r', encoding='UTF-8')
        with Note1:
            self.topRight.setText(Note1.read())
        error = 'This code has no errors!'
        if lexer.error:
            self.bottom.setText(lexer.error)
        else:
            self.bottom.setText(error)

    # 自动词法分析
    def zdcffx(self):
        with open('C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt', 'r', encoding='UTF-8') as f:
            data = f.read()
        result = Auto(data)
        error = 'This code has no errors!'
        tokenList, errorList = result.GetResult()  # 返回token串与错误信息
        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/tokenList.txt', mode='w', encoding='UTF-8')
        for i in tokenList:
            token = '( ' + str(i.ROW) + ', ' + str(i.number) + ', ' + i.String + ' )'
            Note.write(str(token))
            Note.write('\n')
        Note.close()
        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/tokenList.txt', 'r', encoding='UTF-8')
        with Note:
            self.topRight.setText(Note.read())
        if errorList:
            self.bottom.setText(errorList)
        else:
            self.bottom.setText(error)

    # 自动机界面
    def NFA_DFA_zxhdfa_ui(self):
        self.form2 = QtWidgets.QWidget()
        self.ui2 = nfa_dfa_zxhdfa_ui()
        self.ui2.setupUi(self.form2)
        self.form2.show()

    # 语法分析
    def yffx(self):
        with open("C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt", "r", encoding="utf-8") as file:
            files = file.read()
        result = Auto(files)
        tokenList, errorList = result.GetResult()
        re = GramAnalyzer(tokenList)
        re.Begin()
        pdf_png(r"C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.gv.pdf", r"C:/Users/YL139/Desktop/byyl/test"
                                                                                   r"/byxt/TREE", 1, 1, 0)
        self.form3 = QtWidgets.QWidget()
        self.ui3 = grammar_tree_ui()
        self.ui3.setupUi(self.form3)
        self.form3.resize(2000, 1000)
        self.form3.show()

        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/yffx_error.txt', mode='w', encoding='UTF-8')
        for i in re.errorList:
            Note.write(str(i))
        Note.close()

    # 中间代码生成
    def zjdmsc(self):
        syner = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt")
        syner.run()
        quaternary_list = syner.now_quaternary
        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/zjdm.txt', mode='w', encoding='UTF-8')
        for i, k in enumerate(quaternary_list):
            Note.write(str(k))
            Note.write('\n')
        Note.close()
        Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/zjdm.txt', 'r', encoding='UTF-8')
        with Note1:
            self.topRight.setText(Note1.read())

    # 目标代码生成
    def mbdmsc(self):
        syner = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt")
        syner.run()
        quaternion_list = enumerate(syner.quaternary_list)
        for i, k in enumerate(syner.quaternary_list):
            quaternion_list = k
        result = assemcodes(quaternion_list)
        Note = open('C:/Users/YL139/Desktop/byyl/test/byxt/mbdm.txt', mode='w', encoding='UTF-8')
        for i, k in enumerate(result):
            # print(k)
            Note.write(str(k))
        Note.close()
        Note1 = open('C:/Users/YL139/Desktop/byyl/test/byxt/mbdm.txt', 'r', encoding='UTF-8')
        with Note1:
            self.bottom.setText(Note1.read())

    def go_run(self):  # 分析四元式，运算结果
        self.form4 = QtWidgets.QWidget()
        self.ui4 = jsq_ui()
        self.ui4.setupUi(self.form4)
        self.form4.resize(2000, 1000)
        self.form4.show()

    def openchm(self):
        fname = webbrowser.open("C:/Users/YL139/Desktop/byyl/test/HELP/HELP.chm")
        print(fname)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('C:/Users/YL139/Desktop/byyl/test/byxt/logo.ico'))  # 设置窗体图标
    main = ROOT()
    main.show()
    sys.exit(app.exec_())
