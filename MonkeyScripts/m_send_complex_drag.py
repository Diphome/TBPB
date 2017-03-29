#!/usr/bin/env monkeyrunner
# -*- coding: utf-8 -*-

import sys, time, os

#Hardcoded Grid_Coord:
case = []
x = 0
y = 272
for i in range(0, 8):
    for j in range(0, 6):
        case.append((x+114,y))
        x = x + 113
    y = y + 115
    x = 0

from com.android.monkeyrunner import MonkeyRunner
from com.android.monkeyrunner import monkeyrunnerExt as ext

#Set the ip of your device here.
device = MonkeyRunner.waitForConnection('192.168.1.33:5555')

eval(sys.argv[1])
