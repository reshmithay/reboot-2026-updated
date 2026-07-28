import apiClient from "../../clients/api/axiosClient";
import { ClientRegistry, ClientRegistryListResponse } from "../../types/client.types";

export interface ClientCreateRequest {
  client_id: string;
  client_name: string;
  client_type?: string;
  lei?: string;
  industry_sector?: string;
  country_of_incorporation?: string;
  risk_tier?: string;
  relationship_manager?: string;
  wallet_address?: string;
  wallet_type?: string;
  facility_type?: string;
  credit_limit?: number;
  daily_deposit_limit?: number;
  daily_withdrawal_limit?: number;
  expected_activity_window?: string;
  authorized_signatories?: string[];
  kyc_status?: string;
  aml_status?: string;
}

export interface ClientUpdateRequest {
  client_name?: string;
  client_type?: string;
  lei?: string;
  industry_sector?: string;
  country_of_incorporation?: string;
  risk_tier?: string;
  relationship_manager?: string;
  wallet_address?: string;
  wallet_type?: string;
  facility_type?: string;
  credit_limit?: number;
  daily_deposit_limit?: number;
  daily_withdrawal_limit?: number;
  expected_activity_window?: string;
  authorized_signatories?: string[];
  kyc_status?: string;
  aml_status?: string;
}

export interface ClientListParams {
  page?: number;
  page_size?: number;
  risk_tier?: string;
  kyc_status?: string;
  aml_status?: string;
  client_type?: string;
  search?: string;
}

const clientService = {
  /**
   * Create a new client
   */
  create: (data: ClientCreateRequest): Promise<ClientRegistry> =>
    apiClient
      .post("/api/v1/clients/", data)
      .then((r) => r.data),

  /**
   * List clients with optional filters and pagination
   */
  list: (params?: ClientListParams): Promise<ClientRegistryListResponse> =>
    apiClient
      .get("/api/v1/clients/", { params })
      .then((r) => r.data),

  /**
   * Get a client by ID
   */
  get: (clientId: string): Promise<ClientRegistry> =>
    apiClient
      .get(`/api/v1/clients/${clientId}`)
      .then((r) => r.data),

  /**
   * Get a client by wallet address
   */
  getByWallet: (walletAddress: string): Promise<ClientRegistry> =>
    apiClient
      .get(`/api/v1/clients/wallet/${walletAddress}`)
      .then((r) => r.data),

  /**
   * Update a client
   */
  update: (clientId: string, data: ClientUpdateRequest): Promise<ClientRegistry> =>
    apiClient
      .put(`/api/v1/clients/${clientId}`, data)
      .then((r) => r.data),

  /**
   * Delete a client
   */
  delete: (clientId: string): Promise<void> =>
    apiClient
      .delete(`/api/v1/clients/${clientId}`)
      .then((r) => r.data),

  /**
   * Get client limits
   */
  getLimits: (clientId: string): Promise<any> =>
    apiClient
      .get(`/api/v1/clients/${clientId}/limits`)
      .then((r) => r.data),

  /**
   * Get client compliance information
   */
  getCompliance: (clientId: string): Promise<any> =>
    apiClient
      .get(`/api/v1/clients/${clientId}/compliance`)
      .then((r) => r.data),
};

export default clientService;
