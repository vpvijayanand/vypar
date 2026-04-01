"""Comprehensive test: all new features - view pages, daybook, analytics, payment history."""
import requests, re, sys

s = requests.Session()
r = s.post('http://localhost:5000/auth/login',
           data={'username': 'admin', 'password': 'admin123'}, allow_redirects=False)

passed = 0
failed = 0

def check(name, url, must_contain=None):
    global passed, failed
    r = s.get(url)
    ok = r.status_code == 200
    if ok and must_contain:
        ok = all(text in r.text for text in must_contain)
    if ok:
        passed += 1
        print(f"  ✅ {name} ({r.status_code})")
    else:
        failed += 1
        missing = []
        if must_contain:
            missing = [t for t in must_contain if t not in r.text]
        print(f"  ❌ {name} ({r.status_code}) missing: {missing}")
    return r

print("\n── Existing Pages ──")
check("Dashboard", "http://localhost:5000/dashboard", ["Total Sales", "Low Stock", "Out of Stock"])
check("Sales List", "http://localhost:5000/sales", ["INV-"])
check("Purchases List", "http://localhost:5000/purchases", ["PUR-"])
check("Parties List", "http://localhost:5000/parties", ["bi-eye"])
check("Items List", "http://localhost:5000/items", ["bi-eye"])
check("Expenses List", "http://localhost:5000/expenses", ["bi-eye"])
check("Income List", "http://localhost:5000/income", ["bi-eye"])

print("\n── NEW: View Pages ──")
# Get first party ID
r = s.get("http://localhost:5000/parties")
party_match = re.search(r'/parties/(\d+)".*?bi-eye', r.text)
if party_match:
    pid = party_match.group(1)
    check("View Party", f"http://localhost:5000/parties/{pid}", ["Current Balance", "View Statement"])

# Get first item ID
r = s.get("http://localhost:5000/items")
item_match = re.search(r'/items/(\d+)".*?bi-eye', r.text)
if item_match:
    iid = item_match.group(1)
    check("View Item", f"http://localhost:5000/items/{iid}", ["Product Details", "Pricing", "Stock", "Total Sold"])

# Get first expense ID
r = s.get("http://localhost:5000/expenses")
exp_match = re.search(r'/expenses/(\d+)".*?bi-eye', r.text)
if exp_match:
    eid = exp_match.group(1)
    check("View Expense", f"http://localhost:5000/expenses/{eid}", ["Expense Details"])

# Get first income ID
r = s.get("http://localhost:5000/income")
inc_match = re.search(r'/income/(\d+)".*?bi-eye', r.text)
if inc_match:
    iid2 = inc_match.group(1)
    check("View Income", f"http://localhost:5000/income/{iid2}", ["Income Details"])

print("\n── NEW: Invoice Payment History ──")
# Find an invoice with payments
r = s.get("http://localhost:5000/sales")
inv_match = re.search(r'/sales/(\d+)".*?badge-partial', r.text)
if not inv_match:
    inv_match = re.search(r'/sales/(\d+)"', r.text)
if inv_match:
    inv_id = inv_match.group(1)
    resp = check("Invoice View + Payment History", f"http://localhost:5000/sales/{inv_id}",
           ["Payment History", "clock-history"])

print("\n── NEW: Day Book Report ──")
check("Reports Index (Day Book link)", "http://localhost:5000/reports", ["daybook"])
check("Day Book (today)", "http://localhost:5000/reports/daybook",
      ["Day Book", "Total Inflow", "Total Outflow", "Net Cash Flow"])
check("Day Book (March 15)", "http://localhost:5000/reports/daybook?date=2026-03-15",
      ["Day Book", "transactions"])

print("\n── NEW: Graphical Analytics Dashboard ──")
r2 = check("Analytics Dashboard", "http://localhost:5000/analytics",
      ["Analytics Dashboard", "monthlyChart", "profitChart", "expensePieChart",
       "statusChart", "paymentChart", "customerChart", "itemChart",
       "stockCatChart", "receivableChart", "expenseTrendChart",
       "Monthly Sales vs Purchases", "Top Customers", "Top Selling Items"])

print("\n── Sidebar Navigation ──")
r3 = s.get("http://localhost:5000/dashboard")
check_nav = "Analytics" in r3.text and "reports.analytics" in r3.text.replace("&#39;", "'").replace("&quot;", '"') or "analytics" in r3.text
if check_nav:
    passed += 1
    print("  ✅ Analytics link in sidebar")
else:
    failed += 1
    print("  ❌ Analytics link in sidebar")

print(f"\n{'='*50}")
print(f"  TOTAL: {passed + failed} checks | ✅ {passed} PASSED | ❌ {failed} FAILED")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
