# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'imageCompareDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from qtpy.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from qtpy.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from qtpy.QtWidgets import (QAbstractButton, QAbstractScrollArea, QApplication, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

from widgets.fst3DGraphicsView import Fst3DGraphicsView

class Ui_ImageCompareDialog(object):
    def setupUi(self, ImageCompareDialog):
        if not ImageCompareDialog.objectName():
            ImageCompareDialog.setObjectName(u"ImageCompareDialog")
        ImageCompareDialog.resize(1065, 595)
        self.verticalLayout = QVBoxLayout(ImageCompareDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.leftVerticalLayout = QVBoxLayout()
        self.leftVerticalLayout.setObjectName(u"leftVerticalLayout")
        self.leftGraphicsView = Fst3DGraphicsView(ImageCompareDialog)
        self.leftGraphicsView.setObjectName(u"leftGraphicsView")
        self.leftGraphicsView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.leftVerticalLayout.addWidget(self.leftGraphicsView)

        self.leftImageLabel = QLabel(ImageCompareDialog)
        self.leftImageLabel.setObjectName(u"leftImageLabel")
        self.leftImageLabel.setAlignment(Qt.AlignCenter)

        self.leftVerticalLayout.addWidget(self.leftImageLabel)


        self.horizontalLayout.addLayout(self.leftVerticalLayout)

        self.rightVerticalLayout = QVBoxLayout()
        self.rightVerticalLayout.setObjectName(u"rightVerticalLayout")
        self.rightGraphicsView = Fst3DGraphicsView(ImageCompareDialog)
        self.rightGraphicsView.setObjectName(u"rightGraphicsView")
        self.rightGraphicsView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.rightVerticalLayout.addWidget(self.rightGraphicsView)

        self.rightImageLabel = QLabel(ImageCompareDialog)
        self.rightImageLabel.setObjectName(u"rightImageLabel")
        self.rightImageLabel.setAlignment(Qt.AlignCenter)

        self.rightVerticalLayout.addWidget(self.rightImageLabel)


        self.horizontalLayout.addLayout(self.rightVerticalLayout)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(ImageCompareDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Discard|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ImageCompareDialog)
        self.buttonBox.accepted.connect(ImageCompareDialog.accept)
        self.buttonBox.rejected.connect(ImageCompareDialog.reject)

        QMetaObject.connectSlotsByName(ImageCompareDialog)
    # setupUi

    def retranslateUi(self, ImageCompareDialog):
        ImageCompareDialog.setWindowTitle(QCoreApplication.translate("ImageCompareDialog", u"Dialog", None))
        self.leftImageLabel.setText(QCoreApplication.translate("ImageCompareDialog", u"Unprocessed Image", None))
        self.rightImageLabel.setText(QCoreApplication.translate("ImageCompareDialog", u"Processed Image", None))
    # retranslateUi

