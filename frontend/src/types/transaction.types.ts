export enum TransactionStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  FAILED = "failed",
  COMPLETED = "COMPLETED",
}

export enum TransactionType {
  TRANSFER = "transfer",
  SWAP = "swap",
  MINT = "mint",
  BURN = "burn",
  STAKE = "stake",
  CONTRACT_CALL = "contract_call",
  DEPOSIT = "DEPOSIT",
  WITHDRAWAL = "WITHDRAWAL",
  ESCROW = "ESCROW",
}

export interface Transaction {
  id: string;
  transaction_id: string;
  transaction_hash: string;
  transaction_type: string;
  amount?: number | null;
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
  metadata?: Record<string, any> | null;
  transaction_category?: string | null;
  
  // Timestamps
  created_at?: string | null;
  updated_at?: string | null;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  page_size: number;
}

export interface TransactionFilters {
  chain?: string;
  risk_level?: string;
  label?: string;
  from?: string;
  to?: string;
  assets?: string[];
  tx_time_start?: string;
  tx_time_end?: string;
  last_screening_start?: string;
  last_screening_end?: string;
  screen_time_start?: string;
  screen_time_end?: string;
  has_unresolved_alerts?: boolean;
  has_note?: boolean;
}
