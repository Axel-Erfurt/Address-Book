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

from __init__ import __version__
from resources import qrc_resources

from PyQt4.QtCore import Qt, QSize, QT_VERSION_STR,PYQT_VERSION_STR
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                  QHBoxLayout, QLabel, QComboBox, QListWidget, QLineEdit,
                  QPushButton, QToolButton, QFrame, QIcon, QListWidgetItem,
                  QMessageBox)

import os
import sys
import platform
import dialogs
import pyqttools
import database


class MyListItem(QListWidgetItem):
    def __init__(self, text, _id, parent=None):
        super(MyListItem, self).__init__(text, parent)
        self._id = _id

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Address Book')
        self.resize(704, 459)
        db_file = self.database_file()        
        self.db = database.Database(db_file)

        dialog = dialogs.UserPanelDlg(self)
        if dialog.exec_():
            self.user = dialog.user
        else:
            self.close()

        self.categComboBox = QComboBox()
        self.cont_numLabel = QLabel()
        self.contactsListWidget = QListWidget()
        self.searchLineEdit = QLineEdit()

        widgets = ((QLabel('Category:'), self.categComboBox),
                   (self.cont_numLabel, None),
                   (self.contactsListWidget,),
                   (QLabel('Search:'), self.searchLineEdit))
        vlayout1 = QVBoxLayout()

        for i in widgets:
            hlayout = pyqttools.add_to_layout(QHBoxLayout(), i)
            vlayout1.addLayout(hlayout)

        addToolButton = QToolButton()
        addToolButton.setIcon(QIcon(':addcontact.jpeg'))
        addToolButton.setIconSize(QSize(45, 45))
        self.showLabel = QLabel()
        self.showLabel.setFrameShape(QFrame.StyledPanel)
        self.showLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.editButton = QPushButton('Edit')
        self.delButton = QPushButton('Delete')

        widgets = ((None, addToolButton, None),
                   (self.showLabel,),
                   (None, self.editButton, self.delButton))
        vlayout2 = QVBoxLayout()

        for i in widgets:
            hlayout = pyqttools.add_to_layout(QHBoxLayout(), i)
            vlayout2.addLayout(hlayout)

        f_layout = pyqttools.add_to_layout(QHBoxLayout(), (vlayout1, vlayout2))

        Widget = QWidget()
        Widget.setLayout(f_layout)
        self.setCentralWidget(Widget)

        self.statusBar = self.statusBar()
        self.userLabel = QLabel()
        self.statusBar.addPermanentWidget(self.userLabel)

        c_action = pyqttools.create_action
        panelAction = c_action(self, 'User panel', triggered=self.user_panel)
        quitAction = c_action(self, 'Quit', 'Ctrl+Q',triggered=self.close)
        add_contactAction = c_action(self, 'Add contact', 'Ctrl+N',
                                                    triggered=self.add_contact)
        delete_allAction = c_action(self, 'Delete all contacts',
                                                     triggered=self.delete_all)
        delete_categAction = c_action(self, 'Delete categories',
                                              triggered=self.delete_categories)
        backupAction = c_action(self, 'Backup', triggered=self.backup)
        restoreAction = c_action(self, 'Restore', triggered=self.restore)                                      
        aboutAction = c_action(self, 'About', 'Ctrl+?', triggered=self.about)

        fileMenu = self.menuBar().addMenu('File')
        contactsMenu = self.menuBar().addMenu('Contacts')
        deleteMenu = self.menuBar().addMenu(self.tr('Delete'))
        backupMenu = self.menuBar().addMenu(self.tr('Backup'))
        helpMenu = self.menuBar().addMenu('Help')

        pyqttools.add_actions(fileMenu, [panelAction, None, quitAction])
        pyqttools.add_actions(contactsMenu, [add_contactAction])
        pyqttools.add_actions(deleteMenu,[delete_allAction,delete_categAction])
        pyqttools.add_actions(backupMenu, [backupAction, restoreAction])
        pyqttools.add_actions(helpMenu, [aboutAction])

        addToolButton.clicked.connect(self.add_contact)
        self.editButton.clicked.connect(self.edit_contact)
        self.delButton.clicked.connect(self.delete_contact)
        self.categComboBox.currentIndexChanged.connect(self.fill_ListWidget)
        self.contactsListWidget.currentRowChanged.connect(self.show_contact)

        self.fill_categComboBox()
        self.refresh_userLabel()

    def fill_categComboBox(self):
        categories = ['All']
        categories.extend([i[1] for i in self.db.get_categories(self.user)])
        self.categComboBox.currentIndexChanged.disconnect(self.fill_ListWidget)
        self.categComboBox.clear()
        self.categComboBox.addItems(categories)
        self.categComboBox.currentIndexChanged.connect(self.fill_ListWidget)
        self.fill_ListWidget()

    def fill_ListWidget(self):
        self.showLabel.clear()
        self.contactsListWidget.clear()

        category = self.categComboBox.currentText()
        if category == 'All':
            contacts = self.db.get_all_contacts(self.user)
        else:
            categ_id = self.db.get_category_id(category, self.user)
            if categ_id is None: return
            contacts = self.db.get_contacts(categ_id)
        for i in contacts:
            _id, name, surname = i[0], i[1], i[2]
            item = MyListItem(name+' '+surname, _id)
            self.contactsListWidget.addItem(item)

        self.contactsListWidget.setCurrentRow(0)
        self.refresh_contacts_number()
        self.set_buttons_enabled()

    def refresh_userLabel(self):
        self.userLabel.setText('User:  '+self.user)

    def refresh_contacts_number(self):
        text = 'Contacts Numer:  {0}'.format(self.contactsListWidget.count())
        self.cont_numLabel.setText(text)

    def set_buttons_enabled(self):
        enable = bool(self.contactsListWidget)
        self.editButton.setEnabled(enable)
        self.delButton.setEnabled(enable)

    def user_panel(self):
        dialog = dialogs.UserPanelDlg(self)
        if dialog.exec_():
            self.user = dialog.user
            self.fill_categComboBox()
            self.refresh_userLabel()

    def show_contact(self):
        try:
            _id = self.contactsListWidget.currentItem()._id
        except AttributeError:
            return
        _id, name, surname, mail, address, tel, categ_id = \
                                           self.db.get_contact_from_id(_id)[0]
        category = self.db.get_category_from_id(categ_id)
        text = ''
        data = (name, surname, mail, address, tel, category)
        labs = ('Name', 'Surname', 'e-mail', 'Address', 'Telephone', 'Category')
        for i, y in zip(labs, data):
            text += '''<p style=\' margin-top:0px; margin-bottom:0px; \'>
                  <span style=\' font-weight:600;\'>{0}:</span> {1} </p>\n'''\
                                                                  .format(i, y)
        self.showLabel.setText(text)

    def add_contact(self):
        categories = [i[1] for i in self.db.get_categories(self.user)]
        dialog = dialogs.AddorEditContactDlg(categories)
        if dialog.exec_():
            data = dialog.values
            if data[-1] not in categories:
                self.db.addto_categories(data[-1], self.user)
            categ_id = self.db.get_category_id(data[-1], self.user)
            data[-1] = categ_id
            self.db.addto_contacts(data)
            self.fill_categComboBox()

    def edit_contact(self):
        _id = self.contactsListWidget.currentItem()._id
        data = list(self.db.get_contact_from_id(_id)[0])
        categ = self.db.get_category_from_id(data[-1])
        data[-1] = categ
        categories = [i[1] for i in self.db.get_categories(self.user)]
        dialog = dialogs.AddorEditContactDlg(categories, True, data)
        if dialog.exec_():
            new_data = dialog.values
            if new_data[-1] not in categories:
                self.db.addto_categories(new_data[-1], self.user)
            categ_id = self.db.get_category_id(new_data[-1], self.user)
            new_data[-1] = categ_id
            self.db.edit_contact(new_data, _id)
            self.fill_categComboBox()

    def delete_contact(self):
        reply = QMessageBox.question(self, "Address Book - Delete Contact",
        "Are you sure that you want to delete this contact?",
        QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            _id = self.contactsListWidget.currentItem()._id
            self.db.delete_contact(_id)
            self.fill_ListWidget()

    def delete_all(self):
        reply = QMessageBox.question(self, "Address Book - Delete Contact",
        "Are you sure that you want to delete all contacts?",
        QMessageBox.Yes|QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.db.delete_all_contacts()
            self.fill_ListWidget()

    def delete_categories(self):
        pass

    def backup(self):
        pass

    def restore(self):
        pass    

    def database_file(self):
        _file = 'addressbook.db'
        if not platform.platform().startswith('Windows'):
            folder = os.getenv('HOME') + os.sep + '.addressbook'
            if not os.path.exists(folder): os.mkdir(folder)
            _file = folder + os.sep + _file
        return _file

    def about(self):
        link = 'http://wiki.ubuntu-gr.org/Address%20Book'
        QMessageBox.about(self, self.tr('About') + ' FF Multi Converter',
            '''<b> Address Book {0} </b>
            <p>Gui application to organize your contacts!
            <p>Copyright &copy; 2012 Ilias Stamatis
            <br>License: GNU GPL3
            <p><a href="{1}">http://wiki.ubuntu-gr.org/Address Book</a>
            <p>Python {2} - Qt {3} - PyQt {4} on {5}'''
            .format(__version__, link, platform.python_version()[:5],
            QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def close(self):
        self.db.close()
        sys.exit()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/addressbook.jpeg'))
    address_book = MainWindow()
    address_book.show()
    app.exec_()

if __name__ == '__main__':
    main()
