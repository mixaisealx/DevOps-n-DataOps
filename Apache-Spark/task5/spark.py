import os
import time
from time import sleep
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession

# Preparing SparkContext
from hdfs import Config
import subprocess

client = Config().get_client()
nn_address = subprocess.check_output('hdfs getconf -confKey dfs.namenode.http-address', shell=True).strip().decode("utf-8")

sc = SparkContext(master='yarn')

# Preparing base RDD with the input data
DATA_PATH = "/data/graphDFQuarter"

sqlss = SparkSession.builder.appName('sparksql_ss').master('yarn').getOrCreate()

batches = [sqlss.read.parquet(os.path.join(*[nn_address, DATA_PATH, path])).rdd for path in client.list(DATA_PATH)]

# Creating QueueStream to emulate realtime data generating
BATCH_TIMEOUT = 10 # Timeout between batch generation
ssc = StreamingContext(sc, BATCH_TIMEOUT)
dstream = ssc.queueStream(rdds=batches)


THRESHOLD = 5

empty_rdds_count = 0
printed = False

def upd_ending(rdd):
    global empty_rdds_count
    if rdd.isEmpty():
        empty_rdds_count += 1
    else:
        empty_rdds_count = 0

dstream.foreachRDD(upd_ending)

def explode_user(dct):
    tpls = []
    for fr in dct['friends']:
        tpls.append((fr, dct['user']))
    return tpls

def umapper(tpl):
    u1,u2 = tpl[1][0],tpl[1][1]
    if int(u1) < int(u2):
        return (str(u1)+'_'+str(u2)+'_'+str(tpl[0]), 1)
    else:
        return (str(u2)+'_'+str(u1)+'_'+str(tpl[0]), 1)


def unpacker(tpl):
    u1,u2 = tpl[0].split('_')[:2]
    return (str(u1)+'_'+str(u2), 1)

def print_only_at_the_end(rdd):
    global printed
    if empty_rdds_count >= THRESHOLD and not printed:
        tosort = rdd.takeOrdered(50, key=lambda x: -x[1])
        tosort = [tuple([v[1]]+v[0].split('_',2)) for v in tosort]
        rest = sorted(tosort, key=lambda x: (x[0], x[1], x[2]), reverse=True)
        for x,y,z in rest:
            print("{}\t{}\t{}".format(x,y,z))
        printed = True
    else:
        rdd.count() # Action to empty the compute-graph


def update_func(current, old):
    if old is None:
        old = 0
    return old + sum(current)

usf = dstream.map(lambda x: x.asDict()).flatMap(explode_user)

usf.join(usf) \
        .filter(lambda x: x[1][0] != x[1][1]) \
        .map(umapper) \
        .reduceByKey(lambda x,y: 1) \
        .map(unpacker) \
        .reduceByKey(lambda x,y: x+y) \
        .updateStateByKey(update_func) \
        .foreachRDD(print_only_at_the_end)

ssc.checkpoint('./checkpoint{}'.format(time.strftime("%Y_%m_%d_%H_%M_%s", time.gmtime())))  # checkpoint for storing current state

ssc.start()
while empty_rdds_count < THRESHOLD:
     time.sleep(8)

ssc.stop()
