#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import jinja2
import json
import os
import re
import sys
import shutil
from common import conf, logger
from url_db import url_db
from timeline_db import timeline_db

RSS_TITLE = 'twimg2rss'
RSS_DESC = 'Images in my Twitter home timeline'
RSS_TEMPLATE_J2_FILE = 'twimg2rss.xml.j2'


def delete_duplicate(url_expurl_dic):
    urls = url_expurl_dic.values()
    for url in urls:
        if url_db.url_in_db(url):
            logger.debug('delete by duplicate URL: {0}'.format(url))
            return False

    now = datetime.datetime.now()
    for url in urls:
        url_db.add_url(url, now)

    return True


def retweet_count_check(tweet):
    if 'retweeted_status' in tweet:
        favorite_count = tweet['retweeted_status']['favorite_count']
        #logger.debug('favorite_count: {0}'.format(favorite_count))
        if favorite_count < conf.minimum_retweet_favorites():
            return False

    return True


def ng_word_check(tweet, url_expurl_dic):
    values = url_expurl_dic.values()
    user = tweet['user']
    at_username = '@' + user['screen_name']
    nickname = user['name']
    for ngw in conf.ng_word_list():
        if ngw in tweet['text'] or ngw in at_username or ngw in nickname:
            logger.debug('delete by NG word in text: {0}'.format(ngw))
            return False
        for v in values:
            if ngw in v:
                logger.debug('delete by NG word in URL: {0}'.format(ngw))
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
    if 'retweeted_status' in tweet:
        item['text'] = '[{0}] {1}'.format(tweet['retweeted_status']['favorite_count'], tweet['text'])
    else:
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
    url_db.open()
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

        if len(media_urls_list) > 0 and \
            ng_word_check(tweet, url_expurl_dic) and \
            retweet_count_check(tweet) and \
            delete_duplicate(url_expurl_dic):
            create_media_timeline_item(media_timeline_list,
                                       tweet, media_urls_list, url_expurl_dic)

    url_db.close()

    return max_parsed_id, newest_created_at, tl_count


def create_rss_xml_items(media_timeline_list):
    tmpl = jinja2.Template('{{ text }}', autoescape=True)
    for item in media_timeline_list:
        rss_xml_item = {}
        rss_xml_item['id'] = item['id']
        rss_xml_item['link'] = 'https://twitter.com/{0}/status/{1}'.format(
            item['screen_name'], item['id'])
        header_name = '<a href=\'https://twitter.com/{0}\'>{1}</a>'.format(
            item['screen_name'], tmpl.render(text=item['name']))
        created = item['created_at'] + datetime.timedelta(
                                 hours=conf.time_difference_from_utc())
        dt = '{0:%Y/%m/%d %H:%M:%S}'.format(created)
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
        timeline_db.add_item(rss_xml_item, created)


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

    if not os.path.isfile(conf.timeline_json_file()):
        logger.info('obtained raw timeline count = ZERO')
        return 0

    with open(conf.timeline_json_file(), 'r') as file:
        req_text0 = file.read()

    req_text = re.sub(r',$',']', req_text0)

    media_timeline_list = []
    max_parsed_id, newest_created_at, tl_count = parse_timeline(
        req_text, media_timeline_list)
    if max_parsed_id == 0:
        return 0

    mt_count = len(media_timeline_list)

    timeline_db.open()
    create_rss_xml_items(media_timeline_list)

    rss_xml_items = []
    timeline_db.prepare_get_items()
    for i in range(conf.rss_xml_limit()):
        item = timeline_db.get_item()
        if item is None:
            break
        rss_xml_items.append(item)

    timeline_db.close()

    with open(conf.rss_xml_file(), 'w') as file:
        create_rss_xml(rss_xml_items, tmpl, newest_created_at, file)

    logger.info('max_parsed_id = {0}'.format(max_parsed_id))
    logger.info('newest_created_at = {0:%Y/%m/%d %H:%M:%S}'.format(
        newest_created_at))
    logger.info('obtained raw timeline count = {0}'.format(tl_count))
    logger.info('added media timeline count  = {0}'.format(mt_count))
    logger.info('total media timeline count  = {0}'.format(len(rss_xml_items)))

    return mt_count


def main():
    make_xml()


if __name__ == '__main__':
    main()
    sys.exit(0)
