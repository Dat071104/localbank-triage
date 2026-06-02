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
