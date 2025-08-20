# Jupyter Notebook Tmux Manager

## Overview

This script provides a command-line utility to **start, stop**, and **manage** multiple Jupyter Notebook servers inside isolated virtual environments (`venv`), each running in a dedicated `tmux` window.
It handles:
- Environment creation (`venv`, Jupyter installation, directories).
- Notebook process management via `tmux`.
- Tracking running instances (in `master.json` state-file).
- Cleanup the corrupted environments.

The script supports three main commands:
- `start N` - Start `N` new Jupyter notebook servers.
- `stop i` - Stop the notebook with ID `i`.
- `stop_all` - Stop all notebooks and clean up.

## Dependencies

- Python 3
- `libtmux` (Python bindings for `tmux`)
- `tmux` installed and available
- `jupyter` (installed into created virtual environments)

## File/Directory Structure

- `dir<ID>`: Per-notebook working directory, created dynamically.
	- Contains `venv/` (Python virtual environment).
	- Contains `jupyter.log` (captured Jupyter server logs).
- `master.json`: Tracks running notebooks (ID, port, token, tmux window ID).

## CLI Interface

### Usage

```bash
python main.py start N        # Start N notebooks
python main.py stop i         # Stop notebook with ID i
python main.py stop_all       # Stop all notebooks
```

### Examples

```bash
# Start 2 notebooks
python main.py start 2

# Stop notebook with ID 0
python main.py stop 0

# Stop everything
python main.py stop_all
```

## Notebook Tracking (`master.json`)

Each running notebook is stored as a dict:

```json
{
  "id": 0,
  "port": 8888,
  "token": "abcd1234ef5678...",
  "winid": "@1"
}
```

- `id`: Sequential numeric ID.
- `port`: Localhost port assigned by Jupyter.
- `token`: Access token for authentication.
- `winid`: Associated tmux window ID.
