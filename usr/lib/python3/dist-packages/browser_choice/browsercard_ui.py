


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BrowserCard(object):
    def setupUi(self, BrowserCard):
        BrowserCard.setObjectName("BrowserCard")
        BrowserCard.resize(155, 268)
        self.verticalLayout = QtWidgets.QVBoxLayout(BrowserCard)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.appIconLabel = QtWidgets.QLabel(BrowserCard)
        self.appIconLabel.setMaximumSize(QtCore.QSize(48, 48))
        self.appIconLabel.setScaledContents(True)
        self.appIconLabel.setObjectName("appIconLabel")
        self.horizontalLayout.addWidget(self.appIconLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.appRadioButton = QtWidgets.QRadioButton(BrowserCard)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.appRadioButton.sizePolicy().hasHeightForWidth())
        self.appRadioButton.setSizePolicy(sizePolicy)
        self.appRadioButton.setObjectName("appRadioButton")
        self.horizontalLayout_2.addWidget(self.appRadioButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.label = QtWidgets.QLabel(BrowserCard)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.appVendorIconLabel = QtWidgets.QLabel(BrowserCard)
        self.appVendorIconLabel.setMaximumSize(QtCore.QSize(20, 20))
        self.appVendorIconLabel.setScaledContents(True)
        self.appVendorIconLabel.setObjectName("appVendorIconLabel")
        self.horizontalLayout_3.addWidget(self.appVendorIconLabel)
        self.appVendorLabel = QtWidgets.QLabel(BrowserCard)
        self.appVendorLabel.setObjectName("appVendorLabel")
        self.horizontalLayout_3.addWidget(self.appVendorLabel)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.appWikiLabel = QtWidgets.QLabel(BrowserCard)
        self.appWikiLabel.setObjectName("appWikiLabel")
        self.verticalLayout.addWidget(self.appWikiLabel)
        self.label_5 = QtWidgets.QLabel(BrowserCard)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.availableInstallListLabel = QtWidgets.QLabel(BrowserCard)
        self.availableInstallListLabel.setObjectName("availableInstallListLabel")
        self.verticalLayout.addWidget(self.availableInstallListLabel)
        self.installedHeaderLabel = QtWidgets.QLabel(BrowserCard)
        self.installedHeaderLabel.setObjectName("installedHeaderLabel")
        self.verticalLayout.addWidget(self.installedHeaderLabel)
        self.installedLabel = QtWidgets.QLabel(BrowserCard)
        self.installedLabel.setObjectName("installedLabel")
        self.verticalLayout.addWidget(self.installedLabel)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)

        self.retranslateUi(BrowserCard)
        QtCore.QMetaObject.connectSlotsByName(BrowserCard)

    def retranslateUi(self, BrowserCard):
        _translate = QtCore.QCoreApplication.translate
        BrowserCard.setWindowTitle(_translate("BrowserCard", "Form"))
        self.appIconLabel.setText(_translate("BrowserCard", "O"))
        self.appRadioButton.setText(_translate("BrowserCard", "App Name"))
        self.label.setText(_translate("BrowserCard", "by"))
        self.appVendorIconLabel.setText(_translate("BrowserCard", "O"))
        self.appVendorLabel.setText(_translate("BrowserCard", "<a href=\"https://example.com\">Vendor</a>"))
        self.appWikiLabel.setText(_translate("BrowserCard", "<a href=\"https://www.example.com\">App info</a>, <a href=\"https://www.kicksecure.com/wiki\">Wiki</a>"))
        self.label_5.setText(_translate("BrowserCard", "<html><head/><body><p>Available as:</p></body></html>"))
        self.availableInstallListLabel.setText(_translate("BrowserCard", "<html><head/><body>\n"
"<ul>\n"
"<li>Inst. Method 1</li>\n"
"<li>Inst. Method 2</li>\n"
"</body></html>"))
        self.installedHeaderLabel.setText(_translate("BrowserCard", "<html><head/><body><p>Installed as:</p></body></html>"))
        self.installedLabel.setText(_translate("BrowserCard", "<html><head/><body>\n"
"<ul>\n"
"<li>Inst. Method 1</li>\n"
"</ul>\n"
"</body></html>"))
