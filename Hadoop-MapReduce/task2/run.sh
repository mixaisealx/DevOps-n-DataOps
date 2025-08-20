#!/usr/bin/env bash

OUT_DIR="err_plug_stat_result"
NUM_REDUCERS=8

hdfs dfs -rm -r -skipTrash ${OUT_DIR}* > /dev/null

yarn jar /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="err_plug_stat_stage_1" \
    -D mapreduce.job.reduces=${NUM_REDUCERS} \
    -files mapper.py,reducer.py \
    -mapper "python3 mapper.py" \
    -combiner "python3 reducer.py" \
    -reducer "python3 reducer.py" \
    -input /data/minecraft-server-logs \
    -output ${OUT_DIR}.tmp > /dev/null

yarn jar /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -D mapreduce.job.name="err_plug_stat_stage_2" \
    -D mapreduce.job.reduces=1 \
    -D stream.num.map.output.key.fields=2 \
    -D mapreduce.job.output.key.comparator.class=org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator \
    -D mapreduce.partition.keycomparator.options="-k2,2nr -k1,1r" \
    -files mapper_dummy.py,reducer_dummy.py \
    -mapper "python3 mapper_dummy.py" \
    -reducer "python3 reducer_dummy.py" \
    -input ${OUT_DIR}.tmp \
    -output ${OUT_DIR} > /dev/null


# Checking result
hdfs dfs -cat ${OUT_DIR}/part-00000 2>/dev/null | head -10

