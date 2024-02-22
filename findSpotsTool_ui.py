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
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QListView,
    QMainWindow, QMenuBar, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1158, 867)
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
        self.sliceSelectionGridLayout = QGridLayout()
        self.sliceSelectionGridLayout.setObjectName(u"sliceSelectionGridLayout")
        self.lastSliceLineEdit = QLineEdit(self.centralwidget)
        self.lastSliceLineEdit.setObjectName(u"lastSliceLineEdit")
        self.lastSliceLineEdit.setAlignment(Qt.AlignCenter)

        self.sliceSelectionGridLayout.addWidget(self.lastSliceLineEdit, 1, 4, 1, 1)

        self.sliceSelectionSettingsLabel = QLabel(self.centralwidget)
        self.sliceSelectionSettingsLabel.setObjectName(u"sliceSelectionSettingsLabel")

        self.sliceSelectionGridLayout.addWidget(self.sliceSelectionSettingsLabel, 0, 0, 1, 3)

        self.lastSliceLabel = QLabel(self.centralwidget)
        self.lastSliceLabel.setObjectName(u"lastSliceLabel")

        self.sliceSelectionGridLayout.addWidget(self.lastSliceLabel, 1, 3, 1, 1)

        self.firstSliceLabel = QLabel(self.centralwidget)
        self.firstSliceLabel.setObjectName(u"firstSliceLabel")

        self.sliceSelectionGridLayout.addWidget(self.firstSliceLabel, 1, 0, 1, 1)

        self.firstSliceLineEdit = QLineEdit(self.centralwidget)
        self.firstSliceLineEdit.setObjectName(u"firstSliceLineEdit")
        self.firstSliceLineEdit.setAlignment(Qt.AlignCenter)

        self.sliceSelectionGridLayout.addWidget(self.firstSliceLineEdit, 1, 1, 1, 1)

        self.afterLastSliceHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.sliceSelectionGridLayout.addItem(self.afterLastSliceHorizontalSpacer, 1, 5, 1, 1)

        self.betweennSlicesHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.sliceSelectionGridLayout.addItem(self.betweennSlicesHorizontalSpacer, 1, 2, 1, 1)

        self.nucleusSliceLabel = QLabel(self.centralwidget)
        self.nucleusSliceLabel.setObjectName(u"nucleusSliceLabel")

        self.sliceSelectionGridLayout.addWidget(self.nucleusSliceLabel, 2, 0, 1, 1)

        self.nucleusSliceLineEdit = QLineEdit(self.centralwidget)
        self.nucleusSliceLineEdit.setObjectName(u"nucleusSliceLineEdit")
        self.nucleusSliceLineEdit.setAlignment(Qt.AlignCenter)

        self.sliceSelectionGridLayout.addWidget(self.nucleusSliceLineEdit, 2, 1, 1, 1)


        self.rightVerticalLayout.addLayout(self.sliceSelectionGridLayout)

        self.verticalSpacer_1 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_1)

        self.channelsGridLayout = QGridLayout()
        self.channelsGridLayout.setObjectName(u"channelsGridLayout")
        self.leftChannelComboBox = QComboBox(self.centralwidget)
        self.leftChannelComboBox.setObjectName(u"leftChannelComboBox")

        self.channelsGridLayout.addWidget(self.leftChannelComboBox, 3, 0, 1, 1)

        self.channelsLabel = QLabel(self.centralwidget)
        self.channelsLabel.setObjectName(u"channelsLabel")
        self.channelsLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.channelsGridLayout.addWidget(self.channelsLabel, 1, 0, 1, 1)

        self.middleChannelLabel = QLabel(self.centralwidget)
        self.middleChannelLabel.setObjectName(u"middleChannelLabel")
        self.middleChannelLabel.setAlignment(Qt.AlignCenter)

        self.channelsGridLayout.addWidget(self.middleChannelLabel, 2, 1, 1, 1)

        self.leftChannelLabel = QLabel(self.centralwidget)
        self.leftChannelLabel.setObjectName(u"leftChannelLabel")
        self.leftChannelLabel.setAlignment(Qt.AlignCenter)

        self.channelsGridLayout.addWidget(self.leftChannelLabel, 2, 0, 1, 1)

        self.rightChannelLabel = QLabel(self.centralwidget)
        self.rightChannelLabel.setObjectName(u"rightChannelLabel")
        self.rightChannelLabel.setAlignment(Qt.AlignCenter)

        self.channelsGridLayout.addWidget(self.rightChannelLabel, 2, 2, 1, 1)

        self.rightChannelComboBox = QComboBox(self.centralwidget)
        self.rightChannelComboBox.setObjectName(u"rightChannelComboBox")

        self.channelsGridLayout.addWidget(self.rightChannelComboBox, 3, 2, 1, 1)

        self.middleChannelComboBox = QComboBox(self.centralwidget)
        self.middleChannelComboBox.setObjectName(u"middleChannelComboBox")

        self.channelsGridLayout.addWidget(self.middleChannelComboBox, 3, 1, 1, 1)


        self.rightVerticalLayout.addLayout(self.channelsGridLayout)

        self.verticalSpacer_2 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_2)

        self.denoiseSettingsGridLayout = QGridLayout()
        self.denoiseSettingsGridLayout.setObjectName(u"denoiseSettingsGridLayout")
        self.rightSigmaLineEdit = QLineEdit(self.centralwidget)
        self.rightSigmaLineEdit.setObjectName(u"rightSigmaLineEdit")
        self.rightSigmaLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.rightSigmaLineEdit, 3, 3, 1, 1)

        self.sharpenNucleusLineEdit = QLineEdit(self.centralwidget)
        self.sharpenNucleusLineEdit.setObjectName(u"sharpenNucleusLineEdit")
        self.sharpenNucleusLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpenNucleusLineEdit, 4, 4, 1, 1)

        self.saveDetectedSpotsCheckBox = QCheckBox(self.centralwidget)
        self.saveDetectedSpotsCheckBox.setObjectName(u"saveDetectedSpotsCheckBox")

        self.denoiseSettingsGridLayout.addWidget(self.saveDetectedSpotsCheckBox, 5, 0, 1, 1)

        self.rightDenoiseLabel = QLabel(self.centralwidget)
        self.rightDenoiseLabel.setObjectName(u"rightDenoiseLabel")
        self.rightDenoiseLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.rightDenoiseLabel, 1, 3, 1, 1)

        self.leftSigmaLineEdit = QLineEdit(self.centralwidget)
        self.leftSigmaLineEdit.setObjectName(u"leftSigmaLineEdit")
        self.leftSigmaLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.leftSigmaLineEdit, 3, 1, 1, 1)

        self.rightSharpenLineEdit = QLineEdit(self.centralwidget)
        self.rightSharpenLineEdit.setObjectName(u"rightSharpenLineEdit")
        self.rightSharpenLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.rightSharpenLineEdit, 4, 3, 1, 1)

        self.sigmaLabel = QLabel(self.centralwidget)
        self.sigmaLabel.setObjectName(u"sigmaLabel")
        self.sigmaLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigmaLabel, 3, 0, 1, 1)

        self.denoiseCheckBox = QCheckBox(self.centralwidget)
        self.denoiseCheckBox.setObjectName(u"denoiseCheckBox")

        self.denoiseSettingsGridLayout.addWidget(self.denoiseCheckBox, 0, 0, 1, 1)

        self.sharpenLabel = QLabel(self.centralwidget)
        self.sharpenLabel.setObjectName(u"sharpenLabel")
        self.sharpenLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sharpenLabel, 4, 0, 1, 1)

        self.leftDenoiseLabel = QLabel(self.centralwidget)
        self.leftDenoiseLabel.setObjectName(u"leftDenoiseLabel")
        self.leftDenoiseLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.leftDenoiseLabel, 1, 1, 1, 1)

        self.leftSharpenLineEdit = QLineEdit(self.centralwidget)
        self.leftSharpenLineEdit.setObjectName(u"leftSharpenLineEdit")
        self.leftSharpenLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.leftSharpenLineEdit, 4, 1, 1, 1)

        self.use3DCheckBox = QCheckBox(self.centralwidget)
        self.use3DCheckBox.setObjectName(u"use3DCheckBox")

        self.denoiseSettingsGridLayout.addWidget(self.use3DCheckBox, 1, 0, 1, 1)

        self.denoiseNucleusLabel = QLabel(self.centralwidget)
        self.denoiseNucleusLabel.setObjectName(u"denoiseNucleusLabel")
        self.denoiseNucleusLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.denoiseNucleusLabel, 1, 4, 1, 1)

        self.middleSigmaLineEdit = QLineEdit(self.centralwidget)
        self.middleSigmaLineEdit.setObjectName(u"middleSigmaLineEdit")
        self.middleSigmaLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.middleSigmaLineEdit, 3, 2, 1, 1)

        self.middleDenoiseLabel = QLabel(self.centralwidget)
        self.middleDenoiseLabel.setObjectName(u"middleDenoiseLabel")
        self.middleDenoiseLabel.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.middleDenoiseLabel, 1, 2, 1, 1)

        self.middleSharpenLineEdit = QLineEdit(self.centralwidget)
        self.middleSharpenLineEdit.setObjectName(u"middleSharpenLineEdit")
        self.middleSharpenLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.middleSharpenLineEdit, 4, 2, 1, 1)

        self.sigmaNucleusLineEdit = QLineEdit(self.centralwidget)
        self.sigmaNucleusLineEdit.setObjectName(u"sigmaNucleusLineEdit")
        self.sigmaNucleusLineEdit.setAlignment(Qt.AlignCenter)

        self.denoiseSettingsGridLayout.addWidget(self.sigmaNucleusLineEdit, 3, 4, 1, 1)


        self.rightVerticalLayout.addLayout(self.denoiseSettingsGridLayout)

        self.verticalSpacer_3 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_3)

        self.nucleusMaskingGridLayout = QGridLayout()
        self.nucleusMaskingGridLayout.setObjectName(u"nucleusMaskingGridLayout")
        self.nucleusMaskingHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.nucleusMaskingGridLayout.addItem(self.nucleusMaskingHorizontalSpacer, 1, 2, 1, 1)

        self.nucleusMaskingThresholdLineEdit = QLineEdit(self.centralwidget)
        self.nucleusMaskingThresholdLineEdit.setObjectName(u"nucleusMaskingThresholdLineEdit")
        self.nucleusMaskingThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.nucleusMaskingGridLayout.addWidget(self.nucleusMaskingThresholdLineEdit, 1, 1, 1, 1)

        self.nucleusMaskingThresholdLabel = QLabel(self.centralwidget)
        self.nucleusMaskingThresholdLabel.setObjectName(u"nucleusMaskingThresholdLabel")
        self.nucleusMaskingThresholdLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.nucleusMaskingGridLayout.addWidget(self.nucleusMaskingThresholdLabel, 1, 0, 1, 1)

        self.maskingCheckBox = QCheckBox(self.centralwidget)
        self.maskingCheckBox.setObjectName(u"maskingCheckBox")

        self.nucleusMaskingGridLayout.addWidget(self.maskingCheckBox, 0, 0, 1, 1)

        self.countNucleiCheckBox = QCheckBox(self.centralwidget)
        self.countNucleiCheckBox.setObjectName(u"countNucleiCheckBox")

        self.nucleusMaskingGridLayout.addWidget(self.countNucleiCheckBox, 0, 1, 1, 1)


        self.rightVerticalLayout.addLayout(self.nucleusMaskingGridLayout)

        self.verticalSpacer_4 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_4)

        self.spotDetectionGridLayout = QGridLayout()
        self.spotDetectionGridLayout.setObjectName(u"spotDetectionGridLayout")
        self.rightSpotDetectionLabel = QLabel(self.centralwidget)
        self.rightSpotDetectionLabel.setObjectName(u"rightSpotDetectionLabel")
        self.rightSpotDetectionLabel.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.rightSpotDetectionLabel, 2, 3, 1, 1)

        self.leftSpotDetectionThresholdLineEdit = QLineEdit(self.centralwidget)
        self.leftSpotDetectionThresholdLineEdit.setObjectName(u"leftSpotDetectionThresholdLineEdit")
        self.leftSpotDetectionThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.leftSpotDetectionThresholdLineEdit, 3, 1, 1, 1)

        self.middleSpotDetection555Label = QLabel(self.centralwidget)
        self.middleSpotDetection555Label.setObjectName(u"middleSpotDetection555Label")
        self.middleSpotDetection555Label.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.middleSpotDetection555Label, 2, 2, 1, 1)

        self.rightSpotDetectionThresholdLineEdit = QLineEdit(self.centralwidget)
        self.rightSpotDetectionThresholdLineEdit.setObjectName(u"rightSpotDetectionThresholdLineEdit")
        self.rightSpotDetectionThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.rightSpotDetectionThresholdLineEdit, 3, 3, 1, 1)

        self.spotDetectionSettingsLabel = QLabel(self.centralwidget)
        self.spotDetectionSettingsLabel.setObjectName(u"spotDetectionSettingsLabel")

        self.spotDetectionGridLayout.addWidget(self.spotDetectionSettingsLabel, 0, 0, 1, 2)

        self.spotDetectionThresholdLabel = QLabel(self.centralwidget)
        self.spotDetectionThresholdLabel.setObjectName(u"spotDetectionThresholdLabel")

        self.spotDetectionGridLayout.addWidget(self.spotDetectionThresholdLabel, 3, 0, 1, 1)

        self.middleSpotDetectionThresholdLineEdit = QLineEdit(self.centralwidget)
        self.middleSpotDetectionThresholdLineEdit.setObjectName(u"middleSpotDetectionThresholdLineEdit")
        self.middleSpotDetectionThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.middleSpotDetectionThresholdLineEdit, 3, 2, 1, 1)

        self.leftSpotDetectionLabel = QLabel(self.centralwidget)
        self.leftSpotDetectionLabel.setObjectName(u"leftSpotDetectionLabel")
        self.leftSpotDetectionLabel.setAlignment(Qt.AlignCenter)

        self.spotDetectionGridLayout.addWidget(self.leftSpotDetectionLabel, 2, 1, 1, 1)


        self.rightVerticalLayout.addLayout(self.spotDetectionGridLayout)

        self.verticalSpacer_5 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_5)

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

        self.findDoubletsCheckBox = QCheckBox(self.centralwidget)
        self.findDoubletsCheckBox.setObjectName(u"findDoubletsCheckBox")

        self.tripletSettingsGridLayout.addWidget(self.findDoubletsCheckBox, 1, 2, 1, 1)


        self.rightVerticalLayout.addLayout(self.tripletSettingsGridLayout)

        self.verticalSpacer_6 = QSpacerItem(366, 13, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.rightVerticalLayout.addItem(self.verticalSpacer_6)

        self.touchingSettingsGridLayout = QGridLayout()
        self.touchingSettingsGridLayout.setObjectName(u"touchingSettingsGridLayout")
        self.touchingSettingsLabel = QLabel(self.centralwidget)
        self.touchingSettingsLabel.setObjectName(u"touchingSettingsLabel")

        self.touchingSettingsGridLayout.addWidget(self.touchingSettingsLabel, 0, 0, 1, 2)

        self.xTouchingThresholdLineEdit = QLineEdit(self.centralwidget)
        self.xTouchingThresholdLineEdit.setObjectName(u"xTouchingThresholdLineEdit")
        self.xTouchingThresholdLineEdit.setAlignment(Qt.AlignCenter)

        self.touchingSettingsGridLayout.addWidget(self.xTouchingThresholdLineEdit, 2, 1, 1, 1)

        self.xTouchingThresholdLabel = QLabel(self.centralwidget)
        self.xTouchingThresholdLabel.setObjectName(u"xTouchingThresholdLabel")
        self.xTouchingThresholdLabel.setAlignment(Qt.AlignCenter)

        self.touchingSettingsGridLayout.addWidget(self.xTouchingThresholdLabel, 1, 1, 1, 1)

        self.zTouchingThresholdLabel = QLabel(self.centralwidget)
        self.zTouchingThresholdLabel.setObjectName(u"zTouchingThresholdLabel")
        self.zTouchingThresholdLabel.setAlignment(Qt.AlignCenter)

        self.touchingSettingsGridLayout.addWidget(self.zTouchingThresholdLabel, 1, 3, 1, 1)

        self.touchingThresholdLabel = QLabel(self.centralwidget)
        self.touchingThresholdLabel.setObjectName(u"touchingThresholdLabel")

        self.touchingSettingsGridLayout.addWidget(self.touchingThresholdLabel, 2, 0, 1, 1)

        self.yTouchingThresholdLabel = QLabel(self.centralwidget)
        self.yTouchingThresholdLabel.setObjectName(u"yTouchingThresholdLabel")
        self.yTouchingThresholdLabel.setAlignment(Qt.AlignCenter)

        self.touchingSettingsGridLayout.addWidget(self.yTouchingThresholdLabel, 1, 2, 1, 1)

        self.yTouchingThresholdLineEdit = QLineEdit(self.centralwidget)
        self.yTouchingThresholdLineEdit.setObjectName(u"yTouchingThresholdLineEdit")

        self.touchingSettingsGridLayout.addWidget(self.yTouchingThresholdLineEdit, 2, 2, 1, 1)

        self.zTouchingThresholdLineEdit = QLineEdit(self.centralwidget)
        self.zTouchingThresholdLineEdit.setObjectName(u"zTouchingThresholdLineEdit")

        self.touchingSettingsGridLayout.addWidget(self.zTouchingThresholdLineEdit, 2, 3, 1, 1)


        self.rightVerticalLayout.addLayout(self.touchingSettingsGridLayout)

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
        self.menubar.setGeometry(QRect(0, 0, 1158, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.addFilesButton, self.pendingFilesListView)
        QWidget.setTabOrder(self.pendingFilesListView, self.completedFilesListView)
        QWidget.setTabOrder(self.completedFilesListView, self.firstSliceLineEdit)
        QWidget.setTabOrder(self.firstSliceLineEdit, self.lastSliceLineEdit)
        QWidget.setTabOrder(self.lastSliceLineEdit, self.use3DCheckBox)
        QWidget.setTabOrder(self.use3DCheckBox, self.leftSigmaLineEdit)
        QWidget.setTabOrder(self.leftSigmaLineEdit, self.leftSharpenLineEdit)
        QWidget.setTabOrder(self.leftSharpenLineEdit, self.middleSigmaLineEdit)
        QWidget.setTabOrder(self.middleSigmaLineEdit, self.middleSharpenLineEdit)
        QWidget.setTabOrder(self.middleSharpenLineEdit, self.rightSigmaLineEdit)
        QWidget.setTabOrder(self.rightSigmaLineEdit, self.rightSharpenLineEdit)
        QWidget.setTabOrder(self.rightSharpenLineEdit, self.leftSpotDetectionThresholdLineEdit)
        QWidget.setTabOrder(self.leftSpotDetectionThresholdLineEdit, self.middleSpotDetectionThresholdLineEdit)
        QWidget.setTabOrder(self.middleSpotDetectionThresholdLineEdit, self.rightSpotDetectionThresholdLineEdit)
        QWidget.setTabOrder(self.rightSpotDetectionThresholdLineEdit, self.xTouchingThresholdLineEdit)
        QWidget.setTabOrder(self.xTouchingThresholdLineEdit, self.testSettingsPushButton)
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
        self.lastSliceLabel.setText(QCoreApplication.translate("MainWindow", u"Last Slice:", None))
        self.firstSliceLabel.setText(QCoreApplication.translate("MainWindow", u"First Slice:", None))
        self.nucleusSliceLabel.setText(QCoreApplication.translate("MainWindow", u"Nucleus Slice:", None))
        self.channelsLabel.setText(QCoreApplication.translate("MainWindow", u"Channel Settings", None))
        self.middleChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Middle", None))
        self.leftChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Left", None))
        self.rightChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Right", None))
        self.saveDetectedSpotsCheckBox.setText(QCoreApplication.translate("MainWindow", u"Save spot image", None))
        self.rightDenoiseLabel.setText(QCoreApplication.translate("MainWindow", u"Right", None))
        self.sigmaLabel.setText(QCoreApplication.translate("MainWindow", u"Sigma:", None))
        self.denoiseCheckBox.setText(QCoreApplication.translate("MainWindow", u"Do Denoising", None))
        self.sharpenLabel.setText(QCoreApplication.translate("MainWindow", u"Sharpening:", None))
        self.leftDenoiseLabel.setText(QCoreApplication.translate("MainWindow", u"Left", None))
        self.use3DCheckBox.setText(QCoreApplication.translate("MainWindow", u"Use 3D Denoising", None))
        self.denoiseNucleusLabel.setText(QCoreApplication.translate("MainWindow", u"Nucleus", None))
        self.middleDenoiseLabel.setText(QCoreApplication.translate("MainWindow", u"Middle", None))
        self.nucleusMaskingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Masking Threshold: ", None))
        self.maskingCheckBox.setText(QCoreApplication.translate("MainWindow", u"Do Masking", None))
        self.countNucleiCheckBox.setText(QCoreApplication.translate("MainWindow", u"Count Nuclei", None))
        self.rightSpotDetectionLabel.setText(QCoreApplication.translate("MainWindow", u"Right", None))
        self.middleSpotDetection555Label.setText(QCoreApplication.translate("MainWindow", u"Middle", None))
        self.spotDetectionSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Spot Detection Settings", None))
        self.spotDetectionThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Threshold:", None))
        self.leftSpotDetectionLabel.setText(QCoreApplication.translate("MainWindow", u"Left", None))
        self.tripletMaxSizeLabel.setText(QCoreApplication.translate("MainWindow", u"Max Size: ", None))
        self.tripletSettingsLabelabel.setText(QCoreApplication.translate("MainWindow", u"Triplet Detection Settings", None))
        self.findDoubletsCheckBox.setText(QCoreApplication.translate("MainWindow", u"Also Find Doublets", None))
        self.touchingSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Touching Settings", None))
        self.xTouchingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.zTouchingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.touchingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Threshold:", None))
        self.yTouchingThresholdLabel.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.testSettingsPushButton.setText(QCoreApplication.translate("MainWindow", u"Test Settings", None))
        self.runBatchPushButton.setText(QCoreApplication.translate("MainWindow", u"Run Batch", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
    # retranslateUi

