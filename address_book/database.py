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

import sqlite3

class Database:
    class PrimaryKeyError(sqlite3.IntegrityError): pass

    def __init__(self, _file):
        self.connection = sqlite3.connect(_file)
        self.cur = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS users(
            name TEXT PRIMARY KEY)''')

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            user TEXT REFERENCES users(name)
            ON UPDATE CASCADE ON DELETE CASCADE)''')

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS contacts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            mail TEXT,
            address TEXT,
            telephone TEXT,
            category INTEGER REFERENCES categories(id)
            ON UPDATE CASCADE ON DELETE CASCADE)''')

    def get_users(self):
        return [i[0] for i in self.cur.execute('SELECT name FROM users')]

    def addto_users(self, name):
        try:
            self.cur.execute('INSERT INTO users(name) VALUES(?)', (name,))
        except sqlite3.IntegrityError:
            raise self.PrimaryKeyError('There is already a user with this name!')
        self.commit()

    def edit_user(self, newname, oldname):
        try:
            _tuple = (newname, oldname)
            self.cur.execute('UPDATE users SET name=? WHERE name=?', _tuple)
        except sqlite3.IntegrityError:
            raise self.PrimaryKeyError('There is already a user with this name!')
        self.commit()

    def delete_user(self, name):
        self.cur.execute('DELETE FROM users WHERE name=?', (name,))
        self.commit()

    def get_category_from_id(self, _id):
        self.cur.execute('SELECT name FROM categories WHERE id=?', (_id,))
        return self.cur.fetchall()[0][0]

    def get_categories(self, user):
        self.cur.execute('SELECT * FROM categories WHERE user=?', (user,))
        return self.cur.fetchall()

    def get_category_id(self, name, user):
        self.cur.execute('SELECT id FROM categories WHERE name=? AND user=?',(name, user))
        return self.cur.fetchall()[0][0]

    def addto_categories(self, name, user):
        if name in [i[1] for i in self.get_categories(user)]:
            raise self.PrimaryKeyError('There is already a category with this name!')
        self.cur.execute('INSERT INTO categories(name, user) VALUES(?, ?)', (name, user))
        self.commit()

    def delete_category(self, _id):
        self.cur.execute('DELETE FROM categories WHERE id=?', (_id,))
        self.commit()

    def get_contact_from_id(self, _id):
        self.cur.execute('SELECT * FROM contacts WHERE id=?', (_id,))
        return self.cur.fetchall()

    def get_contacts(self, categ):
        self.cur.execute('SELECT * FROM contacts WHERE category=?', (categ,))
        return self.cur.fetchall()

    def get_all_contacts(self, user):
        categories = tuple(i[0] for i in self.get_categories(user))
        if len(categories) == 1: categories = '({0})'.format(categories[0])
        cmd = 'SELECT * FROM contacts WHERE category IN {0}'.format(categories)
        return self.cur.execute(cmd).fetchall()

    def addto_contacts(self, data):
        cmd = 'INSERT INTO contacts(name, surname, mail, address, telephone, '
        cmd += 'category) VALUES(?, ?, ?, ?, ?, ?)'
        self.cur.execute(cmd, tuple(data))
        self.commit()

    def edit_contact(self, data, _id):
        cmd = 'UPDATE contacts SET name=?, surname=?, mail=?, address=?, '
        cmd += 'telephone=?, category=? WHERE id=?'
        self.cur.execute(cmd, tuple(data+[_id]))
        self.commit()

    def delete_contact(self, _id):
        self.cur.execute('DELETE FROM contacts WHERE id=?', (_id,))
        self.commit()

    def delete_all_contacts(self):
        self.cur.execute('DELETE FROM contacts')
        self.commit()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
