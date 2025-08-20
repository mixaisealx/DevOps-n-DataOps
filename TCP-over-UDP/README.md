# Reliable UDP Delivery Protocol

A consistency-preserving protocol has been implemented that emulates TCP functionality while operating over UDP.

The protocol implementation is provided in the class `MyTCPProtocol` within the file `protocol.py`.

A corresponding test suite has been developed to validate the implementation. The protocol is expected to successfully pass all provided tests.

For testing, execute `test.sh` inside a Docker container. All required Python dependencies are specified in the `requirements.txt` file.

> **Note:** When using Docker for Windows in conjunction with WSL, simulated network constraints may not function as intended. In such cases, even a naive implementation may pass the majority of tests. A workaround is described [here](https://github.com/imunes/imunes/issues/111).

```
docker compose up --build
```

## Protocol Configuration Parameters

The **`MyTCPProtocol`** class (defined in [`protocol.py`](protocol.py)) implements a TCP-like reliable delivery layer over UDP.
Several internal parameters control how data is segmented, transmitted, and buffered. These hyperparameters can be adjusted in the constructor (`__init__`) of `MyTCPProtocol`.

### mtu_payload

- **Defined in:** `protocol.py -> MyTCPProtocol.__init__`
- **Default:** `1428` bytes
- **Description:**
  The maximum payload size per UDP packet.
  Derived from an assumed UDP MTU (`1432` bytes) minus 4 bytes reserved for the sequence number header.
- **Impact:**
	- Larger values: fewer packets, more efficient but higher loss impact.
	- Smaller values: more resilient to loss but higher overhead.

### multiplier

- **Defined in:** `protocol.py -> MyTCPProtocol.__init__`
- **Default:** `82`
- **Description:**
  Factor used to calculate the **sender window size**.
  This value limits the maximum number of unacknowledged bytes that can be in flight at once.
- **Impact:**
	- Higher values: better throughput on high-latency/high-bandwidth networks.
	- Lower values: smaller memory footprint, but may limit throughput.

### window_slots

- **Defined in:** `protocol.py -> MyTCPProtocol.__init__`
- **Default:** `82`
- **Description:**
  Factor used to calculate the **receiver window size**.
  This defines how much out-of-order data the receiver can buffer before dropping new packets.
- **Impact:**
	- Higher values: more tolerant to packet reordering, requires more memory.
	- Lower values: lower memory usage, but increased chance of drops under reordering.
