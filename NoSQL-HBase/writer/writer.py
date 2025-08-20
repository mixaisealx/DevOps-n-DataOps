from pyspark import SparkContext, SparkConf
import happybase
import random
import time

HOSTS = ["node0%01d.mydns.xz" % i for i in xrange(1, 10)]

HBASE_HOST = random.choice(HOSTS)
HBASE_TABLE_NAME = "task_test"
PRIME_PARTS_COUNT = 27


config = SparkConf().setAppName("task_filler").setMaster("yarn")
sc = SparkContext(conf=config)

hconn = happybase.Connection(HBASE_HOST)

try:
    hconn.delete_table(HBASE_TABLE_NAME, disable=True)
except:
    pass

hconn.create_table(
    HBASE_TABLE_NAME,
    {
        'locationY': dict(max_versions=1, block_cache_enabled=True),
        'match': dict(max_versions=1),
        'weapon': dict(max_versions=1)
    }
)

hconn.close()

def parse_log(s):
    data = s.split(',')
    try:
        x,y = float(data[3]),float(data[4])
    except:
        return ("<>",("<>",("<>", "<>")))

    xf = "z" if x % 1 > 0.001 else "a"
    yf = "z" if y % 1 > 0.001 else "a"

    x = "{}{}".format(int(x),xf).zfill(8)
    y = "{}{}".format(int(y),yf).zfill(8)

    return (x,(y,(data[6],data[0]))) # killer_position_x, killer_position_y, match_id, killed_by

def hbase_writer(iterator):
    fails = 0
    hconn = None
    while fails < 5:
        try:
            hconn = happybase.Connection("localhost")
            break
        except:
            time.sleep(10)
            fails += 1
    #hconn = happybase.Connection("localhost")
    htable = hconn.table(HBASE_TABLE_NAME)
    batch = htable.batch()

    for tpl in iterator:
        batch.put(tpl[0], {
            'locationY:':tpl[1][0],
            'match:':tpl[1][1][0],
            'weapon:':tpl[1][1][1]
            })
    batch.send()
    hconn.close()


def logparser(path):
    datap = sc.textFile(path).map(parse_log).filter(lambda x: x[0] != "<>").partitionBy(PRIME_PARTS_COUNT)
    datap.foreachPartition(hbase_writer)

paths = ["/data/logs/kill_match_stats_final_{}.csv".format(i) for i in range(0,5)]

for pth in paths:
    print("==== Processing: ", pth)
    logparser(pth)
