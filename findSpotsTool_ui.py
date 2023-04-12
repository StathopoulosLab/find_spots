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
        MainWindow.resize(1147, 749)
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

        self.stepNameHorizontalLayout = QHBoxLayout()
        self.stepNameHorizontalLayout.setObjectName(u"stepNameHorizontalLayout")
        self.stepNameLabel = QLabel(self.centralwidget)
        self.stepNameLabel.setObjectName(u"stepNameLabel")

        self.stepNameHorizontalLayout.addWidget(self.stepNameLabel)

        self.stepNameLineEdit = QLineEdit(self.centralwidget)
        self.stepNameLineEdit.setObjectName(u"stepNameLineEdit")

        self.stepNameHorizontalLayout.addWidget(self.stepNameLineEdit)


        self.leftVerticalLayout.addLayout(self.stepNameHorizontalLayout)

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
        self.verticalSpacer_5 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

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

        self.verticalSpacer_2 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_2)

        self.denoiseSettingsGridLayout = QGridLayout()
        self.denoiseSettingsGridLayout.setObjectName(u"denoiseSettingsGridLayout")
        self.denoise555Label = QLabel(self.centralwidget)
        self.denoise555Label.setObjectName(u"denoise555Label")
        self.denoise555Label.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoise555Label, 1, 2, 1, 1)

        self.sigma488LineEdit = QLineEdit(self.centralwidget)
        self.sigma488LineEdit.setObjectName(u"sigma488LineEdit")
        self.sigma488LineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigma488LineEdit, 3, 3, 1, 1)

        self.use3DCheckBox = QCheckBox(self.centralwidget)
        self.use3DCheckBox.setObjectName(u"use3DCheckBox")

        self.denoiseSettingsGridLayout.addWidget(self.use3DCheckBox, 1, 0, 1, 1)

        self.denoise647Label = QLabel(self.centralwidget)
        self.denoise647Label.setObjectName(u"denoise647Label")
        self.denoise647Label.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoise647Label, 1, 1, 1, 1)

        self.sharpenLabel = QLabel(self.centralwidget)
        self.sharpenLabel.setObjectName(u"sharpenLabel")
        self.sharpenLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpenLabel, 4, 0, 1, 1)

        self.sharpen555LineEdit = QLineEdit(self.centralwidget)
        self.sharpen555LineEdit.setObjectName(u"sharpen555LineEdit")
        self.sharpen555LineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpen555LineEdit, 4, 2, 1, 1)

        self.sigma555LineEdit = QLineEdit(self.centralwidget)
        self.sigma555LineEdit.setObjectName(u"sigma555LineEdit")
        self.sigma555LineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigma555LineEdit, 3, 2, 1, 1)

        self.sigma647LineEdit = QLineEdit(self.centralwidget)
        self.sigma647LineEdit.setObjectName(u"sigma647LineEdit")
        self.sigma647LineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigma647LineEdit, 3, 1, 1, 1)

        self.sigmaLabel = QLabel(self.centralwidget)
        self.sigmaLabel.setObjectName(u"sigmaLabel")
        self.sigmaLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigmaLabel, 3, 0, 1, 1)

        self.sharpen647LineEdit = QLineEdit(self.centralwidget)
        self.sharpen647LineEdit.setObjectName(u"sharpen647LineEdit")
        self.sharpen647LineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpen647LineEdit, 4, 1, 1, 1)

        self.sharpen488LineEdit = QLineEdit(self.centralwidget)
        self.sharpen488LineEdit.setObjectName(u"sharpen488LineEdit")
        self.sharpen488LineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpen488LineEdit, 4, 3, 1, 1)

        self.denoiseSettingsLabel = QLabel(self.centralwidget)
        self.denoiseSettingsLabel.setObjectName(u"denoiseSettingsLabel")

        self.denoiseSettingsGridLayout.addWidget(self.denoiseSettingsLabel, 0, 0, 1, 2)

        self.denoise488Label = QLabel(self.centralwidget)
        self.denoise488Label.setObjectName(u"denoise488Label")
        self.denoise488Label.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoise488Label, 1, 3, 1, 1)

        self.denoiseNucleusLabel = QLabel(self.centralwidget)
        self.denoiseNucleusLabel.setObjectName(u"denoiseNucleusLabel")
        self.denoiseNucleusLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoiseNucleusLabel, 1, 4, 1, 1)

        self.sigmaNucleusLineEdit = QLineEdit(self.centralwidget)
        self.sigmaNucleusLineEdit.setObjectName(u"sigmaNucleusLineEdit")
        self.sigmaNucleusLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigmaNucleusLineEdit, 3, 4, 1, 1)

        self.sharpenNucleusLineEdit = QLineEdit(self.centralwidget)
        self.sharpenNucleusLineEdit.setObjectName(u"sharpenNucleusLineEdit")
        self.sharpenNucleusLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpenNucleusLineEdit, 4, 4, 1, 1)


        self.rightVerticalLayout.addLayout(self.denoiseSettingsGridLayout)

        self.verticalSpacer_6 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_6)

        self.nucleusMaskingGridLayout = QGridLayout()
        self.nucleusMaskingGridLayout.setObjectName(u"nucleusMaskingGridLayout")
        self.nucleusMaskingThresholdLineEdit = QLineEdit(self.centralwidget)
        self.nucleusMaskingThresholdLineEdit.setObjectName(u"nucleusMaskingThresholdLineEdit")
        self.nucleusMaskingThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.nucleusMaskingGridLayout.addWidget(self.nucleusMaskingThresholdLineEdit, 1, 1, 1, 1)

        self.nucleusMaskingThresholdLabel = QLabel(self.centralwidget)
        self.nucleusMaskingThresholdLabel.setObjectName(u"nucleusMaskingThresholdLabel")
        self.nucleusMaskingThresholdLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.nucleusMaskingGridLayout.addWidget(self.nucleusMaskingThresholdLabel, 1, 0, 1, 1)

        self.nucleusMaskingLabel = QLabel(self.centralwidget)
        self.nucleusMaskingLabel.setObjectName(u"nucleusMaskingLabel")

        self.nucleusMaskingGridLayout.addWidget(self.nucleusMaskingLabel, 0, 0, 1, 1)

        self.nucleusMaskingHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.nucleusMaskingGridLayout.addItem(self.nucleusMaskingHorizontalSpacer, 1, 2, 1, 1)


        self.rightVerticalLayout.addLayout(self.nucleusMaskingGridLayout)

        self.verticalSpacer_3 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_3)

        self.spotDetectionGridLayout = QGridLayout()
        self.spotDetectionGridLayout.setObjectName(u"spotDetectionGridLayout")
        self.spotDetection488Label = QLabel(self.centralwidget)
        self.spotDetection488Label.setObjectName(u"spotDetection488Label")
        self.spotDetection488Label.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection488Label, 2, 3, 1, 1)

        self.spotDetection647ThresholdLineEdit = QLineEdit(self.centralwidget)
        self.spotDetection647ThresholdLineEdit.setObjectName(u"spotDetection647ThresholdLineEdit")
        self.spotDetection647ThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection647ThresholdLineEdit, 3, 1, 1, 1)

        self.spotDetection555Label = QLabel(self.centralwidget)
        self.spotDetection555Label.setObjectName(u"spotDetection555Label")
        self.spotDetection555Label.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection555Label, 2, 2, 1, 1)

        self.spotDetection488ThresholdLineEdit = QLineEdit(self.centralwidget)
        self.spotDetection488ThresholdLineEdit.setObjectName(u"spotDetection488ThresholdLineEdit")
        self.spotDetection488ThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection488ThresholdLineEdit, 3, 3, 1, 1)

        self.spotDetectionSettingsLabel = QLabel(self.centralwidget)
        self.spotDetectionSettingsLabel.setObjectName(u"spotDetectionSettingsLabel")

        self.spotDetectionGridLayout.addWidget(self.spotDetectionSettingsLabel, 0, 0, 1, 2)

        self.spotDetectionThresholdLabel = QLabel(self.centralwidget)
        self.spotDetectionThresholdLabel.setObjectName(u"spotDetectionThresholdLabel")

        self.spotDetectionGridLayout.addWidget(self.spotDetectionThresholdLabel, 3, 0, 1, 1)

        self.spotDetection555ThresholdLineEdit = QLineEdit(self.centralwidget)
        self.spotDetection555ThresholdLineEdit.setObjectName(u"spotDetection555ThresholdLineEdit")
        self.spotDetection555ThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection555ThresholdLineEdit, 3, 2, 1, 1)

        self.spotDetection647Label = QLabel(self.centralwidget)
        self.spotDetection647Label.setObjectName(u"spotDetection647Label")
        self.spotDetection647Label.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.spotDetection647Label, 2, 1, 1, 1)


        self.rightVerticalLayout.addLayout(self.spotDetectionGridLayout)

        self.verticalSpacer_8 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_8)

        self.tripletSettingsGridLayout = QGridLayout()
        self.tripletSettingsGridLayout.setObjectName(u"tripletSettingsGridLayout")
        self.tripletMaxSizeHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.tripletSettingsGridLayout.addItem(self.tripletMaxSizeHorizontalSpacer, 2, 2, 1, 1)

        self.tripletMaxSizeLabel = QLabel(self.centralwidget)
        self.tripletMaxSizeLabel.setObjectName(u"tripletMaxSizeLabel")
        self.tripletMaxSizeLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.tripletSettingsGridLayout.addWidget(self.tripletMaxSizeLabel, 2, 0, 1, 1)

        self.tripletMaxSizeLineEdit = QLineEdit(self.centralwidget)
        self.tripletMaxSizeLineEdit.setObjectName(u"tripletMaxSizeLineEdit")
        self.tripletMaxSizeLineEdit.setAlignment(Qt.AlignCenter)

        self.tripletSettingsGridLayout.addWidget(self.tripletMaxSizeLineEdit, 2, 1, 1, 1)

        self.tripletSettingsLabelabel = QLabel(self.centralwidget)
        self.tripletSettingsLabelabel.setObjectName(u"tripletSettingsLabelabel")

        self.tripletSettingsGridLayout.addWidget(self.tripletSettingsLabelabel, 1, 0, 1, 2)


        self.rightVerticalLayout.addLayout(self.tripletSettingsGridLayout)

        self.verticalSpacer = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

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

        self.touchingThresholdLabel = QLabel(self.centralwidget)
        self.touchingThresholdLabel.setObjectName(u"touchingThresholdLabel")

        self.touchingSettingsGridLayout.addWidget(self.touchingThresholdLabel, 1, 0, 1, 1)

        self.touchingThresholdHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.touchingSettingsGridLayout.addItem(self.touchingThresholdHorizontalSpacer, 1, 2, 1, 1)


        self.rightVerticalLayout.addLayout(self.touchingSettingsGridLayout)

        self.verticalSpacer_4 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_4)

        self.spotProjectionGridLayout = QGridLayout()
        self.spotProjectionGridLayout.setObjectName(u"spotProjectionGridLayout")
        self.spotProjectionSettingsLabel = QLabel(self.centralwidget)
        self.spotProjectionSettingsLabel.setObjectName(u"spotProjectionSettingsLabel")

        self.spotProjectionGridLayout.addWidget(self.spotProjectionSettingsLabel, 0, 0, 1, 1)

        self.spotProjectionsSliceLabel = QLabel(self.centralwidget)
        self.spotProjectionsSliceLabel.setObjectName(u"spotProjectionsSliceLabel")

        self.spotProjectionGridLayout.addWidget(self.spotProjectionsSliceLabel, 1, 0, 1, 1, Qt.AlignRight)

        self.spotProjectionSliceLineEdit = QLineEdit(self.centralwidget)
        self.spotProjectionSliceLineEdit.setObjectName(u"spotProjectionSliceLineEdit")
        self.spotProjectionSliceLineEdit.setAlignment(Qt.AlignCenter)

        self.spotProjectionGridLayout.addWidget(self.spotProjectionSliceLineEdit, 1, 1, 1, 1)

        self.spotProjectionHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.spotProjectionGridLayout.addItem(self.spotProjectionHorizontalSpacer, 1, 2, 1, 1)


        self.rightVerticalLayout.addLayout(self.spotProjectionGridLayout)

        self.verticalSpacer_7 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_7)

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
        QWidget.setTabOrder(self.use3DCheckBox, self.sigma647LineEdit)
        QWidget.setTabOrder(self.sigma647LineEdit, self.sharpen647LineEdit)
        QWidget.setTabOrder(self.sharpen647LineEdit, self.sigma555LineEdit)
        QWidget.setTabOrder(self.sigma555LineEdit, self.sharpen555LineEdit)
        QWidget.setTabOrder(self.sharpen555LineEdit, self.sigma488LineEdit)
        QWidget.setTabOrder(self.sigma488LineEdit, self.sharpen488LineEdit)
        QWidget.setTabOrder(self.sharpen488LineEdit, self.spotDetection647ThresholdLineEdit)
        QWidget.setTabOrder(self.spotDetection647ThresholdLineEdit, self.spotDetection555ThresholdLineEdit)
        QWidget.setTabOrder(self.spotDetection555ThresholdLineEdit, self.spotDetection488ThresholdLineEdit)
        QWidget.setTabOrder(self.spotDetection488ThresholdLineEdit, self.touchingThresholdLineEdit)
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
        self.stepNameLabel.setText(QCoreApplication.translate("MainWindow", u"On step:", None))
        self.completedFilesLabel.setText(QCoreApplication.translate("MainWindow", u"Completed Files:", None))
        self.clearCompletedFilesPushButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.sliceSelectionSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Slice Selection Settings", None))
        self.firstSliceLabel.setText(QCoreApplication.translate("MainWindow", u"First Slice:", None))
        self.lastSliceLabel.setText(QCoreApplication.translate("MainWindow", u"Last Slice:", None))
        self.denoise555Label.setText(QCoreApplication.translate("MainWindow", u"555", None))
        self.use3DCheckBox.setText(QCoreApplication.translate("MainWindow", u"Use 3D Denoising", None))
        self.denoise647Label.setText(QCoreApplication.translate("MainWindow", u"647", None))
        self.sharpenLabel.setText(QCoreApplication.translate("MainWindow", u"Sharpening:", None))
        self.sigmaLabel.setText(QCoreApplication.translate("MainWindow", u"Sigma:", None))
        self.denoiseSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Denoising Settings", None))
        self.denoise488Label.setText(QCoreApplication.translate("MainWindow", u"488", None))
        self.denoiseNucleusLabel.setText(QCoreApplication.translate("MainWindow", u"Nucleus", None))
        self.nucleusMaskingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Masking Threshold: ", None))
        self.nucleusMaskingLabel.setText(QCoreApplication.translate("MainWindow", u"Nucleus Masking Settings", None))
        self.spotDetection488Label.setText(QCoreApplication.translate("MainWindow", u"488", None))
        self.spotDetection555Label.setText(QCoreApplication.translate("MainWindow", u"555", None))
        self.spotDetectionSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Spot Detection Settings", None))
        self.spotDetectionThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Threshold:", None))
        self.spotDetection647Label.setText(QCoreApplication.translate("MainWindow", u"647", None))
        self.tripletMaxSizeLabel.setText(QCoreApplication.translate("MainWindow", u"Max Size: ", None))
        self.tripletSettingsLabelabel.setText(QCoreApplication.translate("MainWindow", u"Triplet Detection Settings", None))
        self.touchingSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Touching Settings", None))
        self.touchingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Threshold:", None))
        self.spotProjectionSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Spot Projection Settings", None))
        self.spotProjectionsSliceLabel.setText(QCoreApplication.translate("MainWindow", u"Nucleus Slice for Spot Display:", None))
        self.testSettingsPushButton.setText(QCoreApplication.translate("MainWindow", u"Test Settings", None))
        self.runBatchPushButton.setText(QCoreApplication.translate("MainWindow", u"Run Batch", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
    # retranslateUi

