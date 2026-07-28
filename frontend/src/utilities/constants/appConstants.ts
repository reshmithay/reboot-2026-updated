// API
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const LLM_SERVER_URL = import.meta.env.VITE_LLM_SERVER_URL || "http://localhost:8001";

// Anomaly severity colours
export const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

// Anomaly severity labels
export const SEVERITY_LABELS: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

// Transaction status colours
export const STATUS_COLORS: Record<string, string> = {
  confirmed: "#22c55e",
  pending: "#eab308",
  failed: "#ef4444",
};

// Risk score thresholds
export const RISK_THRESHOLDS = {
  CRITICAL: 90,
  HIGH: 75,
  MEDIUM: 50,
  LOW: 25,
};

// Pagination defaults
export const DEFAULT_PAGE_SIZE = 20;

// Chart colours palette
export const CHART_COLORS = [
  "#6366f1",
  "#22d3ee",
  "#f97316",
  "#ef4444",
  "#22c55e",
  "#a855f7",
];

// Supported chains
export const SUPPORTED_CHAINS: Record<number, string> = {
  1: "Ethereum Mainnet",
  137: "Polygon",
  80001: "Mumbai Testnet",
  31337: "Hardhat Local",
};
