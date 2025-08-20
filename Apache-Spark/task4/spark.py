import os
import time
from time import sleep
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from ua_parser import user_agent_parser
import hyperloglog

# Preparing SparkContext
from hdfs import Config
import subprocess

client = Config().get_client()
nn_address = subprocess.check_output('hdfs getconf -confKey dfs.namenode.http-address', shell=True).strip().decode("utf-8")

sc = SparkContext(master='yarn')

# Preparing base RDD with the input data
DATA_PATH = "/data/uid_ua_100k_splitted_by_5k"

batches = [sc.textFile(os.path.join(*[nn_address, DATA_PATH, path])) for path in client.list(DATA_PATH)]

# Creating QueueStream to emulate realtime data generating
BATCH_TIMEOUT = 2 # Timeout between batch generation
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

def users_mapper(line):
    uid,ua = line.split('\t',2)

    parsed_ua = user_agent_parser.Parse(ua)

    segment = 0
    if "firefox" in parsed_ua['user_agent']['family'].lower():
        segment += 1

    if "windows" in parsed_ua['os']['family'].lower():
        segment += 2

    if "iphone" in parsed_ua['device']['family'].lower():
        segment += 4

    return (uid, segment)

def explode_segment(tpl):
    seg = int(tpl[1])
    tags = []
    if seg & 1 != 0:
        tags.append(("seg_firefox", tpl[0]))
    if seg & 2 != 0:
        tags.append(("seg_windows", tpl[0]))
    if seg & 4 != 0:
        tags.append(("seg_iphone", tpl[0]))

    return tags

def reducer(a, b):
    return int(a) | int(b) # Bitwise OR, user from different segments among the time

def update_func(current, old):
    if old is None:
        old = hyperloglog.HyperLogLog(0.01)
    for item in current:
        old.add(item)
    return old

def print_only_at_the_end(rdd):
    global printed
    if empty_rdds_count >= THRESHOLD and not printed:
        for segment, card in rdd.map(lambda x: (x[0], len(x[1]))).sortBy(lambda x: x[1], ascending=False).collect():
            print("{}\t{}".format(segment, card))
        printed = True
    else:
        rdd.count() # Action to empty the compute-graph

dstream \
    .map(users_mapper) \
    .filter(lambda x: x[1] != 0) \
    .reduceByKey(reducer) \
    .flatMap(explode_segment) \
    .updateStateByKey(update_func) \
    .foreachRDD(print_only_at_the_end)

ssc.checkpoint('./checkpoint{}'.format(time.strftime("%Y_%m_%d_%H_%M_%s", time.gmtime())))  # checkpoint for storing current state

ssc.start()
while empty_rdds_count < THRESHOLD:
     time.sleep(0.1)

ssc.stop()
