"""Quick test: all pages, CSV downloads, PDF generation."""
import requests

s = requests.Session()
r = s.post('http://localhost:5000/auth/login',
           data={'username': 'admin', 'password': 'admin123'}, allow_redirects=False)
print(f'Login: {r.status_code} (302=OK)')

pages = [
    ('Dashboard', '/dashboard'),
    ('Sales List', '/sales'),
    ('Sales Create', '/sales/create'),
    ('Purchases List', '/purchases'),
    ('Purchases Create', '/purchases/create'),
    ('Parties List', '/parties'),
    ('Party Create', '/parties/create'),
    ('Items List', '/items'),
    ('Item Create', '/items/create'),
    ('Expenses List', '/expenses'),
    ('Expense Create', '/expenses/create'),
    ('Income List', '/income'),
    ('Income Create', '/income/create'),
    ('Bank List', '/bank'),
    ('Bank Create', '/bank/create'),
    ('Cash In Hand', '/cash'),
    ('Cheques', '/cheques'),
    ('Cheque Create', '/cheques/create'),
    ('Loan Create', '/loans/create'),
    ('Reports Index', '/reports'),
    ('Sales Report', '/reports/sales?from_date=2026-03-01&to_date=2026-03-31'),
    ('Purchases Report', '/reports/purchases?from_date=2026-03-01&to_date=2026-03-31'),
    ('Party Statement', '/reports/party-statement'),
    ('Profit Loss', '/reports/profit-loss?start=2026-03-01&end=2026-03-31'),
    ('GSTR-1', '/reports/gstr1?start=2026-03-01&end=2026-03-31'),
    ('Settings', '/settings'),
    ('Company Profile', '/settings/company'),
    ('Create User', '/settings/users/create'),
]

ok = 0
fail = 0
for name, url in pages:
    r = s.get(f'http://localhost:5000{url}', timeout=10)
    if r.status_code == 200:
        ok += 1
    else:
        fail += 1
        print(f'  FAIL {name}: {r.status_code}')
print(f'\nPAGES: {ok}/{ok + fail} OK')

# CSV downloads
csv_urls = [
    ('Sales CSV', '/sales/csv'),
    ('Purchases CSV', '/purchases/csv'),
    ('Expenses CSV', '/expenses/csv'),
    ('Income CSV', '/income/csv'),
    ('Parties CSV', '/parties/csv'),
    ('Items CSV', '/items/csv'),
    ('Cheques CSV', '/cheques/csv'),
    ('Sales Report CSV', '/reports/sales/csv?from_date=2026-03-01&to_date=2026-03-31'),
    ('Purchases Report CSV', '/reports/purchases/csv?from_date=2026-03-01&to_date=2026-03-31'),
    ('P&L CSV', '/reports/profit-loss/csv?start=2026-03-01&end=2026-03-31'),
    ('GSTR1 CSV', '/reports/gstr1/csv?start=2026-03-01&end=2026-03-31'),
]

cok = 0
cfail = 0
for name, url in csv_urls:
    r = s.get(f'http://localhost:5000{url}', timeout=10)
    is_csv = 'text/csv' in r.headers.get('Content-Type', '')
    if r.status_code == 200 and is_csv:
        cok += 1
    else:
        cfail += 1
        print(f'  FAIL {name}: {r.status_code} csv={is_csv}')
print(f'CSV DOWNLOADS: {cok}/{cok + cfail} OK')

# PDF generation
r = s.get('http://localhost:5000/sales/1/pdf', timeout=10)
p1 = r.status_code == 200 and 'pdf' in r.headers.get('Content-Type', '')
print(f'Invoice PDF: {"OK" if p1 else "FAIL " + str(r.status_code)}')

r = s.get('http://localhost:5000/purchases/1/pdf', timeout=10)
p2 = r.status_code == 200 and 'pdf' in r.headers.get('Content-Type', '')
print(f'Purchase PDF: {"OK" if p2 else "FAIL " + str(r.status_code)}')

# View individual invoice/purchase (with seed data)
r1 = s.get('http://localhost:5000/sales/1', timeout=10)
r2 = s.get('http://localhost:5000/purchases/1', timeout=10)
v1 = r1.status_code == 200
v2 = r2.status_code == 200
print(f'View Invoice: {"OK" if v1 else "FAIL " + str(r1.status_code)}')
print(f'View Purchase: {"OK" if v2 else "FAIL " + str(r2.status_code)}')

total = ok + cok + (1 if p1 else 0) + (1 if p2 else 0) + (1 if v1 else 0) + (1 if v2 else 0)
mx = (ok + fail) + (cok + cfail) + 4
print(f'\n{"=" * 50}')
print(f'TOTAL: {total}/{mx} PASSED')
print(f'{"=" * 50}')
