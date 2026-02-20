import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"

async def test_rate_limiting():
    print("\n--- Testing Rate Limiting ---")
    async with httpx.AsyncClient() as client:
        for i in range(12):
            resp = await client.get(f"{BASE_URL}/api/request")
            print(f"Req {i+1}: {resp.status_code} - {resp.json().get('status')}")
            if resp.status_code == 429:
                print("SUCCESS: Rate limited as expected.")
                break

async def test_bot_detection():
    print("\n--- Testing Bot Detection (Spam Mode) ---")
    async with httpx.AsyncClient() as client:
        for i in range(10):
            resp = await client.get(f"{BASE_URL}/api/request")
            print(f"Req {i+1}: {resp.status_code} - {resp.json().get('status')}")
            if resp.status_code == 403:
                print("SUCCESS: Bot detected and blocked.")
                break
            await asyncio.sleep(0.1) # Very regular interval

async def test_concurrency_and_queue():
    print("\n--- Testing Concurrency and Queueing (Simulated) ---")
    # Note: This is hard to test with a single local client without many workers
    # But we can check the stats
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/api/stats/global")
        stats = resp.json()
        print(f"Current Stats: {stats}")

async def main():
    try:
        await test_rate_limiting()
        await asyncio.sleep(6) # Wait for rate limit window to reset
        await test_bot_detection()
        await test_concurrency_and_queue()
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure the server is running (python main.py)")

if __name__ == "__main__":
    asyncio.run(main())
