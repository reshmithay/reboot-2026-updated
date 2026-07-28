import React from "react";
import { Tag } from "antd";
import { AnomalySeverity } from "../../types/anomaly.types";

interface RiskBadgeProps {
  severity: string;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ severity, className }) => {
  const getColor = () => {
    switch (severity.toUpperCase()) {
      case AnomalySeverity.CRITICAL:
        return "red";
      case AnomalySeverity.HIGH:
        return "orange";
      case AnomalySeverity.MEDIUM:
        return "gold";
      case AnomalySeverity.LOW:
        return "green";
      default:
        return "default";
    }
  };

  return (
    <Tag color={getColor()} className={className} bordered>
      {severity}
    </Tag>
  );
};

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const getColor = () => {
    const upperStatus = status.toUpperCase();
    
    if (upperStatus.includes("SANCTIONED") || upperStatus.includes("BLACKLIST")) {
      return "red";
    }
    if (upperStatus.includes("ATTACK") || upperStatus.includes("SCAM")) {
      return "volcano";
    }
    if (upperStatus.includes("PENDING") || upperStatus.includes("UNDER_REVIEW")) {
      return "warning";
    }
    if (upperStatus.includes("CONFIRMED") || upperStatus.includes("APPROVED")) {
      return "success";
    }
    if (upperStatus.includes("FAILED") || upperStatus.includes("REJECTED")) {
      return "error";
    }
    
    return "blue";
  };

  return (
    <Tag color={getColor()} className={className}>
      {status}
    </Tag>
  );
};

interface LabelBadgeProps {
  label: string;
  type?: "transfer" | "deposit" | "withdrawal" | "default";
  className?: string;
}

export const LabelBadge: React.FC<LabelBadgeProps> = ({ 
  label, 
  type = "default",
  className 
}) => {
  const getColor = () => {
    switch (type) {
      case "transfer":
        return "purple";
      case "deposit":
        return "blue";
      case "withdrawal":
        return "orange";
      default:
        return "default";
    }
  };

  return (
    <Tag color={getColor()} className={className}>
      {label}
    </Tag>
  );
};
