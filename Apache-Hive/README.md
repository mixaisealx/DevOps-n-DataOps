# Hive Transactions Analysis

## Project Overview

This repository contains solutions for 5 tasks involving the analysis of **cash register transaction data** using **Apache Hive**.

The data comes from the automated system of the Federal Tax Service for monitoring the use of cash register equipment. All transactions are stored in **JSON format** in HDFS, with each line representing a single transaction.

The project demonstrates working with JSON data, creating Hive tables in multiple formats, calculating transaction sums, analyzing profits by time of day, and detecting violations of transaction order according to Law.

## Input Data

- Data path: `/data/hive/fns2`
- JSON fields in transactions:
  - `kktRegId` - unique transaction identifier
  - `userInn` - taxpayer’s ID
  - `subtype` - transaction type (`receipt`, `openShift`, `closeShift`)
  - `totalSum` - transaction amount (for `receipt`)
  - `dateTime` - transaction date and time

Some fields may be missing or have a `null` value.

## Completed Tasks

### Task 1: Hive Table Creation

In this task, a **Hive database and table** were created to store transactions with JSON fields mapped to table columns.
- Extracted key fields: `kktRegId`, `userInn`, `subtype`, `totalSum`, `dateTime`, among others.
- For nested JSON objects, values were stored as strings if extraction was not possible.
- **Result:** successfully retrieved the first 50 rows from the table with all columns correctly populated.

### Task 2: Comparing Data Storage Formats

For performance analysis:
- Three additional Hive tables were created in **Text**, **ORC**, and **Parquet** formats using `CREATE TABLE AS SELECT`.
- Executed a query to find the **taxpayer with the highest total transaction amount** for `receipt` transactions.
- Measured query execution times for different data storage formats.

#### Results

| Data Storage Format | Query Execution Time |
| :-: | :- |
| TEXTFILE | 1 minutes 36 seconds 680 msec |
| ORC | 45 seconds 780 msec |
| PARQUET | 1 minutes 40 seconds 410 msec |

### Task 3: Most Profitable Day

A query was implemented to determine, for **each taxpayer**, the day of the month with the **highest total transaction profit**.
- Only transactions with `subtype = 'receipt'` were considered.
- Dates were extracted from the `dateTime` field.
- **Result:** a table `<UserINN> <day of month> <profit>` sorted in ascending order of UserINN.

### Task 4: Comparing Profit by Time of Day

A query was implemented to identify taxpayers whose **average profit per transaction in the morning (before 13:00)** was higher than in the **afternoon (after 13:00)**.
- Average `totalSum` was calculated for each half of the day.
- Results were rounded to integers and sorted by morning profit.
- **Result:** a table `<UserINN> <morning profit> <afternoon profit>` limited to 50 rows.

### Task 5: Detecting Transaction Order Violations

To identify taxpayers violating transaction order according to Law:
- Periods between `closeShift` and `openShift` were determined for each transaction.
- `receipt` transactions occurring outside the correct order (before the first opening, after the last closing, or between close and open) were identified.
- **Result:** a list of UserINN of violators, sorted by UserINN and limited to 50 rows.

## Requirements

To run the Hive queries and reproduce the results in this repository, the following software and components are required:

1. **Apache Hive** (version 3.x or compatible)
	- Used for creating databases, tables, and executing SQL queries over HDFS data.
	- Supports advanced features such as `STRUCT` and `MAP` column types, external tables, and dynamic partitions.
2. **Hadoop / HDFS** (version 3.x or compatible)
3. **Cloudera Distribution (CDH)**
	- Required to provide Hive and Hadoop services, including the locations of Cloudera parcels used in the project.
4. **Hive JSON SerDe**
	- `json-serde-1.3.8-jar-with-dependencies.jar` is required for parsing JSON-formatted transaction data in Hive tables.
5. **Hive Contrib Library**
	- `hive-contrib.jar` is included to support additional Hive functions.
6. **Java Runtime Environment (JRE)**
	- Version 8 or higher is required to run Hive and Hadoop services.
7. **Linux-based environment**
	- Recommended for compatibility with Hive, Hadoop, and Cloudera parcels.
