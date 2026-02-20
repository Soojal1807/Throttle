# 🛡️ Throttle: Traffic Control & API Defense System

A robust, local demonstration of a traffic-controlled API system
featuring **Rate Limiting**, **Throttling**, **Queueing**, and
**Heuristic Abuse Detection**. This project provides a real-time
monitoring dashboard to visualize traffic patterns and audit suspicious
activity via persistent file-based logs.

------------------------------------------------------------------------

## 🚀 Features

-   **Multi-Stage Rate Limiting**: Implements a sliding window algorithm using memory-efficient `deque` structures to prevent API exhaustion.
-   **Security Hardening**: Supports **Proxy-Aware IP detection** via `X-Forwarded-For` and `X-Real-IP` headers with a configurable trusted proxy list.
-   **True Throttling & Queueing**: Uses an asynchronous `Semaphore` and `Queue` system to manage concurrent requests. Excess traffic is actually queued and processed as capacity becomes available.
-   **Heuristic Abuse Detection**: Analyzes request interval variance to distinguish between human users and automated scripts (bots).
-   **Persistent Blocking**: Flagged IPs are automatically blocked from all endpoints until administratively unblocked.
-   **Real-Time Dashboard**: Live visualization of global traffic and queue status using Chart.js.
-   **Admin API & Audit Logs**: Automatically generates physical `.log` files for flagged IPs and provides API endpoints for unblocking and log maintenance.

------------------------------------------------------------------------

## 🛠️ Admin API

The system provides several administrative endpoints:
- `POST /api/admin/unblock/{ip}`: Removes an IP from the blocklist.
- `POST /api/admin/clear-logs`: Wipes all persistent audit logs from the server.

------------------------------------------------------------------------

## 🛠️ Tech Stack

-   **Backend**: Python 3.10+, FastAPI, Uvicorn (Asynchronous Server)
-   **Frontend**: HTML5, CSS3, Vanilla JavaScript (Modern ES6+)
-   **Visualization**: Chart.js
-   **Storage**: In-memory data structures (optimized with `deque`) + Local File System for logging

------------------------------------------------------------------------

## ⚡ Quick Start

### 1. Installation

Ensure you have Python installed, then install the required
dependencies:

``` bash
pip install fastapi uvicorn
```

### 2. Execution

Run the server from the project root:

``` bash
python main.py
```

### 3. Access

-   **Client Simulator**: http://localhost:8000/index.html
-   **Monitoring Dashboard**: http://localhost:8000/dashboard.html

------------------------------------------------------------------------

## 🐳 Docker Deployment

For a professional, containerized setup, use Docker Compose:

``` bash
# Build and start the container
docker-compose up --build -d
```

The system will be available at `http://localhost:8000`. Audit logs are persisted to the `./logs` directory on your host machine via volumes.

------------------------------------------------------------------------

## 📂 Project Structure

``` plaintext
Throttle/
├── main.py              # FastAPI Backend with advanced defense logic
├── logs/                # Persistent audit logs for flagged IPs
└── static/              # Frontend Web Assets (HTML/CSS/JS)
```

------------------------------------------------------------------------

## 🧪 Testing Scenarios

-   **Rate Limit Trigger**: Click **"Send Request"** more than 10 times in 5 seconds to trigger a `429 Too Many Requests` status.
-   **Bot Detection**: Toggle **"Spam Mode"**. The system detects high-regularity intervals and issues a permanent 403 block.
-   **Queueing**: When capacity exceeds `MAX_ACTIVE`, requests will wait in the `MAX_QUEUE` buffer before processing.
-   **Audit**: Check the `logs/` folder for human-readable reports of blocked IP activity.

------------------------------------------------------------------------

## ⚙️ Configuration

The system parameters can be adjusted at the top of `main.py`:

-   `RATE_LIMIT_MAX`: Requests allowed per sliding window.
-   `TRUSTED_PROXIES`: List of IP addresses allowed to provide `X-Forwarded-For` headers.
-   `MAX_ACTIVE`: Maximum global simultaneous processing capacity.
-   `MAX_QUEUE`: Maximum size of the overflow queue before returning 503.
-   `ABUSE_VARIANCE_THRESHOLD`: Sensitivity of the bot-detection algorithm.

This project is intended for educational and portfolio purposes.
