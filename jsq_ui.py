from PyQt5 import QtCore, QtGui, QtWidgets
# from main import ROOT
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jsq import jsq
from zjdm import Zjdmsc


class jsq_ui(object):
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
        # self.textEdit.setFont(font)
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

        self.textEdit1 = QtWidgets.QTextEdit(self.widget)
        self.textEdit1.setGeometry(QtCore.QRect(300, 20, 371, 41))
        font = QtGui.QFont()
        font.setFamily("UI")
        font.setPointSize(10)
        self.textEdit1.setFont(font)
        self.textEdit1.setObjectName("textEdit1")
        self.horizontalLayout.addWidget(self.textEdit1)

        # self.pushButton_4.clicked.connect(self.result_show())
        self.pushButton_4.clicked.connect(lambda: self.result_show())

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def result_show(self):
        syner = Zjdmsc("C:/Users/YL139/Desktop/byyl/test/byxt/topLeft.txt")
        syner.run()
        quaternion_list = enumerate(syner.quaternary_list)
        for i, k in enumerate(syner.quaternary_list):
            quaternion_list = k
        s = quaternion_list
        four = self.textEdit.toPlainText()
        result = jsq(s, four)

        self.textEdit1.setText(result)


    def refresh(self):
        self.pushButton_4.setEnabled(True)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Interpreter"))
        self.label.setText(_translate("Form", "请输入数值:"))
        self.pushButton_4.setText(_translate("Form", "开始"))
        # 当内容改变时
        self.textEdit.textChanged.connect(self.refresh)
