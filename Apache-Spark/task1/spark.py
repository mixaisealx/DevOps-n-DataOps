from pyspark import SparkContext, SparkConf

config = SparkConf().setAppName("spark_1").setMaster("yarn")
sc = SparkContext(conf=config)

def parse_edge(s):
    efrom, eto = s.split("\t") # user \t follower
    return (int(eto), int(efrom)) # v1 -> v2

def jswap(tpl):
    return (tpl[1], tpl[0])

def jrecomb(tpl):
    prev_joinkey, prev_first, prev_second = tpl[0], tpl[1][0], tpl[1][1] # (joinkey, (first, second))
    second = (prev_first, prev_joinkey)
    return (prev_second, second)
    

PRIME_PARTS_COUNT = 45
START_ID = 12
END_ID = 34

edges = sc.textFile("/data/twitter/twitter_sample.txt").map(parse_edge).partitionBy(PRIME_PARTS_COUNT).persist()

rvedges = edges.filter(lambda x: x[0] == START_ID).map(jswap)

for i in range(0,50): # 50 is max path len
    rvedges = rvedges.join(edges, PRIME_PARTS_COUNT).persist()
    if rvedges.filter(lambda x: x[1][1] == END_ID).count() > 0: # checking second (last target)
        break
    else:
        rvedges = rvedges.unpersist().map(jrecomb)

rtpl = rvedges.filter(lambda x: x[1][1] == END_ID).take(1)[0]


def tolistn(tpl):
    rslt = []
    for it in tpl:
        if isinstance(it, tuple):
            rslt.extend(tolistn(it))
        else:
            rslt.append(it)
    return rslt


result_lst = tolistn((rtpl[1][0], rtpl[0], rtpl[1][1]))

result = ",".join([str(x) for x in result_lst])

print(result)
