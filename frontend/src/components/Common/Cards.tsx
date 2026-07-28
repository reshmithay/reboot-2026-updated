import React, { ReactNode } from "react";
import { Card, Statistic } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  trend,
  className,
}) => {
  return (
    <Card className={className} hoverable>
      <Statistic
        title={title}
        value={value}
        prefix={icon}
        suffix={
          trend && (
            <span style={{ fontSize: 14, fontWeight: 500, color: trend.isPositive ? "#52c41a" : "#ff4d4f" }}>
              {trend.isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />} {trend.value}
            </span>
          )
        }
      />
    </Card>
  );
};

interface InfoCardProps {
  title: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export const InfoCard: React.FC<InfoCardProps> = ({
  title,
  children,
  className,
  action,
}) => {
  return (
    <Card
      title={title}
      extra={action}
      className={className}
      bordered
    >
      {children}
    </Card>
  );
};

interface DataCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  className?: string;
}

export const DataCard: React.FC<DataCardProps> = ({
  label,
  value,
  subValue,
  className,
}) => {
  return (
    <div className={className} style={{ display: "flex", flexDirection: "column" }}>
      <span style={{ fontSize: 14, color: "#8c8c8c", marginBottom: 4 }}>{label}</span>
      <span style={{ fontSize: 18, fontWeight: 600, color: "#1f2937" }}>{value}</span>
      {subValue && <span style={{ fontSize: 12, color: "#bfbfbf", marginTop: 4 }}>{subValue}</span>}
    </div>
  );
};
