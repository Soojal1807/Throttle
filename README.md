# 🛡️ Throttle:

A high-performance, asynchronous traffic management system for APIs. This project implements advanced rate limiting, throttling, and heuristic-based bot detection to protect your services from abuse while ensuring smooth traffic flow.

---

## 🌟 Key Features

### 🚦 Multi-Stage Rate Limiting
Implements a sliding window algorithm using memory-efficient `deque` structures. It monitors request frequency per IP and global traffic, preventing API exhaustion.

### 🛡️ Heuristic Abuse Detection
Distinguishes between human users and automated scripts (bots) by analyzing request interval variance. Flagged IPs are automatically blocked and logged.

### ⏳ True Throttling & Queueing
Unlike simple wrappers, Throttle uses an asynchronous `Semaphore` and `Queue` system. Excess traffic is buffered and processed as capacity becomes available, maintaining system stability under load.

### 📊 Real-Time Dashboard
A live visualization suite built with Chart.js to monitor:
- Global request frequency
- Current queue depth
- Blocked IP audit logs
- Heuristic analysis status

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI (Asynchronous framework)
- **Concurrency**: `asyncio`, `Semaphore`, `Queue`
- **Frontend**: ES6+ JavaScript, Chart.js, Vanilla CSS
- **Containerization**: Docker & Docker Compose
- **Persistence**: File-based audit logs for blocked entity tracking

---

## 🚀 Quick Start

### Docker (Recommended)
Launch the entire system in a containerized environment:
```bash
docker-compose up --build -d
```
Access the dashboard at `http://localhost:8000/dashboard.html`.

### Local Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python main.py
   ```

---

## 🧪 Testing Scenarios

- **Rate Limiting**: Trigger a `429 Too Many Requests` by exceeding 10 requests in 5 seconds.
- **Bot Detection**: Enable "Spam Mode" in the client simulator to trigger the heuristic detection.
- **Queueing**: Observe how requests are queued when `MAX_ACTIVE` capacity is reached.

---

## 📂 Project Structure

- `main.py`: The heart of the defense logic and API endpoints.
- `static/`: Frontend assets for the monitoring suite.
- `logs/`: Persistent records of all blocked IPs and their activity.
- `verify_throttle.py`: A CLI tool for automated system validation.

---

## ⚙️ Configuration

Adjust constants in `main.py` to tune the defense parameters:
- `RATE_LIMIT_MAX`: Requests per window.
- `MAX_ACTIVE`: Maximum concurrent request processing.
- `MAX_QUEUE`: Buffer size for pending requests.
- `ABUSE_VARIANCE_THRESHOLD`: Sensitivity for bot detection.


