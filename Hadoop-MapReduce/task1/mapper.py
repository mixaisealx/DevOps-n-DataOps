#!/usr/bin/env python3

import sys
import re

def is_word(x):
    v = len(x)
    return v >= 6 and v <= 9

def is_proper_name(x):
    return x[0].isupper() and x[1:].islower()

for line in sys.stdin:
    splits = re.split(r"[,. !?:;'()\u2013\u00A0\[\]\-\t\\]+", line.strip())
    words = [val for val in splits if is_word(val)]
    for word in words:
        print("{0}\t{1}\t{2}".format(word.lower(), 1, int(is_proper_name(word))))

