


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChangesCompletePage(object):
    def setupUi(self, ChangesCompletePage):
        ChangesCompletePage.setObjectName("ChangesCompletePage")
        ChangesCompletePage.resize(504, 186)
        self.verticalLayout = QtWidgets.QVBoxLayout(ChangesCompletePage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(ChangesCompletePage)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.actionCompleteLabel = QtWidgets.QLabel(ChangesCompletePage)
        self.actionCompleteLabel.setWordWrap(True)
        self.actionCompleteLabel.setObjectName("actionCompleteLabel")
        self.verticalLayout.addWidget(self.actionCompleteLabel)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.launchAppCheckbox = QtWidgets.QCheckBox(ChangesCompletePage)
        self.launchAppCheckbox.setObjectName("launchAppCheckbox")
        self.horizontalLayout_2.addWidget(self.launchAppCheckbox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.doneButton = QtWidgets.QPushButton(ChangesCompletePage)
        icon = QtGui.QIcon.fromTheme("checkbox")
        self.doneButton.setIcon(icon)
        self.doneButton.setObjectName("doneButton")
        self.horizontalLayout_3.addWidget(self.doneButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(ChangesCompletePage)
        QtCore.QMetaObject.connectSlotsByName(ChangesCompletePage)

    def retranslateUi(self, ChangesCompletePage):
        _translate = QtCore.QCoreApplication.translate
        ChangesCompletePage.setWindowTitle(_translate("ChangesCompletePage", "Form"))
        self.label.setText(_translate("ChangesCompletePage", "<span style=\" font-size:20pt; font-weight:600;\">Step 4/4: Software Changes Complete</span>"))
        self.actionCompleteLabel.setText(_translate("ChangesCompletePage", "The application \"App Name\" has been installed/removed via \"Repository\". Click \"Done\" to exit the wizard."))
        self.launchAppCheckbox.setText(_translate("ChangesCompletePage", "Launch \"App Name\""))
        self.doneButton.setText(_translate("ChangesCompletePage", "Done"))
