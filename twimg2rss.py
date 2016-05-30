#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import get_timeline
import make_xml


def main():
    get_timeline.get_timeline()
    make_xml.make_xml()

if __name__ == '__main__':
    main()
    sys.exit(0)
