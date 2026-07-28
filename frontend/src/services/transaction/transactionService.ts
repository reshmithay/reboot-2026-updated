import apiClient from "../../clients/api/axiosClient";

export interface Transaction {
  id: string;
  transaction_id: string;
  transaction_hash: string;
  transaction_type: string;
  amount?: number | null;  // Optional to handle transactions without amounts
  currency: string;
  transaction_timestamp: string;
  transaction_status: string;
  on_chain_status?: string | null;
  
  // Account information
  from_account?: string | null;
  to_account?: string | null;
  from_wallet_address?: string | null;
  to_wallet_address?: string | null;
  wallet_address?: string | null;
  
  // Client information
  client_id?: string | null;
  client_name?: string | null;
  
  // Blockchain details
  blockchain_network?: string | null;
  ledger_type?: string | null;
  chain_id?: number | null;
  block_number?: number | null;
  block_hash?: string | null;
  token_symbol?: string | null;
  
  // Gas and fees
  gas_fee?: number | null;
  gas_price?: number | null;
  
  // Metadata
  correlation_id?: string | null;
  metadata?: any;
  transaction_category?: string | null;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

export interface TransactionIngest {
  tx_hash: string;
  from_address: string;
  to_address: string;
  value: number;
  token_symbol?: string;
  chain_id?: number;
  block_number?: number;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

const transactionService = {
  ingest: (data: TransactionIngest): Promise<Transaction> =>
    apiClient.post("/api/v1/transactions/ingest", data).then((r) => r.data),

  list: (params?: {
    page?: number;
    page_size?: number;
    is_anomaly?: boolean;
    chain_id?: number;
  }): Promise<PaginatedResponse<Transaction>> =>
    apiClient.get("/api/v1/transactions/", { params }).then((r) => r.data),

  getByHash: (txHash: string): Promise<Transaction> =>
    apiClient.get(`/api/v1/transactions/${txHash}`).then((r) => r.data),
  
  getById: (transactionId: string): Promise<Transaction> =>
    apiClient.get(`/api/v1/transactions/${transactionId}`).then((r) => r.data),
};

export default transactionService;
