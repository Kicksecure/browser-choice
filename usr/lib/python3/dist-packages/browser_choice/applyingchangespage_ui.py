


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ApplyingChangesPage(object):
    def setupUi(self, ApplyingChangesPage):
        ApplyingChangesPage.setObjectName("ApplyingChangesPage")
        ApplyingChangesPage.resize(493, 171)
        self.verticalLayout = QtWidgets.QVBoxLayout(ApplyingChangesPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(ApplyingChangesPage)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtWidgets.QLabel(ApplyingChangesPage)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.continueButton = QtWidgets.QPushButton(ApplyingChangesPage)
        icon = QtGui.QIcon.fromTheme("go-next")
        self.continueButton.setIcon(icon)
        self.continueButton.setObjectName("continueButton")
        self.horizontalLayout_2.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ApplyingChangesPage)
        QtCore.QMetaObject.connectSlotsByName(ApplyingChangesPage)

    def retranslateUi(self, ApplyingChangesPage):
        _translate = QtCore.QCoreApplication.translate
        ApplyingChangesPage.setWindowTitle(_translate("ApplyingChangesPage", "Form"))
        self.label.setText(_translate("ApplyingChangesPage", "<span style=\" font-size:20pt; font-weight:600;\">Step 3/4: Applying Software Changes</span>"))
        self.label_2.setText(_translate("ApplyingChangesPage", "A terminal window has been opened for finishing the installation or removal process. Please finish installing or removing your selected application there."))
        self.continueButton.setText(_translate("ApplyingChangesPage", "Continue"))
