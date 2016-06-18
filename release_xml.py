#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from common import conf, logger


def release_xml(media_timeline_count):
    if not os.path.isfile(conf.rss_xml_file()):
        return

    if media_timeline_count > 0:
        shutil.copy(conf.rss_xml_file(), conf.release_rss_xml_file())
    else:
        # Even if you change the rss_xml_limit come here if
        # media_timeline_count is 0.
        logger.info('No update: {0}'.format(conf.release_rss_xml_file()))
