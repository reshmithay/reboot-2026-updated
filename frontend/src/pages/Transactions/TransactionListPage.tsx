import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DataTable, Pagination } from "../../components/Common/DataTable";
import { StatusBadge } from "../../components/Common/Badges";
import { FilterDropdown } from "../../components/Common/SearchBar";
import { Transaction, TransactionFilters } from "../../types/transaction.types";
import transactionService from "../../services/transaction/transactionService";
import anomalyService from "../../services/anomaly/anomalyService";
import { message, Dropdown } from "antd";
import type { MenuProps } from "antd";

const TransactionListPage: React.FC = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<TransactionFilters>({});
  const [screeningHash, setScreeningHash] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        setApiError(null);

        // Currently backend supports page/page_size/is_anomaly/chain_id filters.
        const response = await transactionService.list({
          page: currentPage,
          page_size: pageSize,
        });

        setTransactions(response.items || []);
        setTotalTransactions(response.total || 0);
      } catch (error: any) {
        const errMsg = error?.message || "Failed to load transactions from server";
        setApiError(errMsg);
        setTransactions([]);
        setTotalTransactions(0);
        message.error(errMsg);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [currentPage, pageSize]);

  const handleScreenTransaction = async (transaction: Transaction) => {
    try {
      setScreeningHash(transaction.transaction_hash);
      const detectMessage = message.loading("Detecting anomalies...", 0);

      // Call anomaly detection API
      await anomalyService.detect(transaction.transaction_hash, false);

      detectMessage();
      message.success("Anomaly detection completed");

      // Navigate to anomaly details page using transaction hash
      navigate(`/narrative/${transaction.transaction_hash}`);
    } catch (error: any) {
      console.error("Failed to screen transaction:", error);
      const errorMessage = error.response?.data?.detail || error.message || "Failed to detect anomaly";
      message.error(errorMessage);
    } finally {
      setScreeningHash(null);
    }
  };

  // Filter options
  const chainOptions = [
    { label: "Hyperledger Fabric", value: "hyperledger" },
    { label: "Ethereum", value: "ethereum" },
    { label: "Polygon", value: "polygon" },
  ];

  const riskLevelOptions = [
    { label: "Critical", value: "critical" },
    { label: "High", value: "high" },
    { label: "Medium", value: "medium" },
    { label: "Low", value: "low" },
  ];

  // Server-side pagination values
  const totalPages = Math.max(1, Math.ceil(totalTransactions / pageSize));

  // Table columns
  const columns = [
    {
      key: "transaction_hash",
      header: "Tx Hash",
      render: (tx: Transaction) => (
        <div className="flex items-center gap-2">
          <input type="checkbox" className="rounded border-gray-300" />
          <span className="font-mono text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
            {tx.transaction_hash.substring(0, 12)}...
          </span>
        </div>
      ),
    },
    {
      key: "onchain_status",
      header: "Onchain status",
      render: (tx: Transaction) => {
        // Mock risk data based on amount
        const status = tx.on_chain_status || 'UNKNOWN';
        
      
        return (
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <StatusBadge
                status={status}
              />
            </div>
          </div>
        );
      },
    },
    {
      key: "direction",
      header: "Direction",
      render: (tx: Transaction) => {
        const type = tx.transaction_type.toLowerCase();
        if (type.includes("deposit")) {
          return (
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <svg
                className="h-4 w-4 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                />
              </svg>
              Deposit
            </div>
          );
        } else if (type.includes("withdrawal")) {
          return (
            <div className="flex items-center gap-2 text-sm text-gray-700">
              <svg
                className="h-4 w-4 text-orange-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                />
              </svg>
              Withdrawal
            </div>
          );
        }
        return (
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <svg
              className="h-4 w-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
              />
            </svg>
            Both Direction
          </div>
        );
      },
    },
    {
      key: "trasaction_timestamp",
      header: "Transaction Time",
      render: (tx: Transaction) => {
           return (
          <span className="text-sm text-gray-900">
            {tx.transaction_timestamp ? new Date(tx.transaction_timestamp).toLocaleString() : "-"}
          </span>
        );
      },
    },
    // {
    //   key: "value",
    //   header: "Value (USD)",
    //   render: (tx: Transaction) => (
    //     <span className="text-sm font-medium text-gray-900">
    //       ${(tx.amount || 0).toLocaleString()}
    //     </span>
    //   ),
    // },
    {
      key: "amount",
      header: "Amount",
      render: (tx: Transaction) => (
        <div className="text-sm text-gray-900">
          <div>{(tx.amount || 0).toLocaleString()}</div>
        </div>
      ),
    },
    {
      key: "assets",
      header: "Assets",
      render: (tx: Transaction) => (
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs">
            {tx.currency.substring(0, 1)}
          </div>
          <span className="text-sm text-gray-900">{tx.currency}</span>
        </div>
      ),
    },
    {
      key: "from",
      header: "From",
      render: (tx: Transaction) => (
        <span className="text-sm font-mono text-gray-600">
          {tx.from_wallet_address || "-"}
        </span>
      ),
    },
    {
      key: "to",
      header: "To",
      render: (tx: Transaction) => (
        <span className="text-sm font-mono text-gray-600">
          {tx.to_wallet_address || "-"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (tx: Transaction) => {
        const menuItems: MenuProps["items"] = [
          {
            key: "screen",
            label: screeningHash === tx.transaction_hash ? (
              <div className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Screening...</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span>Screen</span>
              </div>
            ),
            disabled: screeningHash === tx.transaction_hash,
          },
        ];

        const handleMenuClick: MenuProps["onClick"] = ({ key, domEvent }) => {
          domEvent.stopPropagation();
          if (key === "screen") {
            handleScreenTransaction(tx);
          }
        };

        return (
          <Dropdown
            menu={{ items: menuItems, onClick: handleMenuClick }}
            trigger={["click"]}
            placement="bottomRight"
          >
            <button
              onClick={(e) => e.stopPropagation()}
              className="inline-flex items-center justify-center p-2 text-gray-500 hover:text-gray-700 rounded transition-colors"
            >
              <svg
                className="h-5 w-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 8c1.1 0 2-0.9 2-2s-0.9-2-2-2-2 0.9-2 2 0.9 2 2 2zm0 2c-1.1 0-2 0.9-2 2s0.9 2 2 2 2-0.9 2-2-0.9-2-2-2zm0 6c-1.1 0-2 0.9-2 2s0.9 2 2 2 2-0.9 2-2-0.9-2-2-2z" />
              </svg>
            </button>
          </Dropdown>
        );
      },
    },
  ];

  const handleRowClick = (transaction: Transaction) => {
    navigate(`/narrative/${transaction.transaction_id}`);
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                View Transactions
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Centralized transaction insights for faster risk review.
              </p>
            </div>
            {/* <button className="text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Screen Transaction
            </button> */}
          </div>

          <div className="text-sm text-gray-600">
            Access all screened transactions in one unified interface. Quickly review{" "}
            <span className="font-medium">risk levels</span> and{" "}
            <span className="font-medium">summaries</span>, manage{" "}
            <span className="font-medium">labels</span>, and streamline workflows with
            bulk transaction management.
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filters and Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Transaction</h2>
              {/* <div className="flex items-center gap-2">
                <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                  Re-screen
                </button>
                <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                  KYT Report
                </button>
                <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                  STR Report
                </button>
                <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                  Add to Customer
                </button>
                <button className="px-3 py-2 text-sm font-medium text-red-700 border border-gray-300 rounded-md">
                  Delete
                </button>
              </div> */}
            </div>

            <div className="flex items-center gap-3 hidden">
              <FilterDropdown
                label="Chain"
                options={chainOptions}
                selected={filters.chain}
                onSelect={(value) => setFilters({ ...filters, chain: value })}
                className="w-48"
              />
              <FilterDropdown
                label="Risk Level"
                options={riskLevelOptions}
                selected={filters.risk_level}
                onSelect={(value) => setFilters({ ...filters, risk_level: value })}
                className="w-48"
              />
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md flex items-center gap-2"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                  />
                </svg>
                More Filters (3)
              </button>
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 text-sm font-medium"
              >
                Clear All Filters
              </button>
            </div>
          </div>

          {/* Table */}
          {loading && (
            <div className="px-4 py-3 text-sm text-gray-600">Loading transactions...</div>
          )}
          {apiError && (
            <div className="mx-4 mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              Unable to fetch transactions from API: {apiError}
            </div>
          )}
          <DataTable
            data={transactions}
            columns={columns}
            onRowClick={handleRowClick}
            pagination={false}
            emptyMessage={
              apiError
                ? "Server unavailable. Start backend to load transactions."
                : "No transactions found. Try adjusting your filters."
            }
          />

          {/* Pagination */}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalTransactions}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
            onPageSizeChange={(size) => {
              setPageSize(size);
              setCurrentPage(1); // Reset to page 1 when changing page size
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default TransactionListPage;
