# LocalBank Triage Frontend

React + TypeScript + Vite local staff workspace for Phase 10 and the Tauri shell in Phase 11.

## PowerShell

```powershell
cd "D:\Project cua Dat\Localbank-triage\frontend-app"
npm install
npm run dev
npm run test
npm run test:e2e
npm run build
```

Mock mode is the default:

```powershell
$env:VITE_API_MODE="mock"
npm run dev
```

Real gateway mode targets the Phase 1-9 local stack:

```powershell
$env:VITE_API_MODE="real"
$env:VITE_GATEWAY_BASE_URL="http://localhost:8005"
$env:VITE_AUTH_SERVICE_URL="http://localhost:8000"
npm run dev
```

The UI does not send customer text outside the configured local services. Audit logs are visible only to supervisor, auditor, and admin roles. CS agents cannot approve HIGH or CRITICAL drafts.

## Desktop shell

The Tauri desktop shell uses the same Vite build output and does not bundle backend services. Start the local backend stack separately for real mode, or use default mock mode for a desktop demo.

```powershell
cd "D:\Project cua Dat\Localbank-triage\frontend-app"
npm run tauri:dev
npm run tauri:build
```

Windows prerequisites for full packaging:

- Rust and Cargo installed and on `PATH`
- Microsoft Edge WebView2 Runtime
- Windows build tools required by Rust/Tauri

If Rust/Cargo is absent, `npm run tauri:build` cannot produce an installer; the browser build and Tauri config smoke tests still validate package readiness.
