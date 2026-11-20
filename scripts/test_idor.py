import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 70)
print("CS5104 ABUSE-TESTING: CWE-639 (OBJECT-LEVEL AUTHORIZATION / IDOR)")
print("=" * 70)

# 1. Login as Alice (Customer 1 - Legitimate Owner of Order #1)
print("\n[STEP 1] Login as Alice (Customer 1)...")
r_alice = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "alice_customer",
    "password": "AlicePassword123!"
})
if r_alice.status_code != 200:
    print(f"Failed to login Alice: {r_alice.text}")
    exit(1)

alice_token = r_alice.json()["access_token"]
alice_headers = {"Authorization": f"Bearer {alice_token}"}
print("Alice authenticated successfully.")

# Alice fetches her own order #1
r_alice_order = requests.get(f"{BASE_URL}/orders/1", headers=alice_headers)
print(f"Alice fetches Order #1: HTTP {r_alice_order.status_code}")
if r_alice_order.status_code == 200:
    print(f"Order Details: ID #{r_alice_order.json()['id']}, Total: ₹{r_alice_order.json()['total_amount']}")
    print("[PASS] Legitimate access allowed for the resource owner.")

# 2. Register / Login as Bob (Customer 2 - The Attacker)
print("\n[STEP 2] Authenticating as Bob (Customer 2 - The Attacker)...")
# Try registering bob if not present
requests.post(f"{BASE_URL}/auth/register", json={
    "username": "bob_attacker",
    "email": "bob_attacker@example.com",
    "password": "BobPassword123!",
    "full_name": "Bob The Attacker"
})

r_bob = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "bob_attacker",
    "password": "BobPassword123!"
})
bob_token = r_bob.json()["access_token"]
bob_headers = {"Authorization": f"Bearer {bob_token}"}
print("Bob authenticated with valid Customer JWT.")

# 3. ATTACK: Bob attempts to view Alice's Order #1 (IDOR Attack - CWE-639)
print("\n[STEP 3] ATTACK: Bob attempts IDOR - GET /api/v1/orders/1 ...")
r_attack = requests.get(f"{BASE_URL}/orders/1", headers=bob_headers)
print(f"HTTP Status: {r_attack.status_code}")
print(f"Response Body: {json.dumps(r_attack.json(), indent=2)}")

if r_attack.status_code == 403:
    print("\n[PASS] BOLA / IDOR DEFENSE SUCCESSFUL (CWE-639):")
    print("  -> The API verified object-level ownership before returning data.")
    print("  -> Bob has a valid JWT, but does NOT own Order #1.")
    print("  -> Server explicitly rejected the request with 403 Forbidden.")
else:
    print("\n[FAIL] Vulnerable to IDOR!")

# 4. Privilege Escalation Attack: Bob attempts to delete a product (Admin endpoint)
print("\n[STEP 4] ATTACK: Bob attempts Privilege Escalation - DELETE /api/v1/admin/products/1 ...")
r_priv_attack = requests.delete(f"{BASE_URL}/admin/products/1", headers=bob_headers)
print(f"HTTP Status: {r_priv_attack.status_code}")
print(f"Response Body: {json.dumps(r_priv_attack.json(), indent=2)}")
if r_priv_attack.status_code == 403:
    print("\n[PASS] PRIVILEGE ESCALATION PREVENTED:")
    print("  -> Regular customer role rejected from administrative endpoint.")

print("\n" + "=" * 70)
