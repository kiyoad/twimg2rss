#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import jinja2
import json
import os
import sqlite3
import sys
import shutil
from common import conf, logger

RSS_TITLE = 'twimg2rss'
RSS_DESC = 'Images in my Twitter home timeline'
RSS_TEMPLATE_J2_FILE = 'twimg2rss.xml.j2'


def _open_sqlite3(url_db_file):
    conn = sqlite3.connect(
        url_db_file,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    return conn, c


def open_url_db():
    url_db_file = conf.url_db_file()
    if os.path.isfile(url_db_file):
        conn, c = _open_sqlite3(url_db_file)

    else:
        conn, c = _open_sqlite3(url_db_file)
        c.execute('CREATE TABLE urls (url TEXT, updated TIMESTAMP)')
        c.execute('CREATE INDEX url_index ON urls(url, updated)')

    return conn, c


def close_url_db(conn, c):
    c.close()
    conn.close()


def url_in_db(url, c):
    c.execute('SELECT * FROM urls WHERE url == ?', (url,))
    return c.fetchone() is not None


def add_url_to_db(url, updated, c):
    c.execute('INSERT INTO urls(url, updated) VALUES (?, ?)', (url, updated))


def clear_old_db_data(c):
    reference = datetime.datetime.now() - datetime.timedelta(
        seconds=conf.url_db_period())
    c.execute('DELETE FROM urls WHERE updated < ?', (reference,))


def delete_duplicate(url_expurl_dic, c):
    urls = url_expurl_dic.values()
    for url in urls:
        if url_in_db(url, c):
            logger.info('delete duplicate URL: {0}'.format(url))
            return False

    now = datetime.datetime.now()
    for url in urls:
        add_url_to_db(url, now, c)

    return True


def ng_word_check(tweet, url_expurl_dic):
    values = url_expurl_dic.values()
    for ngw in conf.ng_word_list():
        if ngw in tweet['text']:
            return False
        for v in values:
            if ngw in v:
                return False

    return True


def create_media_timeline_item(media_timeline_list,
                               tweet, media_urls_list, url_expurl_dic):
    item = {}
    item['id'] = tweet['id']
    item['created_at'] = datetime.datetime.strptime(
        tweet['created_at'],
        '%a %b %d %H:%M:%S +0000 %Y')
    user = tweet['user']
    item['name'] = user['name']
    item['screen_name'] = user['screen_name']
    item['text'] = tweet['text']
    item['media_urls'] = media_urls_list
    item['url_expurl_dic'] = url_expurl_dic
    media_timeline_list.append(item)


def parse_media_entities(entities, media_urls_list, url_expurl_dic):
    if 'media' in entities:
        medias = entities['media']
        for media in medias:
            if media['type'] == 'photo':
                media_urls_list.append(media['media_url'])
                url_expurl_dic[media['url']] = media['expanded_url']


def parse_urls_entities(entities, url_expurl_dic):
    if 'urls' in entities:
        urls = entities['urls']
        for url in urls:
            url_expurl_dic[url['url']] = url['expanded_url']


def parse_timeline(req_text, media_timeline_list):
    timeline = json.loads(req_text)
    tl_count = len(timeline)
    max_parsed_id = 0
    newest_created_at = datetime.datetime.now()
    conn, c = open_url_db()
    for tweet in timeline:
        if max_parsed_id == 0:
            max_parsed_id = tweet['id']
            newest_created_at = datetime.datetime.strptime(
                tweet['created_at'],
                '%a %b %d %H:%M:%S +0000 %Y')

        media_urls_list = []
        url_expurl_dic = {}
        if 'extended_entities' in tweet:
            parse_media_entities(tweet['extended_entities'], media_urls_list,
                                 url_expurl_dic)
        else:
            parse_media_entities(tweet['entities'], media_urls_list,
                                 url_expurl_dic)
        parse_urls_entities(tweet['entities'], url_expurl_dic)

        if len(media_urls_list) > 0 and ng_word_check(
                tweet, url_expurl_dic) and delete_duplicate(url_expurl_dic, c):
            create_media_timeline_item(media_timeline_list,
                                       tweet, media_urls_list, url_expurl_dic)

    clear_old_db_data(c)
    conn.commit()
    close_url_db(conn, c)

    return max_parsed_id, newest_created_at, tl_count


def create_rss_xml_items(media_timeline_list, rss_xml_items):
    tmpl = jinja2.Template('{{ text }}', autoescape=True)
    for item in media_timeline_list:
        rss_xml_item = {}
        rss_xml_item['id'] = item['id']
        rss_xml_item['link'] = 'https://twitter.com/{0}/status/{1}'.format(
            item['screen_name'], item['id'])
        header_name = '<a href=\'https://twitter.com/{0}\'>{1}</a>'.format(
            item['screen_name'], tmpl.render(text=item['name']))
        dt = '{0:%Y/%m/%d %H:%M:%S}'.format(
            item['created_at'] + datetime.timedelta(
                hours=conf.time_difference_from_utc()))
        rss_xml_item['header'] = '{0} @{1} {2}'.format(
            header_name, item['screen_name'], dt)
        rss_xml_item['pubdate'] = '{0:%a, %d %b %Y %H:%M:%S +0000}'.format(
            item['created_at'])
        if len(item['text']) > 64:
            title_text = item['text'][:64] + '...'
        else:
            title_text = item['text']
        rss_xml_item['title'] = tmpl.render(text=title_text)
        main_text = tmpl.render(text=item['text'])
        for k, v in item['url_expurl_dic'].items():
            main_text = main_text.replace(
                k, '<a href=\'{0}\'>{0}</a>'.format(v))
        rss_xml_item['text'] = main_text
        rss_xml_item['images'] = item['media_urls']
        rss_xml_items.append(rss_xml_item)


def create_rss_xml(rss_xml_items, tmpl, newest_created_at, file):
    file.write(tmpl.render(
        rss_title=RSS_TITLE,
        rss_link=conf.rss_xml_url(),
        home_link=conf.homepage_url(),
        rss_desc=RSS_DESC,
        utc='{0:%a, %d %b %Y %H:%M:%S +0000}'.format(newest_created_at),
        builddate='{0:%a, %d %b %Y %H:%M:%S +0000}'.format(
            datetime.datetime.utcnow()),
        items=rss_xml_items))


def make_xml():
    scrpt_abs_path_dir = os.path.abspath(os.path.dirname(__file__))
    jinja2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(scrpt_abs_path_dir, encoding='utf8'),
        autoescape=True)
    tmpl = jinja2_env.get_template(RSS_TEMPLATE_J2_FILE)

    with open(conf.timeline_json_file(), 'r') as file:
        req_text = file.read()

    media_timeline_list = []
    max_parsed_id, newest_created_at, tl_count = parse_timeline(
        req_text, media_timeline_list)
    if max_parsed_id == 0:
        return

    mt_count = len(media_timeline_list)

    rss_xml_items = []
    create_rss_xml_items(media_timeline_list, rss_xml_items)

    with open(conf.rss_xml_file(), 'w') as file:
        create_rss_xml(rss_xml_items, tmpl, newest_created_at, file)

    logger.info('max_parsed_id = {0}'.format(max_parsed_id))
    logger.info('newest_created_at = {0:%Y/%m/%d %H:%M:%S}'.format(
        newest_created_at))
    logger.info('total timeline count = {0}'.format(tl_count))
    logger.info('media timeline count = {0}'.format(mt_count))

    if mt_count > 0:
        log_timeline_json_file = '{0}/timeline_{1:%Y%m%d-%H%M%S}.json'.format(
            conf.log_timeline_json_dir(), datetime.datetime.now())
        shutil.move(conf.timeline_json_file(), log_timeline_json_file)
        shutil.copy(conf.rss_xml_file(), conf.release_rss_xml_file())
    else:
        logger.info('No update: {0}'.format(conf.release_rss_xml_file()))


def main():
    make_xml()


if __name__ == '__main__':
    main()
    sys.exit(0)
