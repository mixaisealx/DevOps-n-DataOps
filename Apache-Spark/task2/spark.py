from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType
import pyspark.sql.functions as fc

spark = SparkSession.builder.appName('spark_2').master('yarn').getOrCreate()

PRIME_PARTS_COUNT = 45
START_ID = 12
END_ID = 34

schema = StructType(fields=[ StructField("user", IntegerType(), False), StructField("follower", IntegerType(), False) ])

edges = spark.read.csv("/data/twitter/twitter_sample.txt", schema=schema, sep="\t").repartition(PRIME_PARTS_COUNT).persist()

rvedges = edges.where(edges.follower == START_ID).selectExpr("user as userc", "follower as followerc")

for i in range(0,50): # 50 is max path len
    rvedges = rvedges.join(edges, fc.col("userc") == fc.col("follower"), 'inner').persist()

    if rvedges.where(fc.col("user") == END_ID).count() > 0:
        break
    else:
        rvedges = rvedges.unpersist().select(fc.col("user").alias("userc"), fc.concat(fc.col("followerc"), fc.lit(","), fc.col("userc")).alias("followerc"))

rtpl = rvedges.where(fc.col("user") == END_ID).first().asDict()

result = rtpl["followerc"] + "," + str(rtpl["userc"]) + "," + str(rtpl["user"])

print(result)

