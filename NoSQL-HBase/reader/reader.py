import happybase
import random
import time
import sys
from collections import defaultdict


def usage():
    print("Pass arguments in following format: <min X> <min Y> <max X> <max Y>")

try:
    locations = [int(val) for val in sys.argv[1:]]
except:
    usage()
    sys.exit()


if (len(locations) != 4):
    usage()
    sys.exit()

HOSTS = ["node0%01d.mydns.xz" % i for i in xrange(1, 10)]
#HOSTS = ["localhost"]

HBASE_TABLE_NAME = "task_test"

hconn = None
fails = 0

while fails < 10:
    try:
        hconn = happybase.Connection(random.choice(HOSTS))
        break
    except:
        time.sleep(2)
        fails += 1

htable = hconn.table(HBASE_TABLE_NAME)

minX = (str(locations[0]) + "a").zfill(8)
maxX = (str(locations[2]) + "b").zfill(8)

minY = (str(locations[1]) + "a").zfill(8)
maxY = (str(locations[3]) + "b").zfill(8)

data = htable.scan(row_start=minX, row_stop=maxX, filter="SingleColumnValueFilter('locationY', '', >=, 'binary:{}') AND SingleColumnValueFilter('locationY', '', <, 'binary:{}')".format(minY, maxY))

groupby = defaultdict(list)
for v in data:
    groupby[v[1][b'match:'].decode("utf-8")].append(v[1][b'weapon:'].decode("utf-8"))

hconn.close()
data = None

for v in groupby:
    lst = groupby[v]

    accum = defaultdict(int)
    for w in lst:
        accum[w] += 1

    groupby[v] = [cv[0] for cv in sorted(accum.items(), key=lambda x: x[1], reverse=True)[:10]]

for i in groupby:
    print("Match-ID: ", i, "; Top-10: ", end='')
    for w in groupby[i]:
        print('"{}"; '.format(w), end='')
    print()


