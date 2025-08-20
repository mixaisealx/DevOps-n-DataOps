#!/usr/bin/env python3

import sys

current_key = None
sum_count = 0
sum_proper = 0
for line in sys.stdin:
    try:
        key, count, proper = line.split('\t', 2)
        count = int(count)
        proper = int(proper)
    except ValueError as e:
        continue
    if current_key != key:
        if current_key and sum_count == sum_proper:
            print("{0}\t{1}".format(current_key, sum_count))
        sum_count = 0
        sum_proper = 0
        current_key = key
    sum_count += count
    sum_proper += proper

if current_key and sum_count == sum_proper:
    print("{0}\t{1}".format(current_key, sum_count))

