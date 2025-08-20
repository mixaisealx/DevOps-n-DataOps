# MapReduce Solutions

This repository contains solutions for two Hadoop MapReduce tasks: **Task 1 (Wikipedia Analysis)** and **Task 2 (Log Analysis)**.

## Repository Structure

**Directories:**
- `task1` - solution for Task 1 (Wikipedia)
- `task2` - solution for Task 2 (Log Analysis)
  
**Execution:**

Running `run.sh` executes the solution and outputs results to HDFS (and partially to STDOUT).

## Task 1 - Wikipedia Proper Names Frequency

**Objective:**
Count occurrences of proper names with 6 to 9 characters. A proper name is defined as a word that starts with an uppercase letter followed by lowercase letters, and that never appears in the text starting with a lowercase letter.

**Input Data:**
- Path on the cluster: `/data/wiki/en_articles`
- Format: `article_id <tab> article_text`

**Output:**
- **HDFS:** `name count`
- **STDOUT:** top 10 names, sorted by decreasing count; ties sorted lexicographically.

**Example Output:**

```
english 8358
states  7264
british 6829
...
```

**Processing Notes:**
- Remove punctuation from words.
- Convert results to lowercase before output.

## Task 2 - Log Analysis

**Objective:**
Analyze server logs to identify which Java classes generate the most errors. This helps the server admin identify problematic modules.

**Input Data:**
- Path on HDFS: `/data/system-server-logs`
- Log format:
```
[YYYY-MM-dd.HH:mm:ss] [Thread name/SEVERITY]: Message
```
- Messages include regular events, warnings (WARN), plugin events, and errors (ERROR). Errors may span multiple lines (stacktrace).

**Processing Rules:**

- Ignore errors without a stacktrace.
- Only consider the **lowest entry** in the stacktrace (most informative) to identify the initiating class.
- Ignore line numbers and file names.
- Stacktrace is read **from bottom to top**.

**Output format**:

```
JavaClass<TAB>ErrorCount
```
- Sorted by error count in descending order.

**Example Output:**

```
org.bukkit.plugin.java.JavaPluginLoader.getPluginDescription    20
java.lang.Thread.run                                           11
```

## Running the Solutions

```bash
git clone <repo-url>
cd task1  # or task2
./run.sh
```

## Technologies

- **Hadoop with YARN**
  - Hadoop Streaming must be available (tested with Cloudera CDH).
  - Java runtime required for Hadoop/YARN.
- **Python 3**
  - For executing mapper and reducer scripts.
  - Must be installed on all cluster nodes.
- **Bash / Shell**
  - For executing `run.sh` scripts.
- **HDFS Command Line Tools**
  - For interacting with input/output data: `hdfs dfs -ls`, `hdfs dfs -rm`, `hdfs dfs -cat`.
- **Optional / Configurable**
  - Ability to configure the number of reducers per job (`-D mapreduce.job.reduces`).
  - Access to YARN memory and CPU settings for large datasets.
