# Synapto Platform — User Guide

> **Audience:** Non-technical and basic-technical users responsible for installing, configuring, and managing the Synapto platform.

---

## Table of Contents

1. [Application Overview](#1-application-overview)
2. [Prerequisites & System Requirements](#2-prerequisites--system-requirements)
3. [Step-by-Step Installation Guide](#3-step-by-step-installation-guide)
4. [Configuration & Setup](#4-configuration--setup)
5. [Management & Daily Operations](#5-management--daily-operations)
6. [Troubleshooting & FAQ](#6-troubleshooting--faq)

---

## 1. Application Overview

### What is Synapto?

Synapto is an **automated infrastructure healing platform**. It watches your IT systems around the clock, detects problems the moment they occur, and — where possible — fixes them automatically without requiring you to wake anyone up at 3 AM.

Think of it as a tireless on-call engineer that:

- **Listens** to alerts from your existing monitoring tools (Prometheus, Datadog, CloudWatch, and others)
- **Diagnoses** the problem using a library of pre-written, human-approved runbooks
- **Executes** the right fix automatically, or escalates to a human if it cannot resolve the issue
- **Learns** from every incident, building a growing library of known fixes over time
- **Connects** to your helpdesk (ServiceNow, Jira, BMC) to log tickets automatically

### Key Benefits

| Benefit | What it means for you |
|---|---|
| **Faster resolution** | Issues that previously required a human to diagnose and fix can resolve in seconds |
| **Less alert fatigue** | Your team is only paged for truly novel or complex issues |
| **Audit trail** | Every action the platform takes is logged with who (or what) triggered it |
| **Consistent responses** | The same proven fix is applied every time, not whoever is on call that night |
| **Multi-tenant** | Multiple teams or customers can use a single installation, each with their own isolated data |

### How it Works — A Simple Example

1. Prometheus fires an alert: **"Disk usage on web-server-01 is at 94%"**
2. Synapto receives the alert via a webhook
3. It searches its knowledge library and finds a runbook: *"Free disk space by clearing old logs"*
4. It connects to `web-server-01` and runs the cleanup script
5. Disk usage drops to 42%
6. A ticket is automatically closed in ServiceNow
7. The whole event is logged so your team can review it in the morning

---

## 2. Prerequisites & System Requirements

Before you begin, make sure the following are in place.

### 2.1 Operating System

Synapto runs on any of the following Linux distributions:

| Distribution | Minimum Version |
|---|---|
| Ubuntu | 20.04 LTS or later |
| Debian | 11 (Bullseye) or later |
| Rocky Linux | 8 or later |
| CentOS / RHEL | 8 or later |

> **Windows is not supported** as a host operating system for the Synapto server. However, Synapto can manage and remediate Windows servers remotely.

### 2.2 Hardware Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8 GB or more |
| Disk | 20 GB free | 50 GB+ (logs and data grow over time) |

### 2.3 Software Requirements

You need the following software installed on the server **before** starting the installation:

#### Docker Engine (version 20.10 or later)

Docker is the container runtime that runs all Synapto services.

```bash
# Check if Docker is already installed
docker --version

# If not installed, follow Docker's official guide:
# https://docs.docker.com/engine/install/
```

#### Docker Compose V2 (version 2.0 or later)

Docker Compose orchestrates all the services together.

```bash
# Check if Docker Compose is installed
docker compose version

# Note: The command is "docker compose" (with a space), not "docker-compose"
```

#### Git

Used to download the Synapto source code.

```bash
# Check if Git is installed
git --version

# Install if missing (Ubuntu/Debian)
sudo apt-get install git -y

# Install if missing (Rocky/RHEL)
sudo dnf install git -y
```

#### curl

Used by the health-check and deployment scripts.

```bash
curl --version

# Install if missing (Ubuntu/Debian)
sudo apt-get install curl -y

# Install if missing (Rocky/RHEL)
sudo dnf install curl -y
```

### 2.4 Network Requirements

The following ports must be accessible:

| Port | Purpose | Who needs access |
|---|---|---|
| **3000** | Synapto web interface | Your team's browsers |
| **8000** | API (used by the web interface and external tools) | Internal only |
| **50051** | Remote agent communication (optional) | Only if using remote agents on other servers |

If you are behind a firewall, open ports 3000 and 8000 for inbound access from your team's network.

### 2.5 Accounts You Will Need

- **An AI provider account** (optional but highly recommended): Either [Anthropic](https://console.anthropic.com), [OpenAI](https://platform.openai.com), or Google AI. You will need an API key from one of these services to enable AI-assisted diagnostics.
- **A monitoring tool** sending alerts (Prometheus, Datadog, CloudWatch, etc.) — Synapto needs to receive webhooks from something.

---

## 3. Step-by-Step Installation Guide

### Step 1 — Download the Source Code

Open a terminal on your server and run:

```bash
git clone <your-synapto-repository-url> synapto
cd synapto
```

Replace `<your-synapto-repository-url>` with the actual Git repository URL provided to you.

### Step 2 — Create Your Configuration File

Synapto is configured using a file called `.env`. A template is provided for you:

```bash
cp .env.example .env
```

Now open the file in a text editor:

```bash
nano .env
```

You will need to fill in the values marked below. See [Section 4](#4-configuration--setup) for a full explanation of every option.

**At minimum, you must change these values:**

```
SECRET_KEY=           ← Replace with a long random string (32+ characters)
JWT_SECRET_KEY=       ← Replace with a different long random string
ENCRYPTION_KEY=       ← Replace with another long random string
ADMIN_DEFAULT_PASSWORD=   ← Set a strong password for the admin account
POSTGRES_PASSWORD=    ← Set a strong database password
REDIS_PASSWORD=       ← Set a strong Redis password
```

> **How to generate a random secret key:** Run this command in your terminal:
> ```bash
> openssl rand -hex 32
> ```
> Run it three times to get three different keys for the three secret fields above.

Save the file when done (`Ctrl+O`, then `Ctrl+X` in nano).

### Step 3 — Run the Installation

Synapto includes a deployment script that handles everything automatically:

**Ubuntu / Debian / RHEL:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Rocky Linux specifically:**
```bash
chmod +x deploy-rocky.sh
./deploy-rocky.sh
```

The script will:
- Pull all required Docker images
- Create the database and run all setup migrations
- Load the default knowledge library (pre-built runbooks and scripts)
- Start all 13 services

This process takes **5–15 minutes** depending on your internet speed and server hardware. You will see progress messages as it runs.

### Step 4 — Verify the Installation

Once the script finishes, run the health check:

```bash
./health-check.sh
```

You should see all services listed as **healthy** or **running**. A result that looks like this means everything is working:

```
✓ postgres     healthy
✓ redis        healthy
✓ api-gateway  running
✓ auth-service running
✓ frontend     running
... (all services green)
```

If any service shows as **unhealthy** or **exited**, see [Section 6 — Troubleshooting](#6-troubleshooting--faq).

### Step 5 — Access the Web Interface

Open a web browser and go to:

```
http://<your-server-ip>:3000
```

Replace `<your-server-ip>` with the IP address or hostname of the server you installed Synapto on.

You will see the Synapto login page. Log in with:
- **Username:** `admin`
- **Password:** The value you set for `ADMIN_DEFAULT_PASSWORD` in Step 2

### Step 6 — First-Time Setup in the Interface

After logging in for the first time, complete the following in the Admin panel:

1. **Change the admin password** — Go to your profile settings and set a new secure password
2. **Configure your AI provider** — Go to **Admin → AI Settings** and enter your API key
3. **Connect your monitoring tool** — Go to **Admin → Integrations** to set up your first webhook source
4. **Review the knowledge library** — Go to **Knowledge → SOPs** to see the pre-loaded runbooks

---

## 4. Configuration & Setup

All configuration is stored in the `.env` file in the root of your Synapto installation. Changes take effect when you restart the services (see [Section 5.2](#52-startingstopping-services)).

### 4.1 Core Application Settings

| Setting | Default | Description |
|---|---|---|
| `APP_ENV` | `production` | Set to `development` only for local testing — never in production |
| `APP_NAME` | `SelfHealing Application` | Display name shown in the UI |
| `DEBUG` | `false` | Set to `true` only for troubleshooting — writes verbose logs |
| `LOG_LEVEL` | `INFO` | How detailed the logs are. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### 4.2 Security Keys

These three settings are the most important. They protect all your data and authentication tokens. **They must each be unique, random, and kept secret.**

| Setting | Description |
|---|---|
| `SECRET_KEY` | Master secret for internal service communication |
| `JWT_SECRET_KEY` | Signs the login tokens issued to users |
| `ENCRYPTION_KEY` | Encrypts sensitive credentials stored in the database |

> If you ever need to rotate these keys, you will need to log all users out and re-enter any saved credentials in the admin panel.

### 4.3 Database Settings

| Setting | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `postgres` | Leave as-is when running with Docker |
| `POSTGRES_PORT` | `5432` | Leave as-is |
| `POSTGRES_DB` | `selfhealing` | The database name — leave as-is |
| `POSTGRES_USER` | `selfhealing_user` | Database username — leave as-is |
| `POSTGRES_PASSWORD` | *(must set)* | **Set a strong password — change from the default** |

### 4.4 Redis Settings

Redis is used for real-time event processing and task queues.

| Setting | Default | Description |
|---|---|---|
| `REDIS_HOST` | `redis` | Leave as-is when running with Docker |
| `REDIS_PORT` | `6379` | Leave as-is |
| `REDIS_PASSWORD` | *(must set)* | **Set a strong password — change from the default** |

### 4.5 Service Ports

These control which network ports each service listens on. You generally do not need to change these unless you have port conflicts.

| Setting | Default Port | Service |
|---|---|---|
| `API_GATEWAY_PORT` | `8000` | Main API — exposed externally |
| `INTEGRATION_LAYER_PORT` | `8001` | Receives webhooks from monitoring tools |
| `ORCHESTRATION_LAYER_PORT` | `8002` | Internal incident processing |
| `KNOWLEDGE_LAYER_PORT` | `8003` | Internal knowledge library API |
| `EXECUTION_ENGINE_PORT` | `8004` | Internal script execution |
| `LEARNING_ENGINE_PORT` | `8005` | Internal AI and analytics |

### 4.6 Execution Limits

| Setting | Default | Description |
|---|---|---|
| `MAX_EXECUTION_TIME` | `300` | Maximum seconds a remediation script can run before being killed |
| `MAX_CONCURRENT_EXECUTIONS` | `10` | Maximum number of scripts running at the same time across all incidents |

### 4.7 Frontend Settings

These control how the browser-based web interface connects to the API.

| Setting | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | The URL your users' browsers use to reach the API. **Change this to your server's public IP or domain name** |
| `VITE_WS_URL` | `ws://localhost:8000/ws` | WebSocket URL for real-time updates |

> **Important:** If you are accessing Synapto from a different machine than the server, you must change `VITE_API_URL` from `localhost` to your server's IP address or domain name, then rebuild the frontend (see [Section 5.4](#54-updating-synapto)).

### 4.8 Connecting to an AI Provider

AI is used to generate diagnostic and remediation scripts for incidents that don't have an existing runbook in the library. To enable this:

1. Go to **Admin → AI Settings** in the web interface
2. Select your provider (Anthropic Claude is recommended)
3. Paste your API key
4. Select the model
5. Click **Save**

Supported providers:
- **Anthropic Claude** — Recommended. Use model `claude-sonnet-4-6` or similar
- **OpenAI GPT** — Use model `gpt-4o` or similar
- **Google Gemini** — Use model `gemini-pro` or similar

### 4.9 Connecting Monitoring Tools

Each monitoring tool integration is configured from **Admin → Integrations** in the web interface.

Synapto accepts alerts from the following tools via webhook:

| Tool | How to connect |
|---|---|
| **Prometheus / Alertmanager** | Add Synapto's URL (`http://<server>:8001/api/v1/webhooks/prometheus`) as a receiver in your Alertmanager config |
| **Datadog** | Create a Webhook Integration in Datadog pointing to `http://<server>:8001/api/v1/webhooks/datadog` |
| **AWS CloudWatch** | Set up an SNS topic that sends notifications to Synapto's webhook endpoint |
| **Azure Monitor** | Configure an Action Group with a webhook action pointing to Synapto |
| **Zabbix** | Use Zabbix's Media Type webhook feature to send alerts to Synapto |
| **Custom / Generic** | Use the generic webhook endpoint `http://<server>:8001/api/v1/webhooks/generic` |

### 4.10 Connecting ITSM (Helpdesk) Tools

Configure these from **Admin → Integrations**. Synapto can automatically open and close tickets.

| Tool | Required information |
|---|---|
| **ServiceNow** | Instance URL, username, password |
| **Jira** | Jira URL, project key, API token |
| **BMC Remedy** | Server URL, username, password |

### 4.11 Setting Up Remote Agents

A **Remote Agent** is a small program you install on a server that Synapto needs to manage. The agent receives remediation commands from Synapto and executes them locally on that server.

Use agents when:
- The target server is not directly reachable via SSH from the Synapto server
- You want tighter security (the agent uses encrypted mutual TLS, not open SSH)
- You are managing Windows servers

**To install an agent on a remote server:**

1. Copy the `synapto-agent/` folder to the remote server
2. Run the install script:
   ```bash
   cd synapto-agent
   chmod +x install.sh
   ./install.sh
   ```
3. The agent will register itself with Synapto automatically
4. Verify it appears in **Admin → Agents** in the web interface

---

## 5. Management & Daily Operations

### 5.1 Accessing the Platform

The Synapto web interface is available at:

```
http://<your-server-ip>:3000
```

The API documentation (useful for integrations) is available at:

```
http://<your-server-ip>:8000/docs
```

### 5.2 Starting/Stopping Services

All commands are run from the Synapto installation directory.

**Start all services:**
```bash
docker compose up -d
```

**Stop all services (preserves all data):**
```bash
docker compose down
```

**Restart all services (useful after changing `.env`):**
```bash
docker compose down && docker compose up -d
```

**Restart a single service** (replace `api-gateway` with the service name):
```bash
docker compose restart api-gateway
```

**Available service names:**
`api-gateway`, `auth-service`, `admin-service`, `integration-layer`, `orchestration-layer`, `knowledge-layer`, `execution-engine`, `learning-engine`, `itsm-connector`, `agent-service`, `frontend`, `postgres`, `redis`

### 5.3 Checking Service Status

**Quick status overview:**
```bash
docker compose ps
```

**Run the built-in health check script:**
```bash
./health-check.sh
```

**View logs for all services:**
```bash
docker compose logs --tail=100
```

**View logs for a specific service:**
```bash
docker compose logs --tail=100 api-gateway
```

**Follow logs in real time:**
```bash
docker compose logs -f api-gateway
```

### 5.4 Updating Synapto

To update Synapto to a newer version:

```bash
# 1. Pull the latest code
git pull

# 2. Run the update process (rebuilds containers, runs new migrations, preserves data)
./deploy.sh --update
```

> The `--update` flag applies any new database migrations and rebuilds changed services while keeping your existing data intact.

### 5.5 Backing Up Your Data

All important data is stored in the PostgreSQL database. To back it up:

**Create a backup:**
```bash
docker compose exec postgres pg_dump -U selfhealing_user selfhealing > backup_$(date +%Y%m%d_%H%M%S).sql
```

This creates a timestamped `.sql` file in your current directory containing a full backup of all your data.

**Recommended backup schedule:**
- Run a backup daily using a cron job
- Store backups in a separate location from the server

**Example cron job** (runs daily at 2 AM):
```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/synapto && docker compose exec postgres pg_dump -U selfhealing_user selfhealing > /backups/synapto_$(date +\%Y\%m\%d).sql
```

### 5.6 Restoring from a Backup

```bash
# 1. Stop the application services (keep the database running)
docker compose stop api-gateway auth-service admin-service integration-layer orchestration-layer knowledge-layer execution-engine learning-engine itsm-connector agent-service frontend

# 2. Restore the backup
cat your-backup-file.sql | docker compose exec -T postgres psql -U selfhealing_user selfhealing

# 3. Restart everything
docker compose up -d
```

### 5.7 Managing Users

Users are managed from **Admin → Users** in the web interface.

**User roles explained:**

| Role | What they can do |
|---|---|
| **Super Admin** | Full access to everything, including user management and system settings |
| **Global Operator** | Can manage incidents, run scripts, and manage integrations — cannot manage users |
| **Global Viewer** | Read-only access to all data — cannot make changes |
| **Tenant Admin** | Full admin access within their assigned tenant only |
| **Tenant Operator** | Can operate within their tenant — cannot change tenant settings |
| **Tenant Viewer** | Read-only access within their tenant |

### 5.8 Managing the Knowledge Library

The knowledge library is where Synapto looks for proven fixes. It contains:

- **SOPs (Standard Operating Procedures)** — Step-by-step written guides for handling specific incident types
- **Scripts** — Executable code (Python, Bash, PowerShell) that can be run automatically to diagnose or fix issues
- **Playbooks** — Ordered sequences of scripts that are run together to handle a specific scenario
- **Policies** — Rules that automatically trigger a playbook when a certain type of incident occurs

These are managed from the **Knowledge** section of the web interface.

### 5.9 Reviewing Incidents

All incidents — past and present — are listed under **Incidents** in the navigation.

Each incident record shows:
- When it was detected and by which monitoring tool
- The severity level
- What actions Synapto took automatically
- Whether it was resolved automatically or required human intervention
- A full audit log of every step

### 5.10 Monitoring Synapto Itself

To see if Synapto's services are consuming too much memory or CPU:

```bash
docker stats
```

Press `Ctrl+C` to exit.

---

## 6. Troubleshooting & FAQ

### 6.1 Installation Problems

---

**Problem: `./deploy.sh` fails with "permission denied"**

**Fix:**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

**Problem: Docker says "port is already allocated"**

A service is already using one of the required ports (3000 or 8000).

**Fix:** Find and stop the conflicting service, or change the port in `.env` (e.g., set `API_GATEWAY_PORT=8080`) then re-run the deployment.

```bash
# Find what is using port 3000
sudo lsof -i :3000
```

---

**Problem: Database fails to start — "could not find valid machine for request"**

This usually means Docker ran out of disk space.

**Fix:**
```bash
# Check disk space
df -h

# Clean up unused Docker resources (safe to run)
docker system prune -f
```

---

**Problem: The web interface loads but shows "Cannot connect to server"**

The browser cannot reach the API. The most common cause is that `VITE_API_URL` in `.env` is set to `localhost` but you are accessing the interface from a different machine.

**Fix:** Update `VITE_API_URL` in `.env` to your server's IP address or domain name:
```
VITE_API_URL=http://192.168.1.100:8000
```
Then restart:
```bash
docker compose down && docker compose up -d
```

---

### 6.2 Service Problems

---

**Problem: One service keeps restarting (shows "Restarting" in `docker compose ps`)**

**Diagnose:**
```bash
docker compose logs <service-name> --tail=50
```

Look for an error message near the bottom. Common causes:
- Missing or incorrect value in `.env`
- Database not yet ready (usually resolves after a minute)
- Out of memory

---

**Problem: All services are running but logins fail with "Invalid credentials"**

The `JWT_SECRET_KEY` may have changed after users already logged in, invalidating all existing tokens.

**Fix:** Log out and log back in. If this persists, check that `JWT_SECRET_KEY` in `.env` matches what was set during installation.

---

**Problem: Scripts run but always fail with "Connection refused" or "Host unreachable"**

Synapto cannot connect to the target server to execute the remediation.

**Fix checklist:**
1. Verify the target server's IP or hostname is correct in your topology settings
2. Ensure SSH is enabled on the target server and the correct port (default: 22) is open
3. Check that the credentials (SSH key or username/password) are correctly stored in **Admin → Credentials**
4. If using remote agents, verify the agent is running on the target server: check **Admin → Agents**

---

**Problem: Webhooks from Prometheus/Datadog are not creating incidents**

**Fix checklist:**
1. Verify the integration URL is correct — it should point to port `8001`, not `8000`:
   `http://<server>:8001/api/v1/webhooks/prometheus`
2. Check the integration layer logs:
   ```bash
   docker compose logs integration-layer --tail=50
   ```
3. Ensure the `integration-layer` service is running:
   ```bash
   docker compose ps integration-layer
   ```

---

### 6.3 Data & Performance

---

**Problem: The platform is running slowly after several weeks of use**

The logs and audit tables grow over time.

**Fix:**
```bash
# Vacuum the database (compacts old data)
docker compose exec postgres psql -U selfhealing_user selfhealing -c "VACUUM ANALYZE;"
```

---

**Problem: I accidentally deleted a runbook/script — can I recover it?**

Only if you have a database backup. Restore from your most recent backup (see [Section 5.6](#56-restoring-from-a-backup)).

For future protection, enable regular automated backups (see [Section 5.5](#55-backing-up-your-data)).

---

### 6.4 Frequently Asked Questions

---

**Q: Can Synapto manage Windows servers?**

Yes. Synapto can connect to Windows servers using WinRM (Windows Remote Management) or by installing the Synapto Remote Agent on the Windows server. PowerShell scripts are supported natively.

---

**Q: Is the AI feature required?**

No. The AI feature is optional. Synapto will still work without it — it will use the pre-built library of scripts and runbooks. AI is only invoked when no existing runbook matches the incident, and it can be disabled entirely from the AI Settings page.

---

**Q: Can multiple teams share one Synapto installation?**

Yes. Synapto has multi-tenancy built in. Each team is set up as a "tenant" with their own isolated data, users, and integrations. One super admin manages the overall platform while each team's admin manages their own area.

---

**Q: How do I completely uninstall Synapto and delete all data?**

```bash
./deploy.sh --destroy
```

> **Warning:** This permanently deletes all data including incidents, scripts, and configuration. There is no undo. Make a backup first if you need to preserve anything.

---

**Q: Where do I find the API documentation?**

Go to `http://<your-server-ip>:8000/docs` in your browser. This shows the full interactive API reference for all available endpoints.

---

**Q: I changed a setting in `.env` but nothing changed.**

Configuration changes only take effect after a restart:
```bash
docker compose down && docker compose up -d
```

---

**Q: How do I check what version of Synapto I'm running?**

```bash
cat .env | grep APP_VERSION
```

Or check the footer of the web interface.

---

**Q: The health check shows a service as "unhealthy" but it was working before.**

Try restarting just that service first:
```bash
docker compose restart <service-name>
```

Wait 30 seconds, then run `./health-check.sh` again. If it remains unhealthy, check its logs:
```bash
docker compose logs <service-name> --tail=100
```

---

*For additional support, consult your Synapto administrator or refer to the deployment-specific guides in the `docs/deployment/` folder.*
