"""Quick test: verify dashboard shows all data sections with non-zero values."""
import requests, re, sys

s = requests.Session()
r = s.post('http://localhost:5000/auth/login',
           data={'username': 'admin', 'password': 'admin123'}, allow_redirects=False)
print(f"Login: {r.status_code}")

r = s.get('http://localhost:5000/dashboard')
html = r.text
print(f"Dashboard: {r.status_code} ({len(html)} bytes)\n")

passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}")

# --- Page sections present ---
print("── Page Sections ──")
check("Total Sales (Month) card", "Total Sales (Month)" in html)
check("Total Purchases (Month) card", "Total Purchases (Month)" in html)
check("Low Stock Items section", "Low Stock Items" in html)
check("Out of Stock section", "Out of Stock" in html)
check("Top Selling Items section", "Top Selling Items" in html)
check("Daily Sales Chart canvas", "dailySalesChart" in html)
check("Doughnut Chart canvas", "expenseChart" in html)
check("Recent Sales table", "Recent Sales" in html)
check("Recent Purchases table", "Recent Purchases" in html)

# --- Actual invoice data ---
print("\n── Data Present ──")
check("Has INV- invoice rows", "INV-" in html)
check("Has PUR- purchase rows", "PUR-" in html)
check("Out of Stock badge rendered", "Out of Stock</span>" in html)
check("Low stock badge bg-warning", "bg-warning" in html)

# --- Doughnut chart has non-zero values ---
print("\n── Chart Data ──")
m = re.search(r'data:\s*\[([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\]', html)
if m:
    s_val, p_val, e_val = float(m.group(1)), float(m.group(2)), float(m.group(3))
    check(f"Doughnut Sales > 0 (₹{s_val:,.0f})", s_val > 0)
    check(f"Doughnut Purchases > 0 (₹{p_val:,.0f})", p_val > 0)
    check(f"Doughnut Expenses > 0 (₹{e_val:,.0f})", e_val > 0)
else:
    check("Doughnut chart data found", False)

# --- Daily sales chart has data ---
dm = re.search(r'dailyData\s*=\s*(\[.+?\]);', html, re.DOTALL)
if dm:
    import json
    daily = json.loads(dm.group(1))
    check(f"Daily sales has {len(daily)} data points", len(daily) > 0)
    total_daily = sum(d['amount'] for d in daily)
    check(f"Daily sales total > 0 (₹{total_daily:,.0f})", total_daily > 0)
else:
    check("Daily sales data found", False)

# --- Low stock items listed ---
print("\n── Stock Alerts ──")
low_count = len(re.findall(r'bg-warning text-dark">\d+', html))
out_count = html.count('Out of Stock</span>')
check(f"Low stock items shown: {low_count}", low_count > 0)
check(f"Out of stock items shown: {out_count}", out_count > 0)

# --- Top selling items listed ---
top_match = re.findall(r'text-truncate.*?>(.*?)</td>', html)
check(f"Top selling items listed: {len(top_match)}", len(top_match) > 0)

print(f"\n{'='*50}")
print(f"  TOTAL: {passed + failed} checks | ✅ {passed} PASSED | ❌ {failed} FAILED")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
