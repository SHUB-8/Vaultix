

"""
Comprehensive end-to-end test script for Vaultix API.

Tests every endpoint across all 3 roles (Admin, Analyst, Viewer).
Run with the server already running:
    python -m scripts.test_api

Requirements: httpx (already in requirements.txt)
"""

import httpx
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Track test results
passed = 0
failed = 0
errors = []


def log_pass(test_name: str):
    global passed
    passed += 1
    print(f"  ✅ {test_name}")


def log_fail(test_name: str, detail: str):
    global failed
    failed += 1
    errors.append(f"{test_name}: {detail}")
    print(f"  ❌ {test_name} — {detail}")


def check(test_name: str, condition: bool, detail: str = ""):
    if condition:
        log_pass(test_name)
    else:
        log_fail(test_name, detail or "Assertion failed")


def main():
    run_id = uuid.uuid4().hex[:8]
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # ═══════════════════════════════════════════════
    # 1. HEALTH CHECK
    # ═══════════════════════════════════════════════
    print("\n🏥 HEALTH CHECK")
    r = client.get("http://127.0.0.1:8000/health")
    check("Health endpoint returns 200", r.status_code == 200)
    check("Health status is healthy", r.json().get("status") == "healthy")

    # ═══════════════════════════════════════════════
    # 2. AUTH — LOGIN
    # ═══════════════════════════════════════════════
    print("\n🔐 AUTH — LOGIN")

    # Admin login
    r = client.post("/auth/login", json={"email": "admin@vaultix.dev", "password": "admin123"})
    check("Admin login returns 200", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    admin_token = r.json().get("access_token", "")
    check("Admin login returns token", bool(admin_token))
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Analyst login
    r = client.post("/auth/login", json={"email": "analyst@vaultix.dev", "password": "analyst123"})
    check("Analyst login returns 200", r.status_code == 200, f"Got {r.status_code}")
    analyst_token = r.json().get("access_token", "")
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    # Viewer login
    r = client.post("/auth/login", json={"email": "viewer@vaultix.dev", "password": "viewer123"})
    check("Viewer login returns 200", r.status_code == 200, f"Got {r.status_code}")
    viewer_token = r.json().get("access_token", "")
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Invalid login
    r = client.post("/auth/login", json={"email": "admin@vaultix.dev", "password": "wrongpassword"})
    check("Wrong password returns 401", r.status_code == 401, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 3. AUTH — REGISTER
    # ═══════════════════════════════════════════════
    print("\n📝 AUTH — REGISTER")

    test_email = f"test_{run_id}@vaultix.dev"
    r = client.post("/auth/register", json={
        "name": "Test User",
        "email": test_email,
        "password": "testuser123",
    })
    check("Register returns 201", r.status_code == 201, f"Got {r.status_code}: {r.text}")
    check("New user gets viewer role", r.json().get("role") == "viewer")

    # Duplicate email
    r = client.post("/auth/register", json={
        "name": "Duplicate",
        "email": test_email,
        "password": "testuser123",
    })
    check("Duplicate email returns 409", r.status_code == 409, f"Got {r.status_code}")

    # Short password
    r = client.post("/auth/register", json={
        "name": "Bad Password",
        "email": "badpass@vaultix.dev",
        "password": "short",
    })
    check("Short password returns 422", r.status_code == 422, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 4. AUTH — ME
    # ═══════════════════════════════════════════════
    print("\n👤 AUTH — ME")

    r = client.get("/auth/me", headers=admin_headers)
    check("GET /me with admin token returns 200", r.status_code == 200, f"Got {r.status_code}")
    check("GET /me returns admin role", r.json().get("role") == "admin")
    admin_id = r.json().get("id")

    r = client.get("/auth/me")
    check("GET /me without token returns 401", r.status_code == 401, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 5. USERS
    # ═══════════════════════════════════════════════
    print("\n👥 USERS")

    # Admin can list users
    r = client.get("/users", headers=admin_headers)
    check("Admin can list users", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    users = r.json().get("users", [])
    check("Users list has >= 4 users", len(users) >= 4, f"Got {len(users)}")

    # Analyst can list users
    r = client.get("/users", headers=analyst_headers)
    check("Analyst can list users", r.status_code == 200, f"Got {r.status_code}")

    # Viewer CANNOT list users
    r = client.get("/users", headers=viewer_headers)
    check("Viewer cannot list users (403)", r.status_code == 403, f"Got {r.status_code}")

    # Get user by ID
    test_user_id = None
    for u in users:
        if u["email"] == test_email:
            test_user_id = u["id"]
            break

    if test_user_id:
        r = client.get(f"/users/{test_user_id}", headers=admin_headers)
        check("Get user by ID returns 200", r.status_code == 200, f"Got {r.status_code}")

        # Update role
        r = client.patch(f"/users/{test_user_id}/role", headers=admin_headers, json={"role": "analyst"})
        check("Admin can change user role", r.status_code == 200, f"Got {r.status_code}: {r.text}")
        check("User role updated to analyst", r.json().get("role") == "analyst")

        # Deactivate user
        r = client.patch(f"/users/{test_user_id}/status", headers=admin_headers, json={"is_active": False})
        check("Admin can deactivate user", r.status_code == 200, f"Got {r.status_code}")
        check("User is now inactive", r.json().get("is_active") is False)

        # Re-activate for later tests
        r = client.patch(f"/users/{test_user_id}/status", headers=admin_headers, json={"is_active": True})
        check("Admin can reactivate user", r.status_code == 200, f"Got {r.status_code}")

    # Admin cannot change own role
    r = client.patch(f"/users/{admin_id}/role", headers=admin_headers, json={"role": "viewer"})
    check("Admin cannot change own role (400)", r.status_code == 400, f"Got {r.status_code}")

    # Analyst cannot change roles
    if test_user_id:
        r = client.patch(f"/users/{test_user_id}/role", headers=analyst_headers, json={"role": "viewer"})
        check("Analyst cannot change roles (403)", r.status_code == 403, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 6. EVENTS
    # ═══════════════════════════════════════════════
    print("\n🎪 EVENTS")

    # List existing events
    r = client.get("/events", headers=admin_headers)
    check("Admin can list events", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    events = r.json().get("events", [])
    check("At least 4 seeded events exist", len(events) >= 4, f"Got {len(events)}")

    # Find TechSurge for sub-event creation
    techsurge_id = None
    for e in events:
        if e["name"] == "TechSurge 2025":
            techsurge_id = e["id"]
            break

    # Create a new event
    r = client.post("/events", headers=admin_headers, json={
        "name": "Code Sprint",
        "type": "sub_event",
        "parent_event_id": techsurge_id,
        "description": "Competitive coding event",
    })
    check("Admin can create event", r.status_code == 201, f"Got {r.status_code}: {r.text}")
    new_event_id = r.json().get("id")

    # Sub-event without parent should fail
    r = client.post("/events", headers=admin_headers, json={
        "name": "Orphan Event",
        "type": "sub_event",
    })
    check("Sub-event without parent returns 400", r.status_code == 400, f"Got {r.status_code}")

    # Update event
    r = client.patch(f"/events/{new_event_id}", headers=admin_headers, json={
        "description": "Updated: 2-hour competitive coding event",
    })
    check("Admin can update event", r.status_code == 200, f"Got {r.status_code}")

    # Get single event
    r = client.get(f"/events/{new_event_id}", headers=analyst_headers)
    check("Analyst can get event by ID", r.status_code == 200, f"Got {r.status_code}")

    # Viewer cannot list events
    r = client.get("/events", headers=viewer_headers)
    check("Viewer cannot list events (403)", r.status_code == 403, f"Got {r.status_code}")

    # Analyst cannot create events
    r = client.post("/events", headers=analyst_headers, json={
        "name": "Should Fail",
        "type": "major_fest",
    })
    check("Analyst cannot create events (403)", r.status_code == 403, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 7. FINANCIAL RECORDS
    # ═══════════════════════════════════════════════
    print("\n💰 FINANCIAL RECORDS")

    # Create income record
    r = client.post("/records", headers=admin_headers, json={
        "amount": 10000.00,
        "type": "income",
        "category": "registration_fees",
        "event_id": new_event_id,
        "date": "2025-03-20",
        "notes": "Code Sprint registration fees",
    })
    check("Admin can create income record", r.status_code == 201, f"Got {r.status_code}: {r.text}")
    income_record_id = r.json().get("id")

    # Create expense record
    r = client.post("/records", headers=admin_headers, json={
        "amount": 5000.00,
        "type": "expense",
        "category": "prizes_certificates",
        "event_id": new_event_id,
        "date": "2025-03-21",
        "notes": "Prizes for Code Sprint winners",
    })
    check("Admin can create expense record", r.status_code == 201, f"Got {r.status_code}: {r.text}")
    expense_record_id = r.json().get("id")

    # Invalid: expense category on income type
    r = client.post("/records", headers=admin_headers, json={
        "amount": 1000.00,
        "type": "income",
        "category": "venue_logistics",
        "date": "2025-03-20",
    })
    check("Income with expense category returns 422", r.status_code == 422, f"Got {r.status_code}")

    # Invalid: negative amount
    r = client.post("/records", headers=admin_headers, json={
        "amount": -500.00,
        "type": "expense",
        "category": "miscellaneous",
        "date": "2025-03-20",
    })
    check("Negative amount returns 422", r.status_code == 422, f"Got {r.status_code}")

    # List records
    r = client.get("/records", headers=admin_headers)
    check("Admin can list records", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    records_data = r.json()
    check("Records list has pagination metadata", "total" in records_data and "pages" in records_data)

    # Filter by type
    r = client.get("/records?type=income", headers=admin_headers)
    check("Filter by type works", r.status_code == 200, f"Got {r.status_code}")
    for rec in r.json().get("records", []):
        if rec["type"] != "income":
            log_fail("Filter by type", f"Found non-income record: {rec['type']}")
            break
    else:
        log_pass("All filtered records are income")

    # Filter by category
    r = client.get("/records?category=registration_fees", headers=admin_headers)
    check("Filter by category works", r.status_code == 200, f"Got {r.status_code}")

    # Filter by date range
    r = client.get("/records?date_from=2025-02-01&date_to=2025-02-28", headers=admin_headers)
    check("Filter by date range works", r.status_code == 200, f"Got {r.status_code}")

    # Search by notes
    r = client.get("/records?search=hackathon", headers=admin_headers)
    check("Search by notes works", r.status_code == 200, f"Got {r.status_code}")

    # Pagination
    r = client.get("/records?page=1&limit=5", headers=admin_headers)
    check("Pagination works", r.status_code == 200 and len(r.json().get("records", [])) <= 5,
          f"Got {r.status_code}, records: {len(r.json().get('records', []))}")

    # Get single record
    r = client.get(f"/records/{income_record_id}", headers=admin_headers)
    check("Get single record works", r.status_code == 200, f"Got {r.status_code}")

    # Update record
    r = client.patch(f"/records/{income_record_id}", headers=admin_headers, json={
        "amount": 12000.00,
        "notes": "Updated: Code Sprint registration fees — increased",
    })
    check("Admin can update record", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    check("Amount updated to 12000", float(r.json().get("amount", 0)) == 12000.00)

    # Soft delete record
    r = client.delete(f"/records/{expense_record_id}", headers=admin_headers)
    check("Admin can soft-delete record", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    check("Record is marked as deleted", r.json().get("is_deleted") is True)

    # Soft-deleted record should not appear in list
    r = client.get(f"/records/{expense_record_id}", headers=admin_headers)
    check("Soft-deleted record returns 404", r.status_code == 404, f"Got {r.status_code}")

    # Analyst can read records but not write
    r = client.get("/records", headers=analyst_headers)
    check("Analyst can list records", r.status_code == 200, f"Got {r.status_code}")

    r = client.post("/records", headers=analyst_headers, json={
        "amount": 1000.00, "type": "income", "category": "other_income", "date": "2025-03-20",
    })
    check("Analyst cannot create records (403)", r.status_code == 403, f"Got {r.status_code}")

    # Viewer cannot access records at all
    r = client.get("/records", headers=viewer_headers)
    check("Viewer cannot list records (403)", r.status_code == 403, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 8. DASHBOARD & ANALYTICS
    # ═══════════════════════════════════════════════
    print("\n📊 DASHBOARD & ANALYTICS")

    # Summary — all roles
    r = client.get("/dashboard/summary", headers=viewer_headers)
    check("Viewer can access summary", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    summary = r.json()
    check("Summary has total_income", "total_income" in summary)
    check("Summary has total_expenses", "total_expenses" in summary)
    check("Summary has net_balance", "net_balance" in summary)
    check("Summary has total_records", "total_records" in summary)

    r = client.get("/dashboard/summary", headers=admin_headers)
    check("Admin can access summary", r.status_code == 200, f"Got {r.status_code}")

    # Analytics — Admin + Analyst only
    r = client.get("/dashboard/analytics", headers=admin_headers)
    check("Admin can access analytics", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    analytics = r.json()
    check("Analytics has sponsorship_dependency_ratio", "sponsorship_dependency_ratio" in analytics)
    check("Analytics has event_pnl", "event_pnl" in analytics)
    check("Analytics has category_breakdown", "category_breakdown" in analytics)

    r = client.get("/dashboard/analytics", headers=analyst_headers)
    check("Analyst can access analytics", r.status_code == 200, f"Got {r.status_code}")

    r = client.get("/dashboard/analytics", headers=viewer_headers)
    check("Viewer cannot access analytics (403)", r.status_code == 403, f"Got {r.status_code}")

    # Trends
    r = client.get("/dashboard/trends", headers=admin_headers)
    check("Trends endpoint works", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    trends = r.json()
    check("Trends returns list of months", isinstance(trends, list) and len(trends) > 0,
          f"Got {len(trends)} items")

    r = client.get("/dashboard/trends", headers=viewer_headers)
    check("Viewer cannot access trends (403)", r.status_code == 403, f"Got {r.status_code}")

    # Event P&L
    r = client.get("/dashboard/events", headers=admin_headers)
    check("Event P&L endpoint works", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    event_pnl = r.json()
    check("Event P&L returns data", isinstance(event_pnl, list) and len(event_pnl) > 0,
          f"Got {len(event_pnl)} events")

    # Category breakdown
    r = client.get("/dashboard/categories", headers=admin_headers)
    check("Category breakdown endpoint works", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    categories = r.json()
    check("Category breakdown has percentage", all("percentage" in c for c in categories))

    # ═══════════════════════════════════════════════
    # 9. AUDIT LOGS
    # ═══════════════════════════════════════════════
    print("\n📋 AUDIT LOGS")

    r = client.get("/audit-logs", headers=admin_headers)
    check("Admin can list audit logs", r.status_code == 200, f"Got {r.status_code}: {r.text}")
    audit_data = r.json()
    check("Audit logs have entries", audit_data.get("total", 0) > 0,
          f"Got {audit_data.get('total', 0)} entries")
    check("Audit logs have pagination", "pages" in audit_data)

    # Filter by action
    r = client.get("/audit-logs?action=created", headers=admin_headers)
    check("Filter audit logs by action works", r.status_code == 200, f"Got {r.status_code}")

    # Filter by resource type
    r = client.get("/audit-logs?resource_type=financial_record", headers=admin_headers)
    check("Filter audit logs by resource type works", r.status_code == 200, f"Got {r.status_code}")

    # Analyst can view audit logs
    r = client.get("/audit-logs", headers=analyst_headers)
    check("Analyst can view audit logs", r.status_code == 200, f"Got {r.status_code}")

    # Viewer cannot view audit logs
    r = client.get("/audit-logs", headers=viewer_headers)
    check("Viewer cannot view audit logs (403)", r.status_code == 403, f"Got {r.status_code}")

    # ═══════════════════════════════════════════════
    # 10. ERROR FORMAT VALIDATION
    # ═══════════════════════════════════════════════
    print("\n🚨 ERROR FORMAT")

    r = client.get("/records", headers=viewer_headers)
    body = r.json()
    has_error_format = "detail" in body and "error" in body.get("detail", {})
    check("Error response matches standard format", has_error_format, f"Got: {body}")

    # ═══════════════════════════════════════════════
    # RESULTS SUMMARY
    # ═══════════════════════════════════════════════
    print("\n" + "=" * 55)
    total = passed + failed
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 55)

    if errors:
        print("\n  Failed tests:")
        for err in errors:
            print(f"    ❌ {err}")

    print()
    client.close()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
