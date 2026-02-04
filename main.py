import asyncio
import time
import statistics
import os
from collections import deque, defaultdict
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

app = FastAPI()

# --- SMART PATH DETECTION ---
# This finds the absolute path of the folder where main.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs directory exists relative to the script
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# --- IN-MEMORY STORAGE ---
global_history = []
ip_history = defaultdict(list)
flagged_ips = {}
active_requests = 0
MAX_ACTIVE = 100
ready_queue = deque()
MAX_QUEUE = 10

# --- CONFIGURATION ---
RATE_LIMIT_WINDOW = 5
RATE_LIMIT_MAX = 10
ABUSE_VARIANCE_THRESHOLD = 0.05 

# --- HELPER FUNCTIONS ---

def log_abuse_to_file(ip, reason, history):
    safe_ip = ip.replace('.', '_').replace(':', '_')
    filename = os.path.join(LOG_DIR, f"{safe_ip}.log")
    timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    with open(filename, "a") as f:
        f.write(f"--- INCIDENT DETECTED: {timestamp_str} ---\n")
        f.write(f"IP Address: {ip}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Recent Request Pattern: {history}\n")
        f.write("-" * 40 + "\n\n")

# --- API ENDPOINTS ---

@app.get("/api/request")
async def handle_request(request: Request):
    global active_requests
    client_ip = request.client.host
    now = time.time()

    global_history.append(now)
    ip_history[client_ip].append(now)
    
    if client_ip in flagged_ips:
        return JSONResponse(status_code=403, content={"status": "Blocked", "reason": flagged_ips[client_ip]["reason"]})

    recent_requests = [t for t in ip_history[client_ip] if now - t < RATE_LIMIT_WINDOW]
    ip_history[client_ip] = recent_requests 
    
    if len(recent_requests) > RATE_LIMIT_MAX:
        return JSONResponse(status_code=429, content={"status": "Rate limited"})

    if len(recent_requests) >= 5:
        intervals = [recent_requests[i] - recent_requests[i-1] for i in range(1, len(recent_requests))]
        variance = statistics.variance(intervals) if len(intervals) > 1 else 1
        
        if variance < ABUSE_VARIANCE_THRESHOLD:
            reason = f"Bot-like regularity (Var: {variance:.4f})"
            flagged_ips[client_ip] = {"reason": reason, "flagged_at": now}
            log_abuse_to_file(client_ip, reason, recent_requests)
            return JSONResponse(status_code=403, content={"status": "Blocked", "reason": "Abuse detected"})

    if active_requests < MAX_ACTIVE:
        active_requests += 1
        try:
            await asyncio.sleep(1)
            return {"status": "Processed", "active": active_requests, "ready_queue": len(ready_queue)}
        finally:
            active_requests -= 1
            if ready_queue: ready_queue.popleft()
    elif len(ready_queue) < MAX_QUEUE:
        ready_queue.append(now)
        return {"status": "Queued", "active": active_requests, "ready_queue": len(ready_queue)}
    else:
        return JSONResponse(status_code=503, content={"status": "Server busy"})

@app.get("/api/stats/global")
async def get_global_stats():
    now = time.time()
    relevant = [t for t in global_history if now - t < 30]
    return {"timestamps": relevant}

@app.get("/api/stats/flagged")
async def get_flagged():
    return flagged_ips

@app.get("/api/stats/ip/{ip}")
async def get_ip_stats(ip: str):
    return {"history": ip_history.get(ip, [])}

# --- THE FIX: USE THE DETECTED STATIC PATH ---
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    print(f"CRITICAL ERROR: Could not find static folder at {STATIC_DIR}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)