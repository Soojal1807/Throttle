# 🛡️ Throttle: Traffic Control & API Defense System

A robust, local demonstration of a traffic-controlled API system
featuring **Rate Limiting**, **Throttling**, **Queueing**, and
**Heuristic Abuse Detection**. This project provides a real-time
monitoring dashboard to visualize traffic patterns and audit suspicious
activity via persistent file-based logs.

------------------------------------------------------------------------

## 🚀 Features

-   **Multi-Stage Rate Limiting**: Implements a sliding window algorithm
    to prevent API exhaustion.
-   **Throttling & Queueing**: Simulates high-load scenarios with a
    100-worker capacity and a secondary overflow queue.
-   **Heuristic Abuse Detection**: Analyzes request interval variance to
    distinguish between human users and automated scripts (bots).
-   **Real-Time Dashboard**: Live visualization of global traffic using
    Chart.js.
-   **Per-IP Audit Logs**: Automatically generates physical `.log` files
    for flagged IPs, providing an audit trail for security analysis.
-   **Administrative Actions**: Directly unblock IPs and clear
    persistent logs from the monitoring interface.

------------------------------------------------------------------------

## 🛠️ Tech Stack

-   **Backend**: Python 3.10+, FastAPI, Uvicorn (Asynchronous Server)
-   **Frontend**: HTML5, CSS3, Vanilla JavaScript (Modern ES6+)
-   **Visualization**: Chart.js
-   **Storage**: In-memory data structures for high-speed processing +
    Local File System for logging

------------------------------------------------------------------------

## 📂 Project Structure

``` plaintext
Throttle/
├── main.py              # FastAPI Backend with defense logic
├── logs/                # Persistent audit logs for flagged IPs
└── static/              # Frontend Web Assets
    ├── index.html       # Client Simulator Page
    ├── dashboard.html   # Admin Monitoring Dashboard
    ├── style.css        # Unified Styling
    ├── script.js        # Client-side request logic
    └── dashboard.js     # Dashboard data-polling & visualization
```

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

## 🧪 Testing Scenarios

-   **Standard Traffic**: Click **"Send Request"** to see normal
    processing.
-   **Rate Limit Trigger**: Click **"Send Request"** more than 10 times
    in 5 seconds to trigger a `429 Too Many Requests` status.
-   **Bot Detection**: Toggle **"Spam Mode"**. The system will detect
    the near-zero variance in request timing and issue a permanent
    block.
-   **Audit**: Check the `logs/` folder for a detailed report of why the
    IP was flagged.

------------------------------------------------------------------------

## ⚙️ Configuration

The system parameters can be adjusted at the top of `main.py`:

-   `RATE_LIMIT_MAX`: Requests allowed per window.
-   `ABUSE_VARIANCE_THRESHOLD`: Sensitivity of the bot-detection
    algorithm.
-   `MAX_ACTIVE`: Maximum simultaneous processing threads.

------------------------------------------------------------------------

## 📜 License

This project is intended for educational and portfolio purposes.
