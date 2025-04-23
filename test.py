#!/usr/bin/env python3
import requests
from concurrent.futures import ThreadPoolExecutor
import time

BASE = "http://localhost:8080"

def rate_test(path, headers=None, concurrency=50):
    """Blast `concurrency` parallel GETs at BASE+path and count status codes."""
    URL = BASE + path
    def call(_):
        try:
            r = requests.get(URL, headers=headers or {}, timeout=2)
            return r.status_code
        except:
            return None

    start = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as exe:
        results = list(exe.map(call, range(concurrency)))
    elapsed = time.time() - start
    print(f"\n→ {path} : sent {concurrency} reqs in {elapsed:.2f}s → {concurrency/elapsed:.1f} req/s")
    codes = {}
    for c in results:
        codes[c] = codes.get(c, 0) + 1
    for code, count in sorted(codes.items()):
        print(f"   {count}×{code}")
    return codes

if __name__ == "__main__":
    # 1) Grab a token for protected tests:
    login = requests.post(
        BASE+"/api/login/",
        json={"email":"1@1","password":"1"}
    )
    token = login.json().get("access_token")
    print("Obtained token:", token[:30] + "…")

    # 2) Test an **unprotected** proxied endpoint (no JWT needed).
    #    This goes through limit_req and limit_conn.
    rate_test("/health/login")       # lightweight upstream
   
    # 3) Test a protected endpoint **without** JWT (should all be 401)
    rate_test("/api/traffic/")

    # 4) Test the same protected endpoint **with** JWT (should hit limit)
    hdr = {"Authorization": f"Bearer {token}"}
    rate_test("/api/traffic/", headers=hdr)
