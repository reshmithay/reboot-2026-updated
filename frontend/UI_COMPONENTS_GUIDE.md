# Blockchain Anomaly AI - Frontend UI Components

This directory contains comprehensive UI components for the Blockchain Anomaly AI compliance and monitoring platform, inspired by the Blocksec Phalcon design.

## 📁 Project Structure

```
frontend/src/
├── components/
│   └── Common/
│       ├── Badges.tsx          # Risk, Status, and Label badges
│       ├── Cards.tsx            # StatCard, InfoCard, DataCard
│       ├── DataTable.tsx        # Reusable data table with pagination
│       ├── Modal.tsx            # Modal and BulkScreeningModal
│       └── SearchBar.tsx        # SearchBar and FilterDropdown
├── pages/
│   ├── Compliance/
│   │   └── ComplianceDashboard.tsx    # Main compliance dashboard
│   ├── Transactions/
│   │   └── TransactionListPage.tsx    # Transaction list with filters
│   ├── Clients/
│   │   ├── ClientListPage.tsx         # Client registry list
│   │   └── ClientProfilePage.tsx      # Client profile with analytics
│   └── Anomalies/
│       └── AnomalyListPage.tsx        # Anomaly detection results
├── types/
│   ├── transaction.types.ts     # Transaction interfaces
│   ├── anomaly.types.ts         # Anomaly interfaces
│   └── client.types.ts          # Client interfaces
└── utilities/
    ├── mockData.ts              # Mock data generators
    └── formatters.ts            # Utility functions for formatting
```

## 🎨 Key Features

### 1. **Compliance Dashboard** (`/compliance`)
- AML/CFT risk screening interface
- Compliance hotspots display
- Latest security insights
- Recent anomaly detections
- Bulk CSV screening capability

### 2. **Transaction List** (`/transactions`)
- Advanced filtering (Chain, Risk Level, Label)
- Multi-column data table
- Risk summary with badges
- Transaction direction indicators
- Pagination and search
- Bulk operations support

### 3. **Client Profile** (`/clients/:id`)
- 360° customer risk view
- Transaction statistics
- Risk distribution pie chart
- Triggered risk engine bar chart
- Recent alerts timeline
- Client information and limits

### 4. **Client Registry** (`/clients`)
- Client list with filtering
- Search by name/ID
- Risk tier classification
- KYC/AML status tracking
- Credit limit overview
- Bulk operations

### 5. **Anomaly Detection** (`/anomalies`)
- Anomaly detection results
- Risk score visualization
- Severity filtering
- Status management
- Confidence metrics
- Assignment tracking

## 🛠️ Reusable Components

### Badges
```tsx
import { RiskBadge, StatusBadge, LabelBadge } from "@/components/Common";

<RiskBadge severity="HIGH" />
<StatusBadge status="CONFIRMED" />
<LabelBadge label="Large Transfer" type="transfer" />
```

### Cards
```tsx
import { StatCard, InfoCard, DataCard } from "@/components/Common";

<StatCard title="Total Transactions" value="1,234" />
<InfoCard title="Recent Activity">{children}</InfoCard>
<DataCard label="Credit Limit" value="₹5,000,000" />
```

### Data Table
```tsx
import { DataTable, Pagination } from "@/components/Common";

const columns = [
  { key: "id", header: "ID", render: (item) => item.id },
  // ... more columns
];

<DataTable data={items} columns={columns} onRowClick={handleClick} />
<Pagination currentPage={1} totalPages={10} onPageChange={setPage} />
```

### Modals
```tsx
import { Modal, BulkScreeningModal } from "@/components/Common";

<BulkScreeningModal
  isOpen={isOpen}
  onClose={handleClose}
  onScreen={handleScreen}
/>
```

## 📊 Data Types

All TypeScript interfaces are defined in the `types/` directory:

- **Transaction**: Complete transaction data model
- **AnomalyResult**: Anomaly detection results
- **ClientRegistry**: Client/customer information
- **TransactionFilters**: Filter criteria for transactions

## 🎨 Design System

### Colors
- **Critical/High Risk**: Red (#DC2626)
- **Medium Risk**: Yellow/Orange (#FACC15, #F97316)
- **Low Risk**: Green (#22C55E)
- **Primary**: Blue (#3B82F6)
- **Text**: Gray scale (#111827, #6B7280, #9CA3AF)

### Typography
- **Headings**: Bold, 2xl/xl/lg
- **Body**: Regular, sm/base
- **Monospace**: Transaction hashes, IDs

## 🚀 Usage

### Running the Development Server

```bash
npm run dev
```

### Building for Production

```bash
npm run build
```

### Type Checking

```bash
npm run type-check
```

## 📝 Notes

- **Static Data**: All pages currently use mock data from `utilities/mockData.ts`
- **No API Integration**: API calls are not yet implemented (ready for integration)
- **Routing**: Update `routes/` to include these new pages
- **Responsive**: All components are mobile-responsive using Tailwind CSS

## 🔄 Next Steps for API Integration

When APIs are ready, update the following:

1. Create API client functions in `services/`
2. Replace mock data imports with API calls
3. Add React Query hooks for data fetching
4. Implement error handling and loading states
5. Add form submission handlers

Example:
```tsx
// Before (static)
import { mockTransactions } from "@/utilities/mockData";
const [transactions] = useState(mockTransactions);

// After (with API)
import { useQuery } from "@tanstack/react-query";
const { data: transactions, isLoading } = useQuery({
  queryKey: ["transactions"],
  queryFn: () => api.getTransactions(),
});
```

## 🎯 Best Practices Implemented

- ✅ TypeScript for type safety
- ✅ Reusable component architecture
- ✅ Consistent design patterns
- ✅ Responsive layouts
- ✅ Accessible UI components
- ✅ Clean code organization
- ✅ Mock data for development
- ✅ Utility functions for common operations

## 📚 Dependencies

- **React**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Recharts**: Data visualization
- **date-fns**: Date formatting
- **clsx**: Conditional classes
- **React Router**: Navigation (to be configured)

---

**Note**: This is a static implementation. All data is mocked for demonstration purposes. Once backend APIs are fully developed, integrate them by replacing mock data with actual API calls.
