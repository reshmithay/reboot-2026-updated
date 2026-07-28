---
name: react-frontend
description: "Use when working on React, TypeScript, Vite frontend code, UI components, services, routing, or client-side state management in the frontend/ directory"
user-invocable: true
---

# React Frontend Development Skill

You are an expert in React 18, TypeScript, and Vite for this anomaly detection dashboard.

## Project Context

- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS (dark theme, utility-first)
- **Routing**: React Router v6
- **HTTP Client**: Axios (via `axiosClient.ts`)
- **State**: Zustand + TanStack Query
- **Web3**: Ethers.js for blockchain wallet integration
- **Charts**: Recharts for anomaly/risk visualization

## Directory Structure

```
frontend/src/
├── pages/          # Route components (Dashboard, Transactions, Anomalies, Narrative)
├── components/     # Reusable UI (Charts, Alerts, Wallet, Tables, Common)
├── services/       # API service layer (anomaly, transaction, narrative, blockchain)
├── clients/        # HTTP/WebSocket/Firebase/Web3 clients
├── utilities/      # Helpers, formatters, validators, constants
├── hooks/          # Custom React hooks
├── context/        # React context providers
├── store/          # Zustand state stores
├── routes/         # Route configuration
└── layouts/        # Page layouts
```

## Code Patterns

### API Service Pattern
```typescript
// services/anomaly/anomalyService.ts
import apiClient from "@/clients/api/axiosClient";

const anomalyService = {
  detect: (txId: string) => 
    apiClient.post("/api/v1/anomalies/detect", { transaction_id: txId })
      .then(r => r.data),
};
```

### Component Pattern
```typescript
// pages/Dashboard/Dashboard.tsx
import React, { useEffect, useState } from "react";
import anomalyService, { AnomalyStats } from "@/services/anomaly/anomalyService";

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<AnomalyStats | null>(null);
  
  useEffect(() => {
    anomalyService.getStats().then(setStats);
  }, []);
  
  return <div className="min-h-screen bg-gray-950 text-gray-100 p-8">...</div>;
};
```

### Utility Pattern
```typescript
// utilities/formatters/riskFormatter.ts
export const getRiskColor = (score: number): string => {
  if (score >= 90) return "#ef4444"; // critical
  if (score >= 75) return "#f97316"; // high
  return "#22c55e"; // low
};
```

## Operating Rules

1. **Types First**: Define TypeScript interfaces for all API responses, props, and state
2. **Tailwind Only**: No inline styles, use Tailwind utility classes
3. **Dark Theme**: Use gray-950/900/800 backgrounds, gray-100 text
4. **Error Handling**: Wrap API calls in try/catch, show user-friendly error messages
5. **Loading States**: Always show loading/skeleton UI during async operations
6. **Responsive**: Mobile-first, use Tailwind responsive prefixes (md:, lg:)
7. **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation
8. **Code Splitting**: Lazy load heavy components and routes

## Common Tasks

### Adding a New Page
1. Create component in `pages/YourPage/YourPage.tsx`
2. Add route in `App.tsx`
3. Create service in `services/yourFeature/yourService.ts` if needed
4. Add link in navigation/sidebar

### Adding an API Integration
1. Define TypeScript interface for response
2. Create service method using `apiClient`
3. Use TanStack Query for caching: `useQuery(['key'], fetchFn)`

### Adding a Chart
1. Import Recharts components: `import { LineChart, Line, XAxis, ... } from "recharts"`
2. Use project color constants: `CHART_COLORS`, `SEVERITY_COLORS`
3. Ensure dark theme compatibility

### Web3 Wallet Integration
1. Use ethers.js: `import { BrowserProvider } from "ethers"`
2. Handle wallet connection state
3. Read from smart contracts using ABIs from `blockchain/artifacts/`

## Anti-patterns

- ❌ Don't use `any` type — always define proper interfaces
- ❌ Don't fetch data in render — use `useEffect` or TanStack Query
- ❌ Don't mutate state directly — use `setState` functions
- ❌ Don't put business logic in components — extract to services
- ❌ Don't hardcode API URLs — use environment variables (`import.meta.env.VITE_*`)

## Validation

After changes:
1. Run `npm run type-check` to verify TypeScript
2. Run `npm run lint` to check code quality
3. Test in browser at `http://localhost:5173`
