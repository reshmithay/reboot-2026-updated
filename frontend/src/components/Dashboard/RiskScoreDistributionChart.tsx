import React from "react";
import { Card, Space } from "antd";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { RiskDistributionData } from "../../utils/dashboardUtils";
import { RISK_COLORS } from "../../constants/dashboardConstants";

interface RiskScoreDistributionChartProps {
  data: RiskDistributionData[];
  total: number;
}

const RiskScoreDistributionChart: React.FC<RiskScoreDistributionChartProps> = ({
  data,
  total,
}) => {
  return (
    <Card title="Risk Score Distribution" bordered={false}>
      <div style={{ textAlign: "center", marginBottom: 16 }}>
        <ResponsiveContainer width="100%" height={180}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={RISK_COLORS[index]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ fontSize: 24, fontWeight: 700, marginTop: -100 }}>{total}</div>
        <div style={{ fontSize: 12, color: "#999" }}>Total</div>
      </div>
      <div style={{ marginTop: 60 }}>
        {data.map((item, index) => (
          <div
            key={item.name}
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: 8,
              fontSize: 12,
            }}
          >
            <Space>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: RISK_COLORS[index],
                }}
              />
              <span>{item.name}</span>
            </Space>
            <span style={{ fontWeight: 600 }}>
              {item.percentage}% ({item.count})
            </span>
          </div>
        ))}
      </div>
      <div style={{ textAlign: "center", marginTop: 16 }}>
        <a style={{ fontSize: 12, color: "#2563eb" }}>View full analytics →</a>
      </div>
    </Card>
  );
};

export default RiskScoreDistributionChart;
