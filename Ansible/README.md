# Ansible Role: Nginx + Service State Cron

## Overview

This role sets up a server to run **nginx** and a cron job that maintains a JSON file (`/opt/service_state.json`) with service state information, including nginx uptime. It ensures packages are installed, configuration is deployed, services are running, and the JSON file stays consistent with a local template.

## Supported Platforms

| OS Family | Preparation Details |
| :- | :- |
| **CentOS / RHEL** | Installs `epel-release` and sets cron variables (`cron_package_name=cronie`, `cron_service_name=crond`). |
| **Arch Linux** | Sets cron variables (`cron_package_name=cronie`, `cron_service_name=cronie`). |
| **Debian / Ubuntu / Other Linux** | Uses default package manager for `nginx`, `jq`, and cron. No additional preparation required. |

> The role automatically detects the OS and runs the appropriate preparation tasks.

## Role Functionality

1. **Prepare the host**
	- Runs OS-specific preparation tasks (if applicable).
	- Sets variables required for cron service installation and management.

2. **Install required packages**
	- Installs `nginx`, `jq`, and the OS-appropriate cron package.

3. **Deploy nginx configuration**
	- Copies a predefined configuration to serve `/opt/service_state.json` at `/service_data`.
	- All other requests return 404.
	- Reloads nginx if the configuration changes.

4. **Manage service state**
	- Checks the remote `/opt/service_state.json` `.title` field.
	- Overwrites the file only if the title differs from the local template.

5. **Ensure services are running**
	- Starts and enables `nginx` and the cron service.

6. **Set up cron job**
	- Updates the `uptime` field in `/opt/service_state.json` based on nginx uptime.

## Files

- `playbook.yml` - Main playbook to run the role
- `server_setup/tasks/main.yml` - Main tasks sequence
- `server_setup/tasks/prepare_centos.yml` - CentOS/RHEL preparation tasks
- `server_setup/tasks/prepare_arch.yml` - Arch Linux preparation tasks
- `server_setup/files/deploy_nginx.conf` - Nginx configuration
- `server_setup/files/service_state.json` - Local template for service state
- `server_setup/handlers/main.yml` - Handlers (e.g., nginx restart)
- `server_setup/defaults/main.yml` - Default variables for cron and packages
- `server_setup/tests/` - Test inventory and playbook

## Usage

```bash
ansible-playbook -i server_setup/tests/inventory playbook.yml
```

The role automatically detects the OS and applies the correct preparation steps.

## Notes

- Idempotent: running multiple times does not cause unnecessary changes.
- Only the `.title` field is checked to decide whether to overwrite the service state file.
