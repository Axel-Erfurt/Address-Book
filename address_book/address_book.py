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

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                  QHBoxLayout, QLabel, QComboBox, QListWidget, QLineEdit,
                  QPushButton, QToolButton, QFrame, QIcon, QListWidgetItem)

import sys
import dialogs
import pyqttools
import database

database = database.Database()


class MyListItem(QListWidgetItem):
    def __init__(self, text, _id, parent=None):
        super(MyListItem, self).__init__(text, parent)
        self._id = _id

class MainWindow(QMainWindow):
    def __init__(self, user, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Address Book')
        self.resize(704, 459)
        self.user = user

        categLabel = QLabel('Category:')
        self.categComboBox = QComboBox()
        self.cont_numLabel = QLabel()
        self.contactsListWidget = QListWidget()
        searchLabel = QLabel('Search')
        self.searchLineEdit = QLineEdit()

        widgets = ((categLabel, self.categComboBox),
                   (self.cont_numLabel, None),
                   (self.contactsListWidget,),
                   (searchLabel, self.searchLineEdit))
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

        panelAction = pyqttools.create_action(self, 'User panel',
                                                     triggered=self.user_panel)
        quitAction = pyqttools.create_action(self, 'Quit', 'Ctrl+Q',
                                                          triggered=self.close)
        add_contactAction = pyqttools.create_action(self, 'Add contact',
                                          'Ctrl+N', triggered=self.add_contact)
        delete_allAction = pyqttools.create_action(self,
                              'Delete all contacts', triggered=self.delete_all)
        delete_categAction = pyqttools.create_action(self, 'Delete '
                                'categories', triggered=self.delete_categories)
        aboutAction = pyqttools.create_action(self, 'About', 'Ctrl+?',
                                                          triggered=self.about)

        fileMenu = self.menuBar().addMenu('File')
        contactsMenu = self.menuBar().addMenu('Contacts')
        deleteMenu = self.menuBar().addMenu(self.tr('Delete'))
        helpMenu = self.menuBar().addMenu('Help')

        pyqttools.add_actions(fileMenu, [panelAction, None, quitAction])
        pyqttools.add_actions(contactsMenu, [add_contactAction])
        pyqttools.add_actions(deleteMenu,[delete_allAction,delete_categAction])
        pyqttools.add_actions(helpMenu, [aboutAction])

        self.categComboBox.currentIndexChanged.connect(self.fill_ListWidget)
        self.contactsListWidget.currentRowChanged.connect(self.show_contact)

        self.fill_categComboBox()
        self.refresh_userLabel()

    def fill_categComboBox(self):
        categories = ['All']
        categories.extend([i[1] for i in database.get_categories(self.user)])
        self.categComboBox.clear()
        self.categComboBox.addItems(categories)
        self.fill_ListWidget()

    def fill_ListWidget(self):
        self.showLabel.clear()
        self.contactsListWidget.clear()
        
        category = self.categComboBox.currentText()
        if category == 'All':
            contacts = database.get_all_contacts(self.user)
        else:
            categ_id = database.get_category_id(category, self.user)
            if categ_id is None: return
            contacts = database.get_contacts(categ_id)
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
        text = 'Contacts Numer: {0}'.format(self.contactsListWidget.count())
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
                                           database.get_contact_from_id(_id)[0]
        category = database.get_category_from_id(categ_id)
        text = ''
        data = (name, surname, mail, address, tel, category)
        labs = ('Name', 'Surname', 'e-mail', 'Address', 'Telephone', 'Category')
        for i, y in zip(labs, data):
            text += '''<p style=\' margin-top:0px; margin-bottom:0px; \'>
                  <span style=\' font-weight:600;\'>{0}:</span> {1} </p>\n'''\
                                                                  .format(i, y)
        self.showLabel.setText(text)

    def add_contact(self):
        pass

    def delete_all(self):
        pass

    def delete_categories(self):
        pass

    def about(self):
        pass

    def close(self):
        database.close()
        QMainWindow.close(self)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/addressbook.jpeg'))

    dialog = dialogs.UserPanelDlg()
    if dialog.exec_():
        address_book = MainWindow(dialog.user)
        address_book.show()
        app.exec_()

if __name__ == '__main__':
    main()
