# Kafka & Spark Streaming: User Segmentation

This repository contains solution implemented with **Apache Spark Streaming** for the task: user segmentation from web logs.

This solution is built in the same way as solution `Apache-Spark/task4` (*Streaming: User Segmentation*).

## Task description

The goal is to segment web service users according to certain criteria using web log data. 
It is necessary to transfer the results of processing to Kafka topics as new data becomes available. 

Each event has the format: `user_id <tab> user_agent`

Examples:
```
f78366c2cbed009e1febc060b832dbe4    Mozilla/5.0 (Linux; Android 4.4.2; T1-701u Build/HuaweiMediaPad) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.73 Safari/537.36
62af689829bd5def3d4ca35b10127bc5    Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
```

### Required Segments

1. `seg_iphone` – users with iPhone devices
	Heuristic: `parsed_ua['device']['family'] like '%iPhone%'`
2. `seg_firefox` – users of the Firefox browser
	Heuristic: `parsed_ua['user_agent']['family'] like '%Firefox%'`
3. `seg_windows` – users of Windows OS
	Heuristic: `parsed_ua['os']['family'] like '%Windows%'`

> Users can belong to multiple segments simultaneously. Not all users need to be included in the segmentation.

Kafka topics should have the the names as segments.

### Solution

Input data path: `/data/uid_ua_100k_splitted_by_5k`

1. Create an RDD list from the files.
2. Create a `StreamingContext` with a `batch interval = 2` seconds.
3. Use `ssc.queueStream(rdds=batches)` - this **emulates** a real stream (each element in `batches` is the next batch).
4. For each line:
	- `users_mapper` parses the `user_agent` (`ua_parser.user_agent_parser.Parse`) and forms `(uid, segment_mask)` where `segment_mask` is an integer representing a bit mask of segments:
		- bit 0 (1) - firefox
		- bit 1 (2) - windows
		- bit 2 (4) - iphone
5. Within a single batch, perform `reduceByKey` with a `bitwise OR` to combine multiple records for the same `uid` within that batch.
6. `flatMap(explode_segment)` generates `(segment_name, uid)` pairs for all segments that the user belongs to in that batch.
7. `updateStateByKey(update_func)` accumulates state for each `segment_name` - the state stores `HyperLogLog(0.01)` (1% error). Each incoming `uid` is added to the HLL.
8. Send the current values counts (per segment) to the Kafka topics.
9. Print the results once at the end: when `THRESHOLD = 5` consecutive empty RDDs are detected (`empty_rdds_count >= THRESHOLD`), `print_only_at_the_end` is called to output lines:

### Output

Format:
```
segment_name <tab> count
```

Example:
```
seg_firefox    4176
seg_windows    3890
seg_iphone     2450
```

## Environment

- Python 2.x
- Apache Spark 2.x (with Streaming support)
- Java and `JAVA_HOME` configured
- Kafka + Zookeeper installed and available in the working Kafka directory
- Libraries:
  - `pyspark`
  - `ua-parser`
  - `hyperloglog`
  - `hdfs` (using `hdfs.Config().get_client()` and `client.list`)
  - `kafka`
- HDFS installed and correctly configured (the code may use `hdfs getconf` via `subprocess`)
- Commands assume brokers on `localhost:9092`

## Run

**Start services**

In **Terminal 1**:

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

In **Terminal 2**:

```bash
bin/kafka-server-start.sh config/server.properties
```

In **Terminal 3**:
1. Create topics (runs your topic-creation script): `python3 createTopics.py`
2. Run the Spark job that produces/consumes data: `spark2-submit spark.py`

### Count messages in a topic

Run the helper script:
```bash
bash countTopics.sh <topic name>
```

`countTopics.sh` wraps `kafka-console-consumer.sh` (reads `--from-beginning`), pipes the last lines and greps the line:
```
Processed a total of <N> messages
```

The number on that final line is the total messages processed/read.

Example output:
```
[2022-01-21 20:42:28,744] ERROR Error processing message, terminating consumer process:  (kafka.tools.ConsoleConsumer$)
org.apache.kafka.common.errors.TimeoutException
Processed a total of 28 messages
```

**Quick troubleshooting**

If `countTopics.sh` shows zero or no "Processed..." line:
- Ensure Zookeeper and Kafka are running (check their terminals/logs).
- Verify the topic exists:
```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
bin/kafka-topics.sh --describe --topic <topic name> --bootstrap-server localhost:9092
```
- Confirm `--bootstrap-server` host/port match your Kafka config.
