import os
import sys

from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def get_db_path():
    return resource_path('assets/db.sqlite')


def extract_types(db: QSqlDatabase):
    query = QSqlQuery("SELECT * FROM types", db)
    query.exec_()
    types = {}
    while query.next():
        types[query.value(0)] = query.value(1).capitalize()
    return types


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
