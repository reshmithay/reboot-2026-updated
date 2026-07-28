import { SEVERITY_COLORS, SEVERITY_LABELS, RISK_THRESHOLDS } from "../constants/appConstants";

export const getRiskColor = (score: number): string => {
  if (score >= RISK_THRESHOLDS.CRITICAL) return SEVERITY_COLORS.critical;
  if (score >= RISK_THRESHOLDS.HIGH) return SEVERITY_COLORS.high;
  if (score >= RISK_THRESHOLDS.MEDIUM) return SEVERITY_COLORS.medium;
  return SEVERITY_COLORS.low;
};

export const getRiskLabel = (score: number): string => {
  if (score >= RISK_THRESHOLDS.CRITICAL) return SEVERITY_LABELS.critical;
  if (score >= RISK_THRESHOLDS.HIGH) return SEVERITY_LABELS.high;
  if (score >= RISK_THRESHOLDS.MEDIUM) return SEVERITY_LABELS.medium;
  return SEVERITY_LABELS.low;
};

export const formatScore = (score: number): string => {
  return `${(score * 100).toFixed(1)}%`;
};

export const getSeverityBadgeClass = (severity: string): string => {
  const map: Record<string, string> = {
    critical: "bg-red-100 text-red-800 border-red-200",
    high: "bg-orange-100 text-orange-800 border-orange-200",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
    low: "bg-green-100 text-green-800 border-green-200",
  };
  return map[severity] || "bg-gray-100 text-gray-800 border-gray-200";
};
