# DevOps, DataOps & Networking

[![License](https://img.shields.io/badge/LICENSE-Apache%202.0-green?style=flat)](/LICENSE)  [![Version](https://img.shields.io/badge/VERSION-RELEASE%201.0-green?style=flat)](https://github.com/mixaisealx/DevOps-n-DataOps)

This repository is a collection of projects and demos across different technologies: **Ansible, Docker, Hive, Spark, Hadoop, Kafka, HBase, Networking, and Jupyter**.  
Each project lives in its own folder with a dedicated `README.md` containing detailed setup and usage instructions.

## Repository Contents

| Folder | Project | Description |
|--------|---------|-------------|
| [Ansible](./Ansible) | **Ansible Role: Nginx + Service State Cron** | Installs `nginx` and a cron job that maintains `service_state`. Idempotent, OS-aware (CentOS, RHEL, Arch, Debian, Ubuntu). |
| [Apache-Hive](./Apache-Hive) | **Hive Transactions Analysis** | Hive SQL tasks on transactions: format comparison (TEXT/ORC/PARQUET), profit analysis, shift violations. |
| [Apache-Spark](./Apache-Spark) | **Spark Solutions** | BFS shortest path, collocations (NPMI), streaming user segmentation, and common friends analysis. Implemented with RDD, DataFrames, and Streaming. |
| [Docker-Compose](./Docker-Compose) | **Dockerized Web + DB Pipeline** | MariaDB database + filler service (CSV loader) + web app with `/health` and `/` endpoints. |
| [Hadoop-MapReduce](./Hadoop-MapReduce) | **MapReduce Jobs** | Hadoop streaming tasks: Wikipedia proper-name frequency and system log error analysis. |
| [Kafka](./Kafka) | **Kafka & Spark Streaming Segmentation** | Parses user agents and streams counts to Kafka topics. |
| [MitM-attack](./MitM-attack) | **Man-in-the-Middle Network Attack** | Dockerized network simulation: ARP spoofing and TCP injection by Eve to intercept requests. |
| [NoSQL-HBase](./NoSQL-HBase) | **HBase + Spark + HappyBase** | Spark job ingests game logs into HBase; CLI reader queries top-10 weapons per match within coordinates. |
| [TCP-over-UDP](./TCP-over-UDP) | **Reliable UDP Delivery Protocol** | Custom TCP-like protocol built on UDP with tunable MTU, sliding windows, and retransmission logic. |
| [Tmux-Venv-JupyterNotebook](./Tmux-Venv-JupyterNotebook) | **Jupyter Notebook Tmux Manager** | Manages multiple Jupyter servers in isolated `venv`s, each in its own `tmux` window; state tracked in `master.json`. |

## Getting Started

Clone the repository:
```bash
git clone https://github.com/mixaisealx/DevOps-n-DataOps.git
cd DevOps-n-DataOps
```

Each project can be explored individually by entering its folder and following the instructions in its `README.md`.

## Technologies Covered

- Infrastructure automation -> **Ansible, Docker Compose**
- Big Data -> **Apache Hive, Apache Spark, Hadoop MapReduce**
- Streaming -> **Kafka, Spark Streaming**
- NoSQL -> **HBase (with Spark + HappyBase)**
- Networking -> **Custom UDP protocol, MitM attack**
- Productivity tools -> **Jupyter Notebook manager with Tmux + venv**


## License

This repository is licensed under the **Apache License 2.0**.
See the [LICENSE](LICENSE) file for details.
