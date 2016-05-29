#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import sqlite3
from common import conf


class UrlDb:
    def __init__(self):
        self.conn = None
        self.c = None

    def _open_sqlite3(self, url_db_file):
        self.conn = sqlite3.connect(
            url_db_file,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()

    def _clear_old_db_data(self):
        reference = datetime.datetime.now() - datetime.timedelta(
            seconds=conf.url_db_period())
        self.c.execute('DELETE FROM urls WHERE created < ?', (reference,))

    def open(self):
        url_db_file = conf.url_db_file()
        db_exist = os.path.isfile(url_db_file)
        self._open_sqlite3(url_db_file)
        if not db_exist:
            self.c.execute('CREATE TABLE urls (url TEXT, created TIMESTAMP)')
            self.c.execute('CREATE INDEX url_index ON urls(url, created)')

    def close(self):
        self._clear_old_db_data()
        self.conn.commit()
        self.c.close()
        self.c = None
        self.conn.close()
        self.conn = None

    def url_in_db(self, url):
        self.c.execute('SELECT * FROM urls WHERE url == ?', (url,))
        return self.c.fetchone() is not None

    def add_url(self, url, created):
        self.c.execute('INSERT INTO urls(url, created) VALUES (?, ?)',
                       (url, created))


url_db = UrlDb()
