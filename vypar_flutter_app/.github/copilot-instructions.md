<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Vypar Android - Flutter Mobile App

This is a Flutter Android mobile app for the Vypar GST Billing, Inventory & Accounting system.

## Architecture
- **State Management**: Provider pattern
- **HTTP Client**: Dio with JWT auth interceptor
- **Local Storage**: SharedPreferences for auth tokens
- **Charts**: fl_chart for dashboard analytics
- **Design**: Material Design 3 with Indian business theme

## API Backend
- Flask REST API at `http://10.0.2.2:5000` (Android emulator) or configurable base URL
- JWT token authentication via `Authorization: Bearer <token>` header
- All API endpoints prefixed with `/api/`

## Key Conventions
- Indian Rupee formatting (₹1,23,456.00) using Indian number system
- All monetary values use `double` type
- Date format: dd MMM yyyy for display, yyyy-MM-dd for API
- Color scheme: Indigo primary, professional business theme
