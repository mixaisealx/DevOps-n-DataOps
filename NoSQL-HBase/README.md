# HBase + Spark + HappyBase

**In short:** this project takes game match logs (CSV) from HDFS, processes them with PySpark, and writes the results into HBase (writer). A client program (reader) then queries HBase and, for a given rectangular region on the map, outputs the **TOP-10 weapons** used for kills, grouped **per match**.

## Repository structure

```
.
├── writer/
│   ├── writer.py          # writer code
│   └── run.sh             # script for running
├── reader/
│   ├── reader.py          # reader code
│   └── run.sh             # script for running
└── README.md              # this file
```

## Solution architecture

1. **Writer (processor)**
   - Implemented in *Python + PySpark + HappyBase*.
   - Reads CSV log files from HDFS (`/data/logs/...`), parses them, converts coordinates, and generates a row key for HBase.
   - Creates an HBase table (if not present) and inserts records (using batched puts inside each partition).
   - The goal: store data so that scanning by X coordinate and filtering by Y is efficient.

2. **Reader (client)**
   - Implemented in *Python + HappyBase*.
   - Takes CLI arguments: `x_min y_min x_max y_max`.
   - Runs an HBase `scan` on the row key range (X) and applies a `SingleColumnValueFilter` for Y.
   - Groups results by `match_id`, counts weapon frequencies, selects top-10, and prints them.


### HBase schema

Table: `task_test` (hardcoded in the scripts).

Column families:
- `locationY` - stores the Y coordinate (as a formatted string). Used for filtering by Y range.
- `match` - stores `match_id`.
- `weapon` - stores `killed_by` (weapon type).

**Row key (string):** derived from `killer_position_x`:

- Format: `"{int_part}{flag}"` padded with `zfill(8)`.
- `flag` is to implement the behaviors "equal", "less-equal", "greater-equal". Example: `0000012a`, `0000234z`.

**Stored Y values:** same encoding, stored under the column family `locationY`.

## Requirements

- **Python 2.7**
- PySpark (Yarn mode)
- HappyBase + Thrift
- HBase cluster with Thrift server available

## Usage examples

1. Before running the scripts, make sure to set the in-script constants correctly (`HOSTS`, `HBASE_TABLE_NAME`)
2. Run writer:
  ```bash
  bash writer/run.sh
  ```

3. Run reader:

  ```bash
  bash reader/run.sh 100 200 500 800
  ```

Sample output:

```
Match-ID: 12345 ; Top-10: "AKM"; "M416"; "Kar98k"; "S1897"; ...
Match-ID: 12346 ; Top-10: "M416"; "SCAR-L"; "AKM"; ...
```
