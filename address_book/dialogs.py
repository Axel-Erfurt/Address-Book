#!/usr/bin/python3

# Copyright (C) 2012 Ilias Stamatis <stamatis.iliass@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QDialog, QFrame, QLabel,
                  QLineEdit, QComboBox, QPushButton, QDialogButtonBox,
                  QMessageBox)

from address_book import database
import pyqttools


class AddOrEditDlg(QDialog):
    def __init__(self, oldname, edit=False, parent=None):
        super(AddOrEditDlg, self).__init__(parent)
        self.edit = edit
        self.oldname = oldname
        title = 'Add User' if not self.edit else 'Edit User'
        self.setWindowTitle('Address Book - ' + title)
        self.resize(260, 111)

        text = 'New user:' if not self.edit else 'New username:'
        label = QLabel(text)
        self.userLineEdit = QLineEdit()
        if self.edit: self.userLineEdit.setText(self.oldname)
        self.buttonBox = QDialogButtonBox(
                                   QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), (label, None))
        hlayout2 =pyqttools.add_to_layout(QHBoxLayout(),(None, self.buttonBox))
        f_layout = pyqttools.add_to_layout(QVBoxLayout(), (hlayout1,
                                                  self.userLineEdit, hlayout2))
        self.setLayout(f_layout)

        self.buttonBox.accepted.connect(self.add_or_edit_user)
        self.buttonBox.rejected.connect(self.reject)

    def add_or_edit_user(self):
        try:
            if not self.edit:
                database.addto_users(self.userLineEdit.text())
            else:
                database.edit_user(self.userLineEdit.text(), self.oldname)
            QDialog.accept(self)
        except database.PrimaryKeyError as e:
            QMessageBox.warning(self, 'Address Book - Error!', str(e))


class UserPanelDlg(QDialog):
    def __init__(self, parent=None):
        super(UserPanelDlg, self).__init__(parent)
        self.setWindowTitle('Address Book - User Panel')
        self.resize(330, 164)

        chooseLabel = QLabel('Choose User:')
        self.userComboBox = QComboBox()
        newButton = QPushButton('New user')
        editButton = QPushButton('Edit username')
        deleteButton = QPushButton('Delete user')
        connectButton = QPushButton('Connect')
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), (chooseLabel, None))
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(),(None, connectButton))
        vlayout1 = pyqttools.add_to_layout(QVBoxLayout(), (None, hlayout1,
                                                      self.userComboBox, None))
        vlayout2 = pyqttools.add_to_layout(QVBoxLayout(), (newButton,
                                                     editButton, deleteButton))
        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(), (vlayout1, line,
                                                                     vlayout2))
        f_layout = pyqttools.add_to_layout(QVBoxLayout(), (hlayout3, hlayout2))
        self.setLayout(f_layout)

        newButton.clicked.connect(self.add_user)
        editButton.clicked.connect(self.edit_user)
        deleteButton.clicked.connect(self.delete_user)
        connectButton.clicked.connect(self.accept)

        self.fill_combobox()

    def fill_combobox(self):
        users = database.get_users()
        self.userComboBox.clear()
        self.userComboBox.addItems(users)
        self.userComboBox.setEnabled(bool(users))

    def add_user(self):
        dialog = AddOrEditDlg('', False)
        dialog.exec_()
        self.fill_combobox()

    def edit_user(self):
        dialog = AddOrEditDlg(self.userComboBox.currentText(), True)
        dialog.exec_()
        self.fill_combobox()

    def delete_user(self):
        user = self.userComboBox.currentText()
        reply = QMessageBox.question(self, "Address Book - Delete User",
                       "Are sou sure that you want to delete {};".format(user),
                                            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            database.delete_user(user)
            self.fill_combobox()

    def accept(self):
        self.user = self.userComboBox.currentText()
        QDialog.accept(self)

    def reject(self):
        database.close()
        QDialog.reject(self)
