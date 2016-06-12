#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import sys
from requests_oauthlib import OAuth1Session
from common import conf, logger


def get_max_parsed_id():
    try:
        with open(conf.max_parsed_id_file(), 'r') as file:
            id_str = file.read()
    except FileNotFoundError:
        id_str = '0'

    if len(id_str) == 0:
        id_str = '0'

    return int(id_str)


def put_max_parsed_id(id):
    with open(conf.max_parsed_id_file(), 'w') as file:
        file.write('{0}\n'.format(id))


def get_timeline():
    url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'

    params = {'count': 200}
    max_parsed_id = get_max_parsed_id()
    if max_parsed_id > 0:
        params.update({'since_id': max_parsed_id})

    twitter = OAuth1Session(conf.tw_consumer_key(),
                            conf.tw_consumer_secret(),
                            conf.tw_access_token(),
                            conf.tw_access_token_secret())
    req = twitter.get(url, params=params)

    if req.status_code == 200:
        current_tl_json = req.text
        timeline = json.loads(current_tl_json)
        tweets_count = len(timeline)
        if tweets_count > 0:
            top = timeline[0]
            max_parsed_id = top['id']

            try:
                with open(conf.timeline_json_file(), 'r') as file:
                    old_tl_json = file.read()
                    new_tl_json = current_tl_json[:-1] + ',' + old_tl_json[1:]
            except FileNotFoundError:
                new_tl_json = current_tl_json

            with open(conf.timeline_json_file(), 'w') as file:
                file.write(new_tl_json.strip())

            put_max_parsed_id(max_parsed_id)

        logger.info('Number of tweets: {0}'.format(tweets_count))
        if 'x-rate-limit-remaining' in req.headers:
            limit = req.headers['x-rate-limit-remaining']
            logger.info('API remain: {0}'.format(limit))
        if 'x-rate-limit-reset' in req.headers:
            reset = req.headers['x-rate-limit-reset']
            utc = datetime.datetime.utcfromtimestamp(int(reset))
            logger.info(
                'API reset: {0:%a, %d %b %Y %H:%M:%S +0000}'.format(utc))

        return True

    else:
        logger.info('HTTP Status Code: {0}'.format(req.status_code))
        return False


def main():
    get_timeline()


if __name__ == '__main__':
    main()
    sys.exit(0)
