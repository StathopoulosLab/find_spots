# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/drumph/Develop/Stathopoulos/find_spots/imageCompareDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ImageCompareDialog(object):
    def setupUi(self, ImageCompareDialog):
        ImageCompareDialog.setObjectName("ImageCompareDialog")
        ImageCompareDialog.resize(1065, 595)
        self.verticalLayout = QtWidgets.QVBoxLayout(ImageCompareDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftVerticalLayout = QtWidgets.QVBoxLayout()
        self.leftVerticalLayout.setObjectName("leftVerticalLayout")
        self.leftGraphicsView = Fst3DGraphicsView(ImageCompareDialog)
        self.leftGraphicsView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.leftGraphicsView.setObjectName("leftGraphicsView")
        self.leftVerticalLayout.addWidget(self.leftGraphicsView)
        self.leftImageLabel = QtWidgets.QLabel(ImageCompareDialog)
        self.leftImageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.leftImageLabel.setObjectName("leftImageLabel")
        self.leftVerticalLayout.addWidget(self.leftImageLabel)
        self.horizontalLayout.addLayout(self.leftVerticalLayout)
        self.rightVerticalLayout = QtWidgets.QVBoxLayout()
        self.rightVerticalLayout.setObjectName("rightVerticalLayout")
        self.rightGraphicsView = Fst3DGraphicsView(ImageCompareDialog)
        self.rightGraphicsView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.rightGraphicsView.setObjectName("rightGraphicsView")
        self.rightVerticalLayout.addWidget(self.rightGraphicsView)
        self.rightImageLabel = QtWidgets.QLabel(ImageCompareDialog)
        self.rightImageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.rightImageLabel.setObjectName("rightImageLabel")
        self.rightVerticalLayout.addWidget(self.rightImageLabel)
        self.horizontalLayout.addLayout(self.rightVerticalLayout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(ImageCompareDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Discard|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ImageCompareDialog)
        self.buttonBox.accepted.connect(ImageCompareDialog.accept)
        self.buttonBox.rejected.connect(ImageCompareDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImageCompareDialog)

    def retranslateUi(self, ImageCompareDialog):
        _translate = QtCore.QCoreApplication.translate
        ImageCompareDialog.setWindowTitle(_translate("ImageCompareDialog", "Dialog"))
        self.leftImageLabel.setText(_translate("ImageCompareDialog", "Unprocessed Image"))
        self.rightImageLabel.setText(_translate("ImageCompareDialog", "Processed Image"))

from widgets.fst3DGraphicsView import Fst3DGraphicsView
