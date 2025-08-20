#!/usr/bin/env bash

OUT_DIR="proper_count_result"
NUM_REDUCERS=8

hdfs dfs -rm -r -skipTrash ${OUT_DIR}* > /dev/null

yarn jar /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="proper_count_stage_1" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -files mapper.py,combiner.py,reducer.py \
    -mapper "python3 mapper.py" \
    -combiner "python3 combiner.py" \
    -reducer "python3 reducer.py" \
    -input /data/wiki/en_articles \
    -output ${OUT_DIR}.tmp > /dev/null

yarn jar /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="proper_count_stage_2" \
    -D mapreduce.job.reduces=1 \
    -D stream.num.map.output.key.fields=2 \
    -D mapreduce.job.output.key.comparator.class=org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator \
    -D mapreduce.partition.keycomparator.options="-k2,2nr -k1,1" \
    -files mapper_dummy.py \
    -mapper "python3 mapper_dummy.py" \
    -input ${OUT_DIR}.tmp \
    -output ${OUT_DIR} > /dev/null


# Checking result
hdfs dfs -cat ${OUT_DIR}/part-00000 2>/dev/null | head -10

