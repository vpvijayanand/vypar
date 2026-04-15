# Vypar - GST Billing & Accounting (Flutter Mobile App)

A beautiful, modern Flutter Android app for the **Vypar** GST Billing & Accounting platform. Connects to the Flask backend API for complete business management.

## Features

- 🔐 **Authentication** — Secure JWT-based login
- 📊 **Dashboard** — KPI cards, sales charts, low stock alerts
- 🧾 **Sales Invoices** — Create, view, manage invoices with GST
- 🛒 **Purchases** — Record purchase bills from suppliers
- 📦 **Inventory** — Manage items, stock levels, barcode scanning
- 👥 **Parties** — Customer & supplier management
- 💰 **Expenses & Income** — Track business expenses and other income
- 📈 **Reports** — Profit & Loss, Party Statement, GSTR-1
- 🏦 **Bank & Cash** — Bank accounts, cheques, loans
- ⚙️ **Settings** — Company profile, GST details, bank info
- 📱 **Barcode Scanner** — Scan barcodes to add items to invoices

## Tech Stack

- **Flutter 3.x** — Cross-platform UI framework
- **Dart** — Programming language
- **Provider** — State management
- **Dio** — HTTP client with interceptors
- **fl_chart** — Beautiful charts
- **Material Design 3** — Modern UI components
- **Google Fonts (Inter)** — Clean typography

## Prerequisites

- Flutter SDK 3.x+
- Android SDK
- Vypar Flask backend running (localhost:5000)

## Setup

```bash
# Install dependencies
flutter pub get

# Run on Android emulator
flutter run

# Build APK
flutter build apk --debug
```

## Project Structure

```
lib/
├── config/           # App config, theme
├── providers/        # State management (AuthProvider)
├── services/         # API service (Dio)
├── utils/            # Formatters (INR, dates)
├── widgets/          # Reusable widgets
├── screens/
│   ├── auth/         # Login screen
│   ├── home/         # Bottom nav, more menu
│   ├── dashboard/    # Dashboard with charts
│   ├── sales/        # Sales list, detail, create
│   ├── purchases/    # Purchase list, detail, create
│   ├── items/        # Item list, detail, create/edit
│   ├── parties/      # Party list, detail, create/edit
│   ├── expenses/     # Expenses & income
│   ├── reports/      # P&L, party statement, GSTR-1
│   ├── bank/         # Bank accounts, cheques, loans
│   └── settings/     # Company settings
└── main.dart         # App entry point
```

## Backend API

The app connects to the Flask backend at `http://10.0.2.2:5000` (Android emulator → host localhost).

**Login:** `admin` / `admin123`
