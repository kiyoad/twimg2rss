#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from get_timeline import get_timeline
from make_xml import make_xml
from release_xml import release_xml
from backup_timeline_json import backup_timeline_json


def main():
    get_timeline()
    media_timeline_count = make_xml()
    release_xml(media_timeline_count)
    backup_timeline_json()


if __name__ == '__main__':
    main()
    sys.exit(0)
