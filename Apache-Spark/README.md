# Spark Solutions

This repository contains solutions implemented with Apache Spark:
- shortest path search in a graph (BFS algorithm)
- text analysis and extraction of collocations using the NPMI metric
- user segmentation from web logs (Spark Streaming)
- counting common friends in streaming graph data (Spark Streaming)

## Repository structure

- **task1** – BFS (RDD API)
- **task2** – BFS (DataFrame API)
- **task3** – Collocations extraction (DataFrame API)
- **task4** – Spark Streaming: User Segmentation
- **task5** – Spark Streaming: Common Friends

## Shortest path search (BFS) - task1 & task2

### Input data

HDFS file: `/data/twitter/twitter_sample.txt`

Line format: `user_id \t follower_id`

### Description

1. Build a directed graph.
2. Find the shortest path from vertex `12` to vertex `34` using BFS.
3. Output the path in the format:
```
12,42,57,34
```

### Implementations

- **RDD API** - folder `task1`
- **DataFrame API** - folder `task2`

#### Resulting CPU times

- RDD API: 35.138 seconds
- DataFrame API: 18.86 seconds

## Collocations extraction (NPMI) - task3

### Input data

- articles: `/data/wiki/en_articles_part`
- stop words: `/data/wiki/stop_words_en-xpo6.txt`

### Description

1. Clean the text (keep only Latin characters, convert to lowercase).
2. Remove stop words.
3. Build bigrams `word1_word2`.
4. Filter bigrams (frequency at least 500).
5. Compute NPMI.
6. Output the TOP-39 bigrams by decreasing NPMI value.

#### Example output

```
roman_empire
south_africa
...
```

### Implementation

- **DataFrame API** - folder `task3`

## Streaming: User Segmentation - task4

The goal is to segment web service users according to certain criteria using web log data. Each event has the format:
`user_id <tab> user_agent`

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
8. Print the results once at the end: when `THRESHOLD = 5` consecutive empty RDDs are detected (`empty_rdds_count >= THRESHOLD`), `print_only_at_the_end` is called to output lines:

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

## Streaming: Common Friends - task5

For each user, count the number of common friends with other users. Data arrives in chunks every 10 seconds. User pairs from different batches have no common friends.

The dataset contains the following fields:
- `userId` – user identifier
- `friends` – list of the user’s friends’ IDs

### Required Result

Output **50 user pairs** with the highest number of common friends. Pairs must meet these conditions:
- Format: `common_friends userId1 userId2`
- Sorting: by number of common friends (descending), then `userId1`, then `userId2`
- Reversed pairs are considered identical, and only `userId1 < userId2` should be kept

### Solution

Input data path: `/data/graphDFQuarter`

#### Architecture
- **Spark Streaming** - used to emulate streaming batch processing.
- **RDD and DataFrame API** - used for reading and transforming data.
- **updateStateByKey** - accumulates results as new batches arrive.
- **RDD Queue (`queueStream`)** - emulates real-time data arrival.

#### Main Processing Steps

1. Transform source data into `(friend, user)` pairs.
2. Form unique user pairs who have common friends.
3. Count the number of unique common friends for each pair.
4. Accumulate results across all batches.
5. Output top user pairs with the most common friends.

#### Features
- Streaming data processing with state accumulation between batches.
- Scalable via distributed processing in Spark.
- Efficient deduplication to correctly count common friends.

### Example Output

```
1346    10541383       51640390
1334    3812683        38274136
1301    1049214        4685334
1247    49405386       56739429
1197    24170958       24248832
1186    23936386       56739429
1180    2408699        33766998
1164    16666475       52992701
```

## Environment / Software Requirements

- Python 2.x
- Apache Spark 2.x (with Streaming support)
- Libraries:
  - `pyspark`
  - `ua-parser`
  - `hyperloglog`
  - `hdfs` (using `hdfs.Config().get_client()` and `client.list`)
- HDFS installed and correctly configured (the code may use `hdfs getconf` via `subprocess`)

## Run

```bash
bash run.sh
```
