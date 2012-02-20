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

from PyQt4.QtGui import (QHBoxLayout, QVBoxLayout, QGridLayout, QDialog,
                  QFrame, QLabel, QLineEdit, QComboBox, QPushButton,
                  QDialogButtonBox, QMessageBox)

import pyqttools

class ValidationError(Exception): pass

class AddOrEditUserDlg(QDialog):
    def __init__(self, oldname, edit=False, parent=None):
        super(AddOrEditUserDlg, self).__init__(parent)
        self.edit = edit
        title = 'Add User' if not self.edit else 'Edit User'
        self.setWindowTitle('Address Book - ' + title)
        self.resize(260, 111)

        self.db = parent.db
        self.oldname = oldname

        text = 'New user:' if not self.edit else 'New username:'
        self.userLineEdit = QLineEdit()
        if self.edit: self.userLineEdit.setText(self.oldname)
        self.buttonBox = QDialogButtonBox(
                                   QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), (QLabel(text), None))
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(),(None, self.buttonBox))
        f_layout = pyqttools.add_to_layout(QVBoxLayout(), (hlayout1,
                                                  self.userLineEdit, hlayout2))
        self.setLayout(f_layout)

        self.buttonBox.accepted.connect(self.add_or_edit_user)
        self.buttonBox.rejected.connect(self.reject)

    def add_or_edit_user(self):
        try:
            if not self.edit:
                self.db.addto_users(self.userLineEdit.text())
            else:
                self.db.edit_user(self.userLineEdit.text(), self.oldname)
            QDialog.accept(self)
        except self.db.PrimaryKeyError as e:
            QMessageBox.warning(self, 'Address Book - Error!', str(e))


class UserPanelDlg(QDialog):
    def __init__(self, parent=None):
        super(UserPanelDlg, self).__init__(parent)
        self.setWindowTitle('Address Book - User Panel')
        self.resize(330, 164)

        self.parent = parent
        self.db = self.parent.db

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
        users = self.db.get_users()
        self.userComboBox.clear()
        self.userComboBox.addItems(users)
        self.userComboBox.setEnabled(bool(users))

    def add_user(self):
        AddOrEditUserDlg('', False, self).exec_()
        self.fill_combobox()

    def edit_user(self):
        AddOrEditUserDlg(self.userComboBox.currentText(), True, self).exec_()
        self.fill_combobox()

    def delete_user(self):
        user = self.userComboBox.currentText()
        reply = QMessageBox.question(self, "Address Book - Delete User",
                      "Are sou sure that you want to delete {0}?".format(user),
                                            QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.db.delete_user(user)
            self.fill_combobox()

    def accept(self):
        self.user = self.userComboBox.currentText()
        QDialog.accept(self)

    def reject(self):
        self.parent.close()
        QDialog.reject(self)

class AddorEditContactDlg(QDialog):
    def __init__(self, categories, edit=False, data=[], parent=None):
        super(AddorEditContactDlg, self).__init__(parent)
        title = 'Add' if not edit else 'Edit'
        self.setWindowTitle('Address Book - {0} Contact'.format(title))
        self.resize(345, 279)
        self.categories = categories

        self.nameLineEdit = QLineEdit()
        self.surnameLineEdit = QLineEdit()
        self.mailLineEdit = QLineEdit()
        self.addressLineEdit = QLineEdit()
        self.telLineEdit = QLineEdit()
        self.categLineEdit = QLineEdit()
        self.categComboBox = QComboBox()
        self.buttonBox = QDialogButtonBox(
                                   QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        self.lineedits = (self.nameLineEdit, self.surnameLineEdit,
                     self.mailLineEdit, self.addressLineEdit, self.telLineEdit)
        labels = ('Name:', 'Surname:', 'e-mail:', 'Address:', 'Telephone:')
        grid_tuple = ()
        for label, line in zip(labels, self.lineedits):
            grid_tuple += ((QLabel(label), line),)
        grid = pyqttools.add_to_grid(QGridLayout(), grid_tuple)

        hlayout1 = pyqttools.add_to_layout(QHBoxLayout(), (grid, None))
        _tuple = (QLabel('Category:'), self.categComboBox, QLabel('New:'),
                                                      self.categLineEdit ,None)
        hlayout2 = pyqttools.add_to_layout(QHBoxLayout(), _tuple)
        hlayout3 = pyqttools.add_to_layout(QHBoxLayout(), (None, self.buttonBox))
        f_layout = pyqttools.add_to_layout(QVBoxLayout(), (hlayout1, hlayout2,
                                                               None, hlayout3))
        self.setLayout(f_layout)

        self.categComboBox.currentIndexChanged.connect(self.enable_LineEdit)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.fill_combobox()

        if edit:
            for num, line in enumerate(self.lineedits):
                line.setText(data[num])
            categ = self.categComboBox.findText(data[5])
            self.categComboBox.setCurrentIndex(categ)

    def fill_combobox(self):
        self.categComboBox.addItems(['New']+self.categories)

    def enable_LineEdit(self):
        enable = bool(self.categComboBox.currentText() == 'New')
        self.categLineEdit.setEnabled(enable)

    def validation(self):
        if self.categLineEdit.isEnabled():
            try:
                if not self.categLineEdit.text():
                    raise ValidationError('You should define a category name!')
                elif self.categLineEdit.text() in self.categories:
                    raise ValidationError(
                                 'There is already a category with this name!')
            except ValidationError as e:
                QMessageBox.warning(self, "Address Book - Error!", str(e))
                self.categLineEdit.selectAll()
                self.categLineEdit.setFocus()
                return False
        return True

    def accept(self):
        if self.validation():
            self.values = [i.text() for i in self.lineedits]
            if self.categLineEdit.isEnabled():
                self.values.append(self.categLineEdit.text())
            else:
                self.values.append(self.categComboBox.currentText())
            QDialog.accept(self)
