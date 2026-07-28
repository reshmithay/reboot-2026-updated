import React, { useState, useEffect } from "react";
import { DataTable, Pagination } from "../../components/Common/DataTable";
import { RiskBadge, StatusBadge } from "../../components/Common/Badges";
import { FilterDropdown, SearchBar } from "../../components/Common/SearchBar";
import { ClientRegistry } from "../../types/client.types";
import clientService from "../../services/client/clientService";
import { format } from "date-fns";

const ClientListPage: React.FC = () => {
  const [clients, setClients] = useState<ClientRegistry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<{
    risk_tier?: string;
    client_type?: string;
    kyc_status?: string;
  }>({});

  // Fetch clients from API
  useEffect(() => {
    const fetchClients = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await clientService.list({
          page: currentPage,
          page_size: pageSize,
          risk_tier: filters.risk_tier,
          client_type: filters.client_type,
          kyc_status: filters.kyc_status,
          search: searchQuery || undefined,
        });
        setClients(response.items);
        setTotal(response.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch clients");
        console.error("Failed to fetch clients:", err);
      } finally {
        setLoading(false);
      }
    };

    // Debounce search
    const timeoutId = setTimeout(() => {
      fetchClients();
    }, searchQuery ? 300 : 0);

    return () => clearTimeout(timeoutId);
  }, [currentPage, pageSize, filters, searchQuery]);

  // Filter options
  const riskTierOptions = [
    { label: "All", value: "" },
    { label: "Low", value: "Low" },
    { label: "Medium", value: "Medium" },
    { label: "High", value: "High" },
  ];

  const clientTypeOptions = [
    { label: "All", value: "" },
    { label: "Corporate", value: "Corporate" },
    { label: "Enterprise", value: "Enterprise" },
    { label: "Startup", value: "Startup" },
  ];

  const kycStatusOptions = [
    { label: "All", value: "" },
    { label: "Verified", value: "Verified" },
    { label: "Pending", value: "Pending" },
    { label: "Expired", value: "Expired" },
  ];

  const totalPages = Math.ceil(total / pageSize);

  // Table columns
  const columns = [
    {
      key: "client_id",
      header: "Client ID",
      render: (client: ClientRegistry) => (
        <span className="font-mono text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
          {client.client_id}
        </span>
      ),
    },
    {
      key: "client_name",
      header: "Client Name",
      render: (client: ClientRegistry) => (
        <div>
          <div className="text-sm font-medium text-gray-900">
            {client.client_name}
          </div>
          <div className="text-xs text-gray-500">{client.client_type}</div>
        </div>
      ),
    },
    {
      key: "risk_tier",
      header: "Risk Tier",
      render: (client: ClientRegistry) => (
        <RiskBadge severity={client.risk_tier || "LOW"} />
      ),
    },
    {
      key: "industry_sector",
      header: "Industry",
      render: (client: ClientRegistry) => (
        <span className="text-sm text-gray-900">
          {client.industry_sector || "-"}
        </span>
      ),
    },
    {
      key: "country",
      header: "Country",
      render: (client: ClientRegistry) => (
        <span className="text-sm text-gray-900">
          {client.country_of_incorporation || "-"}
        </span>
      ),
    },
    {
      key: "credit_limit",
      header: "Credit Limit",
      render: (client: ClientRegistry) => (
        <span className="text-sm font-medium text-gray-900">
          ₹{client.credit_limit.toLocaleString()}
        </span>
      ),
    },
    {
      key: "kyc_status",
      header: "KYC Status",
      render: (client: ClientRegistry) => (
        <StatusBadge status={client.kyc_status || "Pending"} />
      ),
    },
    {
      key: "aml_status",
      header: "AML Status",
      render: (client: ClientRegistry) => (
        <StatusBadge status={client.aml_status || "Pending"} />
      ),
    },
    {
      key: "relationship_manager",
      header: "RM",
      render: (client: ClientRegistry) => (
        <span className="text-sm text-gray-900">
          {client.relationship_manager || "-"}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Created At",
      render: (client: ClientRegistry) => (
        <span className="text-sm text-gray-600">
          {client.created_at
            ? format(new Date(client.created_at), "MMM dd, yyyy")
            : "-"}
        </span>
      ),
    },
  ];

  const handleRowClick = (client: ClientRegistry) => {
    console.log("Selected client:", client);
    // Navigate to client profile page
    window.location.href = `/clients/${client.client_id}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Client Registry</h1>
              <p className="text-sm text-gray-600 mt-1">
                Manage and monitor all registered clients
              </p>
            </div>
            <button className="text-white hidden px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
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
              Add New Client
            </button>
          </div>

          <SearchBar
            placeholder="Search by client name or ID..."
            onSearch={(value) => {
              setSearchQuery(value);
              setCurrentPage(1);
            }}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-sm text-gray-600">Loading clients...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && !error && (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">Total Clients</div>
                <div className="text-2xl font-bold text-gray-900">{total}</div>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">High Risk</div>
                <div className="text-2xl font-bold text-red-600">
                  {clients.filter((c) => c.risk_tier === "High").length}
                </div>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">KYC Verified</div>
                <div className="text-2xl font-bold text-green-600">
                  {clients.filter((c) => c.kyc_status === "Verified").length}
                </div>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">Total Credit</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(clients.reduce((sum, c) => sum + c.credit_limit, 0) / 10000000).toFixed(1)}Cr
                </div>
              </div>
            </div>

        {/* Filters and Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Clients</h2>
              <div className="flex hidden items-center gap-2">
                <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                  Export
                </button>
                <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                  Bulk Update
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3 mb-4">
              <FilterDropdown
                label="Risk Tier"
                options={riskTierOptions}
                selected={filters.risk_tier}
                onSelect={(value) => {
                  setFilters({ ...filters, risk_tier: value || undefined });
                  setCurrentPage(1);
                }}
                className="w-48"
              />
              <FilterDropdown
                label="Client Type"
                options={clientTypeOptions}
                selected={filters.client_type}
                onSelect={(value) => {
                  setFilters({ ...filters, client_type: value || undefined });
                  setCurrentPage(1);
                }}
                className="w-48"
              />
              <FilterDropdown
                label="KYC Status"
                options={kycStatusOptions}
                selected={filters.kyc_status}
                onSelect={(value) => {
                  setFilters({ ...filters, kyc_status: value || undefined });
                  setCurrentPage(1);
                }}
                className="w-48"
              />
              <button
                onClick={() => {
                  setFilters({});
                  setCurrentPage(1);
                }}
                className="px-4 py-2 text-sm font-medium"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Table */}
          <DataTable
            data={clients}
            columns={columns}
            pagination={false}
            onRowClick={handleRowClick}
            emptyMessage="No clients found. Try adjusting your search or filters."
          />

          {/* Pagination */}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={total}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
          />
        </div>
        </>
        )}
      </div>
    </div>
  );
};

export default ClientListPage;
