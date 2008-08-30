#!/usr/bin/env python

import sys
import os
from os.path import dirname, join, pardir

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.insert(0, join(dirname(__file__), pardir))


import nose
nose.main()
