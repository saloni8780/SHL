"""Integration tests against a running server.
Usage: python test_api.py [base_url]
Default base_url: http://localhost:8000
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read())


def get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=35) as resp:
        return json.loads(resp.read())


def check(name: str, condition: bool, msg: str = ""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f": {msg}" if msg else ""))
    if not condition:
        raise AssertionError(f"Test failed: {name}")


print(f"\nRunning tests against {BASE_URL}\n")

# Health check
print("=== /health ===")
h = get("/health")
check("status is ok", h.get("status") == "ok", str(h))

# Vague query — must NOT recommend on turn 1
print("\n=== Vague query (no recommendations expected) ===")
r = post("/chat", {"messages": [{"role": "user", "content": "I need an assessment"}]})
check("reply non-empty", bool(r.get("reply")))
check("no recommendations on vague turn 1", len(r.get("recommendations", [])) == 0)
check("end_of_conversation is false", r.get("end_of_conversation") is False)

# Specific query — must recommend
print("\n=== Specific Java developer query ===")
r = post("/chat", {
    "messages": [
        {"role": "user", "content": "I'm hiring a mid-level Java developer, 4 years experience, for selection"},
    ]
})
check("reply non-empty", bool(r.get("reply")))
check("recommendations present", len(r.get("recommendations", [])) >= 1)
check("max 10 recommendations", len(r.get("recommendations", [])) <= 10)
recs = r.get("recommendations", [])
if recs:
    for rec in recs:
        check(f"URL non-empty: {rec['name']}", bool(rec.get("url")))
        check(f"URL starts with shl.com: {rec['name']}", "shl.com" in rec.get("url", ""))
        check(f"test_type present: {rec['name']}", bool(rec.get("test_type")))

# Multi-turn refinement
print("\n=== Multi-turn: refinement ===")
r2 = post("/chat", {
    "messages": [
        {"role": "user", "content": "I'm hiring a customer service manager"},
        {"role": "assistant", "content": r.get("reply", "")},
        {"role": "user", "content": "Also add a personality assessment"},
    ]
})
check("reply non-empty", bool(r2.get("reply")))

# Off-topic refusal
print("\n=== Off-topic refusal ===")
r3 = post("/chat", {"messages": [{"role": "user", "content": "What is the legal minimum wage in California?"}]})
check("reply non-empty", bool(r3.get("reply")))
check("no recommendations for off-topic", len(r3.get("recommendations", [])) == 0)

# Schema compliance
print("\n=== Schema compliance ===")
for key in ["reply", "recommendations", "end_of_conversation"]:
    check(f"field '{key}' present", key in r)

print("\nAll tests passed!\n")
