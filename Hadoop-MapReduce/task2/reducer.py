#!/usr/bin/env python3

import sys

current_key = None
sum_count = 0

for line in sys.stdin:
    try:
        key, count = line.split('\t', 1)
        count = int(count)
    except ValueError as e:
        continue
    if current_key != key:
        if current_key:
            print("{0}\t{1}".format(current_key, sum_count))
        sum_count = 0
        current_key = key
    sum_count += count

if current_key:
    print("{0}\t{1}".format(current_key, sum_count))

