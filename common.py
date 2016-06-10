#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from logging import FileHandler, Formatter, getLogger, DEBUG
import os


class MyConfig:
    def __init__(self):
        self.config = ConfigParser(empty_lines_in_values=False)
        self.config.read(
            os.path.abspath(os.path.dirname(__file__)) + '/config.ini')

    def tw_consumer_key(self):
        return self.config.get('DEFAULT', 'tw_consumer_key')

    def tw_consumer_secret(self):
        return self.config.get('DEFAULT', 'tw_consumer_secret')

    def tw_access_token(self):
        return self.config.get('DEFAULT', 'tw_access_token')

    def tw_access_token_secret(self):
        return self.config.get('DEFAULT', 'tw_access_token_secret')

    def max_parsed_id_file(self):
        return self.config.get('DEFAULT', 'max_parsed_id_file')

    def timeline_json_file(self):
        return self.config.get('DEFAULT', 'timeline_json_file')

    def log_timeline_json_dir(self):
        return self.config.get('DEFAULT', 'log_timeline_json_dir')

    def rss_xml_file(self):
        return self.config.get('DEFAULT', 'rss_xml_file')

    def release_rss_xml_file(self):
        return self.config.get('DEFAULT', 'release_rss_xml_file')

    def rss_xml_url(self):
        return self.config.get('DEFAULT', 'rss_xml_url')

    def homepage_url(self):
        return self.config.get('DEFAULT', 'homepage_url')

    def time_difference_from_utc(self):
        return int(self.config.get('DEFAULT', 'time_difference_from_utc'))

    def log_file(self):
        return self.config.get('DEFAULT', 'log_file')

    def ng_word_list(self):
        return self.config.get('DEFAULT', 'ng_word_list',
                               fallback='').splitlines()

    def url_db_file(self):
        return self.config.get('DEFAULT', 'url_db_file')

    def url_db_period(self):
        return int(self.config.get('DEFAULT', 'url_db_period'))

    def timeline_db_file(self):
        return self.config.get('DEFAULT', 'timeline_db_file')

    def timeline_db_period(self):
        return int(self.config.get('DEFAULT', 'timeline_db_period'))

    def rss_xml_limit(self):
        return int(self.config.get('DEFAULT', 'rss_xml_limit'))


conf = MyConfig()

log_handler = FileHandler(filename=conf.log_file())
log_handler.setFormatter(Formatter(
    fmt='%(asctime)s %(levelname)s %(module)s "%(message)s"'))
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(log_handler)
