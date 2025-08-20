#!/usr/bin/env python3

import sys

last_at_content = None

def write_last_at(last_at_content):
    if last_at_content:
        print("{0}\t{1}".format(last_at_content, 1))
        last_at_content = None
    return last_at_content

for line in sys.stdin:
    line = line.rstrip()
    if line == "":
        continue

    if line[:3] == "\tat": # error message
        last_at_content = line[4:]
        last_at_content = last_at_content[:last_at_content.index('(')]
    elif line[:6] == "Caused": # required 'at' only later in stacktrace, so skip previous collected
        last_at_content = None
    else: # other like ... n more, [, etc. 
        last_at_content = write_last_at(last_at_content)

write_last_at(last_at_content)
