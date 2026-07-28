export interface ClientRegistry {
  client_id: string;
  client_name: string;
  client_type?: string | null;
  lei?: string | null;
  industry_sector?: string | null;
  country_of_incorporation?: string | null;
  risk_tier?: string | null;
  relationship_manager?: string | null;
  wallet_address?: string | null;
  wallet_type?: string | null;
  facility_type?: string | null;
  credit_limit: number;
  daily_deposit_limit: number;
  daily_withdrawal_limit: number;
  expected_activity_window?: string | null;
  authorized_signatories?: any[] | null;
  kyc_status?: string | null;
  aml_status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ClientRegistryListResponse {
  items: ClientRegistry[];
  total: number;
  page: number;
  page_size: number;
}

export interface ClientProfileStats {
  total_addresses: number;
  balance: number;
  total_inflow: number;
  total_outflow: number;
  total_transaction: number;
  total_value: number;
  total_deposit: number;
  total_withdraw: number;
  unresolved_alerts: number;
}

export interface RiskDistribution {
  critical: number;
  high: number;
  medium: number;
  low: number;
  no_risk: number;
  info: number;
}
