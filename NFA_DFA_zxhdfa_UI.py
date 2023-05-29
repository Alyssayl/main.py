from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from NFA_DFA_zxhdfa import *


class Ui_NFA(object):
    def setupUi(self, NFA, name=""):
        from PIL import Image
        file_path = 'C:/Users/YL139/Desktop/byyl/test/byxt/NFA_DFA_zxhdfa/{}.gv.png'.format(name)
        img = Image.open(file_path)
        w = img.width  # 图片的宽
        h = img.height  # 图片的高

        NFA.setObjectName("NFA")
        NFA.resize(w * 1.2, h * 1.5)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(NFA)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(NFA)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.groupBox)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.horizontalLayout_2.addWidget(self.groupBox)

        self.graphicsView.scene_img = QGraphicsScene()
        self.imgShow = QPixmap()
        self.imgShow.load(file_path)
        self.imgShowItem = QGraphicsPixmapItem()
        self.imgShowItem.setPixmap(QPixmap(self.imgShow))
        self.imgShowItem.setPixmap(QPixmap(self.imgShow).scaled(w, h))  # 设定尺寸
        self.graphicsView.scene_img.addItem(self.imgShowItem)
        self.graphicsView.setScene(self.graphicsView.scene_img)

        self.retranslateUi(NFA, name.upper())
        QtCore.QMetaObject.connectSlotsByName(NFA)

    def retranslateUi(self, NFA, name=""):
        _translate = QtCore.QCoreApplication.translate
        NFA.setWindowTitle(_translate("NFA", name))


class nfa_dfa_zxhdfa_ui(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setEnabled(True)
        Form.resize(701, 160)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMaximumSize(QtCore.QSize(701, 160))
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 681, 80))
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(300, 20, 371, 41))
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(14)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 20, 271, 41))
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 90, 681, 61))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setGeometry(QtCore.QRect(130, 20, 397, 31))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_4 = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(12)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_1 = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(12)
        self.pushButton_1.setFont(font)
        self.pushButton_1.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton_1)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(12)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(12)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)

        self.pushButton_4.setEnabled(True)
        self.pushButton_1.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

        self.pushButton_4.clicked.connect(self.botton_display)
        self.pushButton_4.clicked.connect(lambda: self.generate_auto_mata())

        self.pushButton_1.clicked.connect(lambda: self.png_display("NFA"))
        self.pushButton_2.clicked.connect(lambda: self.png_display("DFA"))
        self.pushButton_3.clicked.connect(lambda: self.png_display("zxhdfa"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def botton_display(self):
        self.pushButton_4.setEnabled(False)
        self.pushButton_1.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)

    def png_display(self, name=""):
        self.png_widget = QWidget()
        self.png_window = Ui_NFA()
        self.png_window.setupUi(self.png_widget, name)
        self.png_widget.show()

    def generate_auto_mata(self):
        exp = self.textEdit.toPlainText()
        if exp:
            ss = nfa_dfa_zxhdfa(exp)
            ss.exp_to_nfa()
            ss.show()
            ss.trans_dfa()
            ss.simplify_dfa()
            ss.draw_png()
        else:
            self.pushButton_4.setEnabled(True)
            self.pushButton_1.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)

    def refresh(self):
        self.pushButton_4.setEnabled(True)
        self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_1.setEnabled(False)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "NFA_DFA_zxhdfa"))
        self.label.setText(_translate("Form", "请输入正则表达式:"))
        self.pushButton_4.setText(_translate("Form", "开始"))
        self.pushButton_1.setText(_translate("Form", "NFA"))
        self.pushButton_2.setText(_translate("Form", "DFA"))
        self.pushButton_3.setText(_translate("Form", "zxhdfa"))
        # 当内容改变时
        self.textEdit.textChanged.connect(self.refresh)
