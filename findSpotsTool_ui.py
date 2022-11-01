# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'findSpotsTool.ui'
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
from qtpy.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListView, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1147, 734)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.leftVerticalLayout = QVBoxLayout()
        self.leftVerticalLayout.setObjectName(u"leftVerticalLayout")
        self.pendingFilesHorizontalLayout = QHBoxLayout()
        self.pendingFilesHorizontalLayout.setObjectName(u"pendingFilesHorizontalLayout")
        self.pendingFilesLabel = QLabel(self.centralwidget)
        self.pendingFilesLabel.setObjectName(u"pendingFilesLabel")

        self.pendingFilesHorizontalLayout.addWidget(self.pendingFilesLabel)

        self.addFilesHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.pendingFilesHorizontalLayout.addItem(self.addFilesHorizontalSpacer)

        self.addFilesButton = QPushButton(self.centralwidget)
        self.addFilesButton.setObjectName(u"addFilesButton")

        self.pendingFilesHorizontalLayout.addWidget(self.addFilesButton)


        self.leftVerticalLayout.addLayout(self.pendingFilesHorizontalLayout)

        self.pendingFilesListView = QListView(self.centralwidget)
        self.pendingFilesListView.setObjectName(u"pendingFilesListView")

        self.leftVerticalLayout.addWidget(self.pendingFilesListView)

        self.activeFileHorizontalLayout = QHBoxLayout()
        self.activeFileHorizontalLayout.setObjectName(u"activeFileHorizontalLayout")
        self.activeFileLabel = QLabel(self.centralwidget)
        self.activeFileLabel.setObjectName(u"activeFileLabel")

        self.activeFileHorizontalLayout.addWidget(self.activeFileLabel)

        self.activeFileLineEdit = QLineEdit(self.centralwidget)
        self.activeFileLineEdit.setObjectName(u"activeFileLineEdit")
        self.activeFileLineEdit.setReadOnly(True)

        self.activeFileHorizontalLayout.addWidget(self.activeFileLineEdit)


        self.leftVerticalLayout.addLayout(self.activeFileHorizontalLayout)

        self.progressBarHorizontalLayout = QHBoxLayout()
        self.progressBarHorizontalLayout.setObjectName(u"progressBarHorizontalLayout")
        self.progressBarLabel = QLabel(self.centralwidget)
        self.progressBarLabel.setObjectName(u"progressBarLabel")

        self.progressBarHorizontalLayout.addWidget(self.progressBarLabel)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.progressBarHorizontalLayout.addWidget(self.progressBar)


        self.leftVerticalLayout.addLayout(self.progressBarHorizontalLayout)

        self.completedFilesHorizontalLayout = QHBoxLayout()
        self.completedFilesHorizontalLayout.setObjectName(u"completedFilesHorizontalLayout")
        self.completedFilesLabel = QLabel(self.centralwidget)
        self.completedFilesLabel.setObjectName(u"completedFilesLabel")

        self.completedFilesHorizontalLayout.addWidget(self.completedFilesLabel)

        self.completedFilesHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.completedFilesHorizontalLayout.addItem(self.completedFilesHorizontalSpacer)

        self.clearCompletedFilesPushButton = QPushButton(self.centralwidget)
        self.clearCompletedFilesPushButton.setObjectName(u"clearCompletedFilesPushButton")

        self.completedFilesHorizontalLayout.addWidget(self.clearCompletedFilesPushButton)


        self.leftVerticalLayout.addLayout(self.completedFilesHorizontalLayout)

        self.completedFilesListView = QListView(self.centralwidget)
        self.completedFilesListView.setObjectName(u"completedFilesListView")

        self.leftVerticalLayout.addWidget(self.completedFilesListView)


        self.horizontalLayout.addLayout(self.leftVerticalLayout)

        self.rightVerticalLayout = QVBoxLayout()
        self.rightVerticalLayout.setObjectName(u"rightVerticalLayout")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_5)

        self.sliceSelectionGridLayout = QGridLayout()
        self.sliceSelectionGridLayout.setObjectName(u"sliceSelectionGridLayout")
        self.sliceSelectionSettingsLabel = QLabel(self.centralwidget)
        self.sliceSelectionSettingsLabel.setObjectName(u"sliceSelectionSettingsLabel")

        self.sliceSelectionGridLayout.addWidget(self.sliceSelectionSettingsLabel, 0, 0, 1, 3)

        self.lastSliceLineEdit = QLineEdit(self.centralwidget)
        self.lastSliceLineEdit.setObjectName(u"lastSliceLineEdit")
        self.lastSliceLineEdit.setAlignment(Qt.AlignCenter)

        self.sliceSelectionGridLayout.addWidget(self.lastSliceLineEdit, 1, 4, 1, 1)

        self.firstSliceLabel = QLabel(self.centralwidget)
        self.firstSliceLabel.setObjectName(u"firstSliceLabel")

        self.sliceSelectionGridLayout.addWidget(self.firstSliceLabel, 1, 0, 1, 1)

        self.lastSliceLabel = QLabel(self.centralwidget)
        self.lastSliceLabel.setObjectName(u"lastSliceLabel")

        self.sliceSelectionGridLayout.addWidget(self.lastSliceLabel, 1, 3, 1, 1)

        self.betweennSlicesHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.sliceSelectionGridLayout.addItem(self.betweennSlicesHorizontalSpacer, 1, 2, 1, 1)

        self.firstSliceLineEdit = QLineEdit(self.centralwidget)
        self.firstSliceLineEdit.setObjectName(u"firstSliceLineEdit")
        self.firstSliceLineEdit.setAlignment(Qt.AlignCenter)

        self.sliceSelectionGridLayout.addWidget(self.firstSliceLineEdit, 1, 1, 1, 1)

        self.afterLastSliceHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.sliceSelectionGridLayout.addItem(self.afterLastSliceHorizontalSpacer, 1, 5, 1, 1)


        self.rightVerticalLayout.addLayout(self.sliceSelectionGridLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_2)

        self.denoiseSettingsGridLayout = QGridLayout()
        self.denoiseSettingsGridLayout.setObjectName(u"denoiseSettingsGridLayout")
        self.denoiseSettingsLabel = QLabel(self.centralwidget)
        self.denoiseSettingsLabel.setObjectName(u"denoiseSettingsLabel")

        self.denoiseSettingsGridLayout.addWidget(self.denoiseSettingsLabel, 0, 0, 1, 2)

        self.sharpenLabel = QLabel(self.centralwidget)
        self.sharpenLabel.setObjectName(u"sharpenLabel")
        self.sharpenLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpenLabel, 4, 0, 1, 1)

        self.use3DCheckBox = QCheckBox(self.centralwidget)
        self.use3DCheckBox.setObjectName(u"use3DCheckBox")

        self.denoiseSettingsGridLayout.addWidget(self.use3DCheckBox, 1, 0, 1, 1)

        self.denoisePPELabel = QLabel(self.centralwidget)
        self.denoisePPELabel.setObjectName(u"denoisePPELabel")
        self.denoisePPELabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoisePPELabel, 1, 2, 1, 1)

        self.sigmaPPELineEdit = QLineEdit(self.centralwidget)
        self.sigmaPPELineEdit.setObjectName(u"sigmaPPELineEdit")
        self.sigmaPPELineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigmaPPELineEdit, 3, 2, 1, 1)

        self.sigmaLabel = QLabel(self.centralwidget)
        self.sigmaLabel.setObjectName(u"sigmaLabel")
        self.sigmaLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigmaLabel, 3, 0, 1, 1)

        self.denoise3CRMLabel = QLabel(self.centralwidget)
        self.denoise3CRMLabel.setObjectName(u"denoise3CRMLabel")
        self.denoise3CRMLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoise3CRMLabel, 1, 1, 1, 1)

        self.sharpen3CRMLineEdit = QLineEdit(self.centralwidget)
        self.sharpen3CRMLineEdit.setObjectName(u"sharpen3CRMLineEdit")
        self.sharpen3CRMLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpen3CRMLineEdit, 4, 1, 1, 1)

        self.sigma3CRMLineEdit = QLineEdit(self.centralwidget)
        self.sigma3CRMLineEdit.setObjectName(u"sigma3CRMLineEdit")
        self.sigma3CRMLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigma3CRMLineEdit, 3, 1, 1, 1)

        self.sharpenPPELineEdit = QLineEdit(self.centralwidget)
        self.sharpenPPELineEdit.setObjectName(u"sharpenPPELineEdit")
        self.sharpenPPELineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpenPPELineEdit, 4, 2, 1, 1)

        self.sharpen5CRMLineEdit = QLineEdit(self.centralwidget)
        self.sharpen5CRMLineEdit.setObjectName(u"sharpen5CRMLineEdit")
        self.sharpen5CRMLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpen5CRMLineEdit, 4, 3, 1, 1)

        self.sigma5CRMLineEdit = QLineEdit(self.centralwidget)
        self.sigma5CRMLineEdit.setObjectName(u"sigma5CRMLineEdit")
        self.sigma5CRMLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigma5CRMLineEdit, 3, 3, 1, 1)

        self.denoise5CRMLabel = QLabel(self.centralwidget)
        self.denoise5CRMLabel.setObjectName(u"denoise5CRMLabel")
        self.denoise5CRMLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoise5CRMLabel, 1, 3, 1, 1)


        self.rightVerticalLayout.addLayout(self.denoiseSettingsGridLayout)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_3)

        self.spotDetectionGridLayout = QGridLayout()
        self.spotDetectionGridLayout.setObjectName(u"spotDetectionGridLayout")
        self.spotDetection5CRMLabel = QLabel(self.centralwidget)
        self.spotDetection5CRMLabel.setObjectName(u"spotDetection5CRMLabel")
        self.spotDetection5CRMLabel.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection5CRMLabel, 2, 3, 1, 1)

        self.spotDetectionPPELabel = QLabel(self.centralwidget)
        self.spotDetectionPPELabel.setObjectName(u"spotDetectionPPELabel")
        self.spotDetectionPPELabel.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetectionPPELabel, 2, 2, 1, 1)

        self.spotDetectionSettingsLabel = QLabel(self.centralwidget)
        self.spotDetectionSettingsLabel.setObjectName(u"spotDetectionSettingsLabel")

        self.spotDetectionGridLayout.addWidget(self.spotDetectionSettingsLabel, 0, 0, 1, 2)

        self.spotDetectionPPEThresholdLineEdit = QLineEdit(self.centralwidget)
        self.spotDetectionPPEThresholdLineEdit.setObjectName(u"spotDetectionPPEThresholdLineEdit")
        self.spotDetectionPPEThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetectionPPEThresholdLineEdit, 3, 2, 1, 1)

        self.spotDetection3CRMLabel = QLabel(self.centralwidget)
        self.spotDetection3CRMLabel.setObjectName(u"spotDetection3CRMLabel")
        self.spotDetection3CRMLabel.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection3CRMLabel, 2, 1, 1, 1)

        self.spotDetection3CRMThresholdLineEdit = QLineEdit(self.centralwidget)
        self.spotDetection3CRMThresholdLineEdit.setObjectName(u"spotDetection3CRMThresholdLineEdit")
        self.spotDetection3CRMThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection3CRMThresholdLineEdit, 3, 1, 1, 1)

        self.spotDetection5CRMThresholdLineEdit = QLineEdit(self.centralwidget)
        self.spotDetection5CRMThresholdLineEdit.setObjectName(u"spotDetection5CRMThresholdLineEdit")
        self.spotDetection5CRMThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection5CRMThresholdLineEdit, 3, 3, 1, 1)

        self.spotDetectionThresholdLabel = QLabel(self.centralwidget)
        self.spotDetectionThresholdLabel.setObjectName(u"spotDetectionThresholdLabel")

        self.spotDetectionGridLayout.addWidget(self.spotDetectionThresholdLabel, 3, 0, 1, 1)


        self.rightVerticalLayout.addLayout(self.spotDetectionGridLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer)

        self.touchingSettingsGridLayout = QGridLayout()
        self.touchingSettingsGridLayout.setObjectName(u"touchingSettingsGridLayout")
        self.touchingThresholdLineEdit = QLineEdit(self.centralwidget)
        self.touchingThresholdLineEdit.setObjectName(u"touchingThresholdLineEdit")
        self.touchingThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.touchingSettingsGridLayout.addWidget(self.touchingThresholdLineEdit, 1, 1, 1, 1)

        self.touchingSettingsLabel = QLabel(self.centralwidget)
        self.touchingSettingsLabel.setObjectName(u"touchingSettingsLabel")

        self.touchingSettingsGridLayout.addWidget(self.touchingSettingsLabel, 0, 0, 1, 2)

        self.ltouchingThresholdLabel = QLabel(self.centralwidget)
        self.ltouchingThresholdLabel.setObjectName(u"ltouchingThresholdLabel")

        self.touchingSettingsGridLayout.addWidget(self.ltouchingThresholdLabel, 1, 0, 1, 1)

        self.touchingThresholdHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.touchingSettingsGridLayout.addItem(self.touchingThresholdHorizontalSpacer, 1, 2, 1, 1)


        self.rightVerticalLayout.addLayout(self.touchingSettingsGridLayout)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_4)

        self.controlButtonHorizontalLayout = QHBoxLayout()
        self.controlButtonHorizontalLayout.setObjectName(u"controlButtonHorizontalLayout")
        self.controlButtonsHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.controlButtonHorizontalLayout.addItem(self.controlButtonsHorizontalSpacer)

        self.testSettingsPushButton = QPushButton(self.centralwidget)
        self.testSettingsPushButton.setObjectName(u"testSettingsPushButton")

        self.controlButtonHorizontalLayout.addWidget(self.testSettingsPushButton)

        self.runBatchPushButton = QPushButton(self.centralwidget)
        self.runBatchPushButton.setObjectName(u"runBatchPushButton")

        self.controlButtonHorizontalLayout.addWidget(self.runBatchPushButton)

        self.quitPushButton = QPushButton(self.centralwidget)
        self.quitPushButton.setObjectName(u"quitPushButton")

        self.controlButtonHorizontalLayout.addWidget(self.quitPushButton)


        self.rightVerticalLayout.addLayout(self.controlButtonHorizontalLayout)


        self.horizontalLayout.addLayout(self.rightVerticalLayout)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1147, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.addFilesButton, self.pendingFilesListView)
        QWidget.setTabOrder(self.pendingFilesListView, self.completedFilesListView)
        QWidget.setTabOrder(self.completedFilesListView, self.firstSliceLineEdit)
        QWidget.setTabOrder(self.firstSliceLineEdit, self.lastSliceLineEdit)
        QWidget.setTabOrder(self.lastSliceLineEdit, self.use3DCheckBox)
        QWidget.setTabOrder(self.use3DCheckBox, self.sigma3CRMLineEdit)
        QWidget.setTabOrder(self.sigma3CRMLineEdit, self.sharpen3CRMLineEdit)
        QWidget.setTabOrder(self.sharpen3CRMLineEdit, self.sigmaPPELineEdit)
        QWidget.setTabOrder(self.sigmaPPELineEdit, self.sharpenPPELineEdit)
        QWidget.setTabOrder(self.sharpenPPELineEdit, self.sigma5CRMLineEdit)
        QWidget.setTabOrder(self.sigma5CRMLineEdit, self.sharpen5CRMLineEdit)
        QWidget.setTabOrder(self.sharpen5CRMLineEdit, self.spotDetection3CRMThresholdLineEdit)
        QWidget.setTabOrder(self.spotDetection3CRMThresholdLineEdit, self.spotDetectionPPEThresholdLineEdit)
        QWidget.setTabOrder(self.spotDetectionPPEThresholdLineEdit, self.spotDetection5CRMThresholdLineEdit)
        QWidget.setTabOrder(self.spotDetection5CRMThresholdLineEdit, self.touchingThresholdLineEdit)
        QWidget.setTabOrder(self.touchingThresholdLineEdit, self.testSettingsPushButton)
        QWidget.setTabOrder(self.testSettingsPushButton, self.runBatchPushButton)
        QWidget.setTabOrder(self.runBatchPushButton, self.quitPushButton)
        QWidget.setTabOrder(self.quitPushButton, self.clearCompletedFilesPushButton)
        QWidget.setTabOrder(self.clearCompletedFilesPushButton, self.activeFileLineEdit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pendingFilesLabel.setText(QCoreApplication.translate("MainWindow", u"Pending Files:", None))
        self.addFilesButton.setText(QCoreApplication.translate("MainWindow", u"Add File(s)", None))
        self.activeFileLabel.setText(QCoreApplication.translate("MainWindow", u"Being Processed:", None))
        self.progressBarLabel.setText(QCoreApplication.translate("MainWindow", u"Progress: ", None))
        self.completedFilesLabel.setText(QCoreApplication.translate("MainWindow", u"Completed Files:", None))
        self.clearCompletedFilesPushButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.sliceSelectionSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Slice Selection Settings", None))
        self.firstSliceLabel.setText(QCoreApplication.translate("MainWindow", u"First Slice:", None))
        self.lastSliceLabel.setText(QCoreApplication.translate("MainWindow", u"Last Slice:", None))
        self.denoiseSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Denoising Settings", None))
        self.sharpenLabel.setText(QCoreApplication.translate("MainWindow", u"Sharpening:", None))
        self.use3DCheckBox.setText(QCoreApplication.translate("MainWindow", u"Use 3D Denoising", None))
        self.denoisePPELabel.setText(QCoreApplication.translate("MainWindow", u"PPE", None))
        self.sigmaLabel.setText(QCoreApplication.translate("MainWindow", u"Sigma:", None))
        self.denoise3CRMLabel.setText(QCoreApplication.translate("MainWindow", u"3'CRM", None))
        self.denoise5CRMLabel.setText(QCoreApplication.translate("MainWindow", u"5'CRM", None))
        self.spotDetection5CRMLabel.setText(QCoreApplication.translate("MainWindow", u"5'CRM", None))
        self.spotDetectionPPELabel.setText(QCoreApplication.translate("MainWindow", u"PPE", None))
        self.spotDetectionSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Spot Detection Settings", None))
        self.spotDetection3CRMLabel.setText(QCoreApplication.translate("MainWindow", u"3'CRM", None))
        self.spotDetectionThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Threshold:", None))
        self.touchingSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Touching Settings", None))
        self.ltouchingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Threshold:", None))
        self.testSettingsPushButton.setText(QCoreApplication.translate("MainWindow", u"Test Settings", None))
        self.runBatchPushButton.setText(QCoreApplication.translate("MainWindow", u"Run Batch", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
    # retranslateUi

