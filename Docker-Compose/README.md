# Docker-Compose Project

## Overview

This project defines a small application stack using **Docker Compose**. It consists of three main services:
- **Database (`db`)** - a MariaDB instance initialized automatically.
- **Data filler (`filler`)** - loads CSV data into the database at startup.
- **Web application (`web`)** - a simple HTTP service that connects to the database and provides endpoints for health checks and data retrieval.

## Usage

Start the stack:
```bash
docker-compose up -d
```

## Accessing Services

- **Web application (main entrypoint)**
  Available at: [http://localhost:8000](http://localhost:8000)
  Endpoints:
  - `/health` - health check
  - `/` - returns data from the database
- **Database (optional, for debugging/admin only)**
  Accessible on host port **3306** (standard MySQL/MariaDB).
  You can connect using your favorite client with the credentials defined in `.env`.

## Notes

- Service startup order is handled automatically: the database becomes healthy first, the filler loads data, then the web application starts.
- Database data is not persisted beyond container lifecycle unless you configure a volume.
- The filler relies on the CSV file already included in the project.
