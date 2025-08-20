from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.window import Window
import pyspark.sql.functions as fc

spark = SparkSession.builder.appName('npmi_spark_s').master('yarn').getOrCreate()

schema_data = StructType(fields=[ StructField("id", IntegerType(), False), StructField("text", StringType(), False) ])
schema_stops = StructType(fields=[ StructField("stwords", StringType(), False) ])


bowseq = spark.read.csv("/data/wiki/en_articles_part", schema=schema_data, sep="\t") \
        .select(fc.split(fc.lower(fc.regexp_replace(fc.col('text'), "^\W+|\W+$|\W*\s+\W*", " ")), " ").alias('vtext')) \
        .withColumn("artid", fc.monotonically_increasing_id()) \
        .select('artid', fc.posexplode(fc.col('vtext')).alias('order', 'words')) \
        .persist()

acount_wd2 = bowseq.select("words").distinct().count() ** 2

acount_bg = bowseq.withColumn("wordsl", fc.lag("words").over(Window.partitionBy("artid").orderBy("order"))) \
        .where(fc.col("words").isNotNull() & fc.col("wordsl").isNotNull()) \
        .select("wordsl", "words") \
        .distinct().count()

stops = spark.read.csv("/data/wiki/stop_words_en-xpo6.txt", schema=schema_stops, sep="\t")

bseqfilt = bowseq.unpersist().join(fc.broadcast(stops), fc.col("words") == fc.col("stwords"), 'left_anti').persist() 

fcount_wd = bseqfilt \
        .groupBy("words").count() \
        .selectExpr("words as lcwd_wd","count as lcwd") \
        .persist()

fcount_bg = bseqfilt.unpersist() \
        .withColumn("wordsl", fc.lag("words").over(Window.partitionBy("artid").orderBy("order"))) \
        .where(fc.col("words").isNotNull() & fc.col("wordsl").isNotNull()) \
        .groupBy("wordsl", "words").count() \
        .where(fc.col("count") >= 500) \
        .join(fcount_wd, fc.col('wordsl') == fc.col('lcwd_wd'), 'inner') \
        .selectExpr("wordsl", "words", "count as lbicount", "lcwd as lclword") \
        .join(fcount_wd.unpersist(), fc.col('words') == fc.col('lcwd_wd'), 'inner') \
        .selectExpr("wordsl", "words", "lbicount", "lclword", "lcwd as lcrword") \
        .withColumn("Pbi", fc.col("lbicount") / acount_bg) \
        .withColumn("PMI_2", fc.log2((fc.col("Pbi") * acount_wd2) / (fc.col("lclword") * fc.col("lcrword")))) \
        .withColumn("NPMI", -fc.col("PMI_2") / fc.log2(fc.col("Pbi"))) \
        .orderBy("NPMI", ascending=False) \
        .select(fc.concat(fc.col("wordsl"), fc.lit("_"), fc.col("words"))) \
        .take(39)
       

for row in fcount_bg:
    print(row[0])

