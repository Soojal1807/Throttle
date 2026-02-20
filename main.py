import asyncio
import time
import statistics
import os
import shutil
from collections import deque, defaultdict
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

app = FastAPI()

# --- PATH DETECTION ---
# Absolute directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# --- STORAGE ---
# Global request history
global_history = deque(maxlen=1000)
# IP request history
ip_history = defaultdict(lambda: deque(maxlen=20))
flagged_ips = {}

# --- CONFIG ---
RATE_LIMIT_WINDOW = 5
RATE_LIMIT_MAX = 10
ABUSE_VARIANCE_THRESHOLD = 0.05
TRUSTED_PROXIES = ["127.0.0.1"] # Trusted proxy IPs

# --- CONCURRENCY ---
MAX_ACTIVE = 100
semaphore = asyncio.Semaphore(MAX_ACTIVE)
MAX_QUEUE = 50
request_queue = asyncio.Queue(maxsize=MAX_QUEUE)

# --- HELPERS ---

def get_client_ip(request: Request):
    """Extract client IP."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # First client IP
        client_ip = forwarded_for.split(",")[0].strip()
        # From trusted proxy
        if request.client.host in TRUSTED_PROXIES:
            return client_ip
    return request.client.host

def log_abuse_to_file(ip, reason, history):
    safe_ip = ip.replace('.', '_').replace(':', '_')
    filename = os.path.join(LOG_DIR, f"{safe_ip}.log")
    timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    # Human-readable timestamps
    history_str = [time.strftime('%H:%M:%S', time.localtime(t)) for t in history]
    
    with open(filename, "a") as f:
        f.write(f"--- INCIDENT DETECTED: {timestamp_str} ---\n")
        f.write(f"IP Address: {ip}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Recent Request Pattern: {history_str}\n")
        f.write("-" * 40 + "\n\n")

async def prune_ip_history():
    """Prune inactive IPs."""
    while True:
        await asyncio.sleep(60) # Run every minute
        now = time.time()
        to_delete = []
        for ip, history in ip_history.items():
            # Filter old timestamps
            while history and now - history[0] > 60: # Limit history window
                history.popleft()
            if not history:
                to_delete.append(ip)
        for ip in to_delete:
            del ip_history[ip]

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(prune_ip_history())

# --- ENDPOINTS ---

@app.get("/api/request")
async def handle_request(request: Request):
    client_ip = get_client_ip(request)
    now = time.time()

    global_history.append(now)
    
    if client_ip in flagged_ips:
        return JSONResponse(
            status_code=403, 
            content={"status": "Blocked", "reason": flagged_ips[client_ip]["reason"]}
        )

    # Filter history window
    # Logic uses list
    history = ip_history[client_ip]
    history.append(now)
    
    recent_requests = [t for t in history if now - t < RATE_LIMIT_WINDOW]
    
    # 1. Rate Limit
    if len(recent_requests) > RATE_LIMIT_MAX:
        return JSONResponse(status_code=429, content={"status": "Rate limited"})

    # 2. Bot Detection
    if len(recent_requests) >= 5:
        intervals = [recent_requests[i] - recent_requests[i-1] for i in range(1, len(recent_requests))]
        variance = statistics.variance(intervals) if len(intervals) > 1 else 1
        
        if variance < ABUSE_VARIANCE_THRESHOLD:
            reason = f"Bot-like regularity (Var: {variance:.4f})"
            flagged_ips[client_ip] = {"reason": reason, "flagged_at": now}
            log_abuse_to_file(client_ip, reason, list(recent_requests))
            return JSONResponse(status_code=403, content={"status": "Blocked", "reason": "Abuse detected"})

    # 3. Process Request
    # Capacity available check
    if semaphore._value > 0:
        async with semaphore:
            await asyncio.sleep(1) # Simulate work
            return {
                "status": "Processed", 
                "active": MAX_ACTIVE - semaphore._value, 
                "queue": 0
            }
    
    # 4. Queue Request
    if request_queue.full():
        return JSONResponse(status_code=503, content={"status": "Server busy (Queue full)"})
    
    # Wait in queue
    await request_queue.put(now)
    try:
        async with semaphore:
            await request_queue.get() # Pop from queue
            await asyncio.sleep(1)
            return {
                "status": "Processed (After Waiting)", 
                "active": MAX_ACTIVE - semaphore._value, 
                "queue": request_queue.qsize()
            }
    finally:
        pass

@app.get("/api/stats/global")
async def get_global_stats():
    now = time.time()
    relevant = [t for t in global_history if now - t < 30]
    return {
        "timestamps": relevant,
        "active_requests": MAX_ACTIVE - semaphore._value,
        "queued_requests": request_queue.qsize(),
        "total_flagged": len(flagged_ips)
    }

@app.get("/api/stats/flagged")
async def get_flagged():
    return flagged_ips

@app.get("/api/stats/ip/{ip}")
async def get_ip_stats(ip: str):
    return {"history": list(ip_history.get(ip, []))}

# --- ADMIN ---

@app.post("/api/admin/unblock/{ip}")
async def unblock_ip(ip: str):
    if ip in flagged_ips:
        del flagged_ips[ip]
        if ip in ip_history:
            ip_history[ip].clear()
        return {"status": "Success", "message": f"IP {ip} unblocked"}
    raise HTTPException(status_code=404, detail="IP not found in blocklist")

@app.post("/api/admin/clear-logs")
async def clear_logs():
    try:
        for filename in os.listdir(LOG_DIR):
            file_path = os.path.join(LOG_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return {"status": "Success", "message": "All logs cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- STATIC ---
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    print(f"CRITICAL ERROR: Could not find static folder at {STATIC_DIR}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)