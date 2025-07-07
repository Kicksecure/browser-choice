


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ConfirmInstallationDialog(object):
    def setupUi(self, ConfirmInstallationDialog):
        ConfirmInstallationDialog.setObjectName("ConfirmInstallationDialog")
        ConfirmInstallationDialog.resize(445, 204)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfirmInstallationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.actionInfoLabel = QtWidgets.QLabel(ConfirmInstallationDialog)
        self.actionInfoLabel.setWordWrap(True)
        self.actionInfoLabel.setObjectName("actionInfoLabel")
        self.verticalLayout.addWidget(self.actionInfoLabel)
        self.commandLabel = QtWidgets.QLabel(ConfirmInstallationDialog)
        self.commandLabel.setObjectName("commandLabel")
        self.verticalLayout.addWidget(self.commandLabel)
        self.label_3 = QtWidgets.QLabel(ConfirmInstallationDialog)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        spacerItem = QtWidgets.QSpacerItem(20, 3, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.backButton = QtWidgets.QPushButton(ConfirmInstallationDialog)
        icon = QtGui.QIcon.fromTheme("go-previous")
        self.backButton.setIcon(icon)
        self.backButton.setObjectName("backButton")
        self.horizontalLayout.addWidget(self.backButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.continueButton = QtWidgets.QPushButton(ConfirmInstallationDialog)
        icon = QtGui.QIcon.fromTheme("go-next")
        self.continueButton.setIcon(icon)
        self.continueButton.setObjectName("continueButton")
        self.horizontalLayout.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ConfirmInstallationDialog)
        QtCore.QMetaObject.connectSlotsByName(ConfirmInstallationDialog)

    def retranslateUi(self, ConfirmInstallationDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfirmInstallationDialog.setWindowTitle(_translate("ConfirmInstallationDialog", "Confirm Installation Options"))
        self.actionInfoLabel.setText(_translate("ConfirmInstallationDialog", "The application \"App Name\" will be installed/removed via \"Repository\". The following command will be executed to install/remove the application:"))
        self.commandLabel.setText(_translate("ConfirmInstallationDialog", "<code>actual command here</code>"))
        self.label_3.setText(_translate("ConfirmInstallationDialog", "Click \"Continue\" to proceed with these changes, or \"Back\" to return to the \"Choose Installation Options\" page."))
        self.backButton.setText(_translate("ConfirmInstallationDialog", "Back"))
        self.continueButton.setText(_translate("ConfirmInstallationDialog", "Continue"))
