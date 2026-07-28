# Anomaly Narrative Page - Component Structure

## Overview
The Anomaly Narrative page has been refactored into a component-based architecture for better maintainability and reusability.

## Folder Structure

```
pages/Narrative/
├── components/           # Reusable UI components
│   ├── AnomalyHeader.tsx
│   ├── TransactionHeaderCard.tsx
│   ├── AIGeneratedNarrative.tsx
│   ├── AnomalyReasonsCard.tsx
│   ├── KeyRiskIndicators.tsx
│   ├── RecommendedActions.tsx
│   ├── TransactionSnapshot.tsx
│   ├── AIConfidence.tsx
│   ├── RiskContribution.tsx
│   ├── InvestigationTimeline.tsx
│   └── index.ts
├── hooks/               # Custom React hooks
│   ├── useAnomalyData.ts
│   ├── useNarrativeAudio.ts
│   └── index.ts
├── constants/           # Static data and configurations
│   ├── narrativeData.tsx
│   ├── narrativeTranslations.ts
│   └── index.ts
├── AnomalyNarrativePage.tsx  # Main page component
└── README.md

```

## Components

### AnomalyHeader
- Back navigation button
- Transaction ID display
- Action buttons (Download, Open Case, More actions)

### TransactionHeaderCard
- Transaction details grid
- Risk score circle progress
- Client and anomaly information

### AIGeneratedNarrative
- Multi-language support
- Role-based narratives (Fraud Analyst, Compliance Officer, etc.)
- Audio playback functionality

### AnomalyReasonsCard
- Displays anomaly reasons from API
- Shows fallback message if no reasons available

### KeyRiskIndicators
- List of risk indicators with severity levels
- Icon-based visual representation

### RecommendedActions
- Priority-based action cards (Immediate, Within 1 Hour, Long Term)
- Color-coded by priority

### TransactionSnapshot
- Transaction type, amount, status
- Blockchain network details
- Wallet addresses

### AIConfidence
- Fraud probability metrics
- Model confidence indicators
- Explainability score

### RiskContribution
- Pie chart showing risk factor distribution
- Percentage breakdown by factor

### InvestigationTimeline
- Chronological event timeline
- Color-coded by event type (normal, warning, error)

## Hooks

### useAnomalyData
- Fetches anomaly and transaction data from APIs
- Manages loading and error states
- Returns: `{ anomaly, transaction, loading, error, transactionId }`

### useNarrativeAudio
- Handles text-to-speech functionality
- Multi-language voice support
- Returns: `{ isPlaying, handlePlayNarrative }`

## Constants

### narrativeData.tsx
- Language options
- Risk indicators
- Risk contribution factors
- Investigation timeline events
- Recommended actions

### narrativeTranslations.ts
- Multi-language narrative content
- Role-based narrative variations

## Usage

```tsx
import AnomalyNarrativePage from "./pages/Narrative/AnomalyNarrativePage";

// In your router
<Route path="/narrative/:transactionId" element={<AnomalyNarrativePage />} />
```

## Benefits of This Structure

1. **Modularity**: Each component has a single responsibility
2. **Reusability**: Components can be used in other pages
3. **Maintainability**: Easier to locate and update specific features
4. **Testability**: Smaller components are easier to test
5. **Scalability**: Easy to add new features or modify existing ones
6. **Code Organization**: Clear separation of concerns (UI, logic, data)
