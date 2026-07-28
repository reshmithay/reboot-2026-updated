import React from "react";
import { Card, Space } from "antd";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { CategoryData } from "../../utils/dashboardUtils";
import { CATEGORY_COLORS } from "../../constants/dashboardConstants";

interface AnomaliesByCategoryChartProps {
  data: CategoryData[];
  total: number;
}

const AnomaliesByCategoryChart: React.FC<AnomaliesByCategoryChartProps> = ({ data, total }) => {
  return (
    <Card title="Anomalies by Category" bordered={false}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div style={{ marginTop: 16 }}>
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
                  background: CATEGORY_COLORS[index % CATEGORY_COLORS.length],
                }}
              />
              <span>{item.name}</span>
            </Space>
            <span style={{ fontWeight: 600 }}>
              {item.percentage}% ({item.value})
            </span>
          </div>
        ))}
        <div
          style={{
            marginTop: 16,
            paddingTop: 16,
            borderTop: "1px solid #f0f0f0",
            fontWeight: 700,
          }}
        >
          Total: {total}
        </div>
      </div>
    </Card>
  );
};

export default AnomaliesByCategoryChart;
