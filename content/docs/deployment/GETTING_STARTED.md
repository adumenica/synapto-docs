# Getting Started with Synapto

Welcome! This application automates the detection, analysis, and remediation of system incidents using AI and pre-defined scripts.

## 🚀 How to Start the Application

We've provided a simple script to handle the startup process for you.

1.  **Open a terminal** on the server.
2.  **Navigate to the application folder**:
    ```bash
    cd ~/selfhealing-app
    ```
3.  **Run the startup script**:
    ```bash
    ./start-app.sh
    ```
    *Note: This script will fix permissions and ensure all services are built and running.*

## 🌐 Accessing the UI

Once the script completes, the application will be accessible at:
- **URL**: `http://YOUR_SERVER_IP:3000` (The script will show you the exact IP)
- **Login**: Use your administrative credentials.

## 🔐 Managing Credentials

To run scripts on remote servers, you need to configure credentials in the **Credential Vault**:
1.  Navigate to **Administration** (Settings icon) -> **Credential Vault**.
2.  Add credentials for your target platforms (Linux, Windows, etc.).
3.  Use **Test Resolution** to ensure your hostnames match correctly.

## 🛠️ Basic Troubleshooting

### Viewing Logs
If something isn't working, check the logs:
- **All services**: `docker compose logs -f`
- **Specific service** (e.g., Execution Engine): `docker compose logs -f execution-engine`

### Restarting
If you need to restart everything cleanly:
```bash
./start-app.sh
```

### Stopping the App
```bash
docker compose down
```

---
*For technical support, contact the DevOps team or check the internal documentation. v2.0-Stable*
