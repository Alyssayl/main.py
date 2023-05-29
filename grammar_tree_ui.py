from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class grammar_tree_ui(object):
    def setupUi(self, TREE, name=""):
        from PIL import Image
        file_path = 'C:/Users/YL139/Desktop/byyl/test/byxt/TREE/grammar_tree.png'.format(name)
        img = Image.open(file_path)
        w = img.width  # 图片的宽
        h = img.height  # 图片的高

        TREE.setObjectName("TREE")
        TREE.resize(w * 0.01, h * 0.01)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(TREE)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(TREE)
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

        self.retranslateUi(TREE, name.upper())
        QtCore.QMetaObject.connectSlotsByName(TREE)

    def retranslateUi(self, TREE, name=""):
        _translate = QtCore.QCoreApplication.translate
        TREE.setWindowTitle(_translate("TREE", name))

