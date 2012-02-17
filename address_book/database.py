#!/usr/bin/python3
#
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

class PrimaryKeyError(sqlite3.IntegrityError): pass

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("test.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
            name TEXT PRIMARY KEY
            )''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            user TEXT REFERENCES users(name)
            ON UPDATE CASCADE ON DELETE CASCADE
            )''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            mail TEXT,
            address TEXT,
            telephone INTEGER,
            category INTEGER REFERENCES categories(id)
            ON UPDATE CASCADE ON DELETE CASCADE
            )''')

    def get_users(self):
        return [i[0] for i in self.cursor.execute('SELECT name FROM users')]
        
    def addto_users(self, name):
        try:
            self.cursor.execute('INSERT INTO users(name) VALUES(?)', (name,))
        except sqlite3.IntegrityError:
            raise PrimaryKeyError('There is already a user with this name!')
        self.commit()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
