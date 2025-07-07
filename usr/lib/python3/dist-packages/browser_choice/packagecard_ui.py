


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PackageCard(object):
    def setupUi(self, PackageCard):
        PackageCard.setObjectName("PackageCard")
        PackageCard.resize(232, 162)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PackageCard.sizePolicy().hasHeightForWidth())
        PackageCard.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(PackageCard)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.packageIconLabel = QtWidgets.QLabel(PackageCard)
        self.packageIconLabel.setMaximumSize(QtCore.QSize(48, 48))
        self.packageIconLabel.setScaledContents(True)
        self.packageIconLabel.setObjectName("packageIconLabel")
        self.horizontalLayout.addWidget(self.packageIconLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.packageRadioButton = QtWidgets.QRadioButton(PackageCard)
        self.packageRadioButton.setObjectName("packageRadioButton")
        self.verticalLayout.addWidget(self.packageRadioButton)
        self.packageInfoLabel = QtWidgets.QLabel(PackageCard)
        self.packageInfoLabel.setWordWrap(True)
        self.packageInfoLabel.setObjectName("packageInfoLabel")
        self.verticalLayout.addWidget(self.packageInfoLabel)
        spacerItem2 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(PackageCard)
        QtCore.QMetaObject.connectSlotsByName(PackageCard)

    def retranslateUi(self, PackageCard):
        _translate = QtCore.QCoreApplication.translate
        PackageCard.setWindowTitle(_translate("PackageCard", "Form"))
        self.packageIconLabel.setText(_translate("PackageCard", "O"))
        self.packageRadioButton.setText(_translate("PackageCard", "App Name from Repository"))
        self.packageInfoLabel.setText(_translate("PackageCard", "App Name from www.example.com repository. Managed by package-manager. (Installed)"))
