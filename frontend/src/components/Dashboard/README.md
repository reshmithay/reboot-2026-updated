# Dashboard Component Structure

This document explains the refactored Dashboard implementation following React best practices.

## File Structure

```
frontend/src/
├── pages/Dashboard/
│   └── Dashboard.tsx                          # Main dashboard page (orchestrator)
├── components/Dashboard/
│   ├── StatisticsCards.tsx                    # Top statistics cards
│   ├── AnomaliesOverTimeChart.tsx             # Time series chart
│   ├── AnomaliesByCategoryChart.tsx           # Category pie chart
│   ├── RiskScoreDistributionChart.tsx         # Risk distribution chart
│   ├── RecentAlertsTable.tsx                  # Alerts table
│   └── TopAlertedEntities.tsx                 # Top entities list
├── hooks/
│   └── useDashboardData.ts                    # Custom hook for data fetching
├── utils/
│   └── dashboardUtils.ts                      # Data transformation utilities
└── constants/
    └── dashboardConstants.ts                  # Color schemes and constants
```

## Architecture Principles

### 1. **Separation of Concerns**
- **Pages**: Orchestration layer that composes components
- **Components**: Presentational components with single responsibilities
- **Hooks**: Data fetching and state management logic
- **Utils**: Pure functions for data transformation
- **Constants**: Configuration and theme values

### 2. **Custom Hook Pattern**
`useDashboardData.ts` encapsulates:
- API calls (stats, anomalies, transactions)
- Loading states
- Error handling
- Data caching

### 3. **Pure Utility Functions**
`dashboardUtils.ts` provides:
- Data transformation functions
- Type definitions
- Business logic helpers
- All functions are pure (no side effects)

### 4. **Reusable Components**
Each chart/widget is self-contained:
- Accepts data via props
- No direct API calls
- Easy to test and reuse
- Clear interfaces

### 5. **Constants Management**
`dashboardConstants.ts` centralizes:
- Color palettes
- Chart colors
- Background colors
- Theme tokens

## Component Responsibilities

### Dashboard.tsx (Main Page)
- Fetches data using `useDashboardData` hook
- Transforms data using utility functions
- Composes child components
- Handles layout and spacing
- ~60 lines vs. ~650 lines originally

### StatisticsCards.tsx
- Displays 5 stat cards
- Configurable data-driven approach
- Consistent styling
- Icon and color management

### Chart Components
Each chart component:
- Receives transformed data
- Renders visualization
- Handles its own styling
- Self-contained and testable

### Table Components
- Column configuration
- Data rendering
- Action handlers
- Navigation logic

## Benefits of This Structure

### ✅ Maintainability
- Easy to locate and update specific features
- Clear component boundaries
- Single Responsibility Principle

### ✅ Testability
- Pure functions are easily testable
- Components can be tested in isolation
- Mock data is simple to provide

### ✅ Reusability
- Charts can be used in other dashboards
- Utility functions shared across features
- Custom hook can be extended

### ✅ Scalability
- Easy to add new widgets
- Simple to modify existing charts
- Clear extension points

### ✅ Developer Experience
- Faster navigation to specific code
- Easier onboarding for new developers
- Better IDE autocomplete and navigation

## Data Flow

```
API Calls (useDashboardData)
    ↓
Raw Data (stats, anomalies, transactions)
    ↓
Transformation (dashboardUtils)
    ↓
Transformed Data (chart-ready format)
    ↓
Components (render visualizations)
```

## Usage Example

```typescript
// Simple, declarative usage in Dashboard.tsx
const Dashboard: React.FC = () => {
  const { stats, recentAnomalies, transactionCount, loading } = useDashboardData();
  
  const chartData = transformAnomaliesOverTime(recentAnomalies);
  
  return <AnomaliesOverTimeChart data={chartData} />;
};
```

## Adding New Features

### To add a new chart:
1. Create component in `components/Dashboard/NewChart.tsx`
2. Add transformation function in `utils/dashboardUtils.ts`
3. Import and use in `pages/Dashboard/Dashboard.tsx`

### To add new data source:
1. Add API call to `useDashboardData` hook
2. Add transformation logic to `dashboardUtils`
3. Pass to relevant components

### To add new constants:
1. Add to `constants/dashboardConstants.ts`
2. Import where needed

## Performance Considerations

- All components use React.FC for type safety
- Data transformations are memoizable
- Charts use ResponsiveContainer for performance
- Loading states prevent unnecessary renders

## Type Safety

All components have:
- Explicit prop interfaces
- TypeScript types from shared types
- No `any` types (except for Ant Design callbacks)
- Proper generics usage

## Code Quality

- **DRY**: No repeated code
- **SOLID**: Single responsibility, clear interfaces
- **Clean Code**: Self-documenting function names
- **Consistent**: Follows React conventions
