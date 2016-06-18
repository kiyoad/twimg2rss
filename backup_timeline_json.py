#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import shutil
from common import conf


def backup_timeline_json():
    if not os.path.isfile(conf.timeline_json_file()):
        return

    log_timeline_json_file = '{0}/timeline_{1:%Y%m%d-%H%M%S}.json'.format(
        conf.log_timeline_json_dir(), datetime.datetime.now())
    shutil.move(conf.timeline_json_file(), log_timeline_json_file)
