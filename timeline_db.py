#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import os
import sqlite3
from common import conf


class TimelineDb:
    def __init__(self):
        self.conn = None
        self.c = None

    def _open_sqlite3(self, timeline_db_file):
        self.conn = sqlite3.connect(
            timeline_db_file,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    def _clear_old_db_data(self):
        reference = datetime.datetime.now() - datetime.timedelta(
            seconds=conf.timeline_db_period())
        self.c.execute('DELETE FROM timeline WHERE created < ?', (reference,))

    def open(self):
        timeline_db_file = conf.timeline_db_file()
        db_exist = os.path.isfile(timeline_db_file)
        self._open_sqlite3(timeline_db_file)
        if not db_exist:
            self.c.execute(
                '''CREATE TABLE timeline (
                tw_id TEXT,
                tw_link TEXT,
                tw_header TEXT,
                tw_pubdate TEXT,
                tw_title TEXT,
                tw_text TEXT,
                images_json TEXT,
                created TIMESTAMP)''')
            self.c.execute('CREATE INDEX timeline_index ON timeline(created)')

    def close(self):
        self._clear_old_db_data()
        self.conn.commit()
        self.c.close()
        self.c = None
        self.conn.close()
        self.conn = None

    def add_item(self, item, created):
        id = item['id']
        link = item['link']
        header = item['header']
        pubdate = item['pubdate']
        title = item['title']
        text = item['text']
        images_json = json.dumps(item['images'])
        self.c.execute(
            '''INSERT INTO timeline(
            tw_id, tw_link, tw_header, tw_pubdate, tw_title, tw_text,
            images_json, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (id, link, header, pubdate,
                                                 title, text, images_json,
                                                 created))

    def prepare_get_items(self):
        self.c.execute('SELECT * FROM timeline ORDER BY created DESC')

    def get_item(self):
        r = self.c.fetchone()
        if r is not None:
            item = {}
            item['id'] = r['tw_id']
            item['link'] = r['tw_link']
            item['header'] = r['tw_header']
            item['pubdate'] = r['tw_pubdate']
            item['title'] = r['tw_title']
            item['text'] = r['tw_text']
            item['images'] = json.loads(r['images_json'])
            return item
        else:
            return None


timeline_db = TimelineDb()
