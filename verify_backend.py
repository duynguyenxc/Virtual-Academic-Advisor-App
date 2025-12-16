import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_root():
    try:
        r = requests.get("http://localhost:8000/")
        print(f"[ROOT] Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Backend is Online")
        else:
            print("❌ Backend returned error")
    except Exception as e:
        print(f"❌ Could not connect to backend: {e}")

def test_chat():
    print("\n[TEST] Testing AI Chat (RAG)...")
    payload = {"message": "What is the prerequisite for CSCI 111?"}
    try:
        start = time.time()
        r = requests.post(f"{BASE_URL}/chat/message", json=payload)
        duration = time.time() - start
        
        if r.status_code == 200:
            print(f"✅ Chat Response ({duration:.2f}s): {r.json()['response']}")
        else:
            print(f"❌ Chat Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Chat Request Failed: {e}")

def main():
    print("=== STARTING BACKEND HEALTH CHECK ===")
    test_root()
    time.sleep(1)
    test_chat()
    print("=== END CHECK ===")

if __name__ == "__main__":
    main()
