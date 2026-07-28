import React from "react";
import { Card, Progress, Space } from "antd";
import { TopEntity } from "../../utils/dashboardUtils";

interface TopAlertedEntitiesProps {
  data: TopEntity[];
}

const TopAlertedEntities: React.FC<TopAlertedEntitiesProps> = ({ data }) => {
  const maxCount = data[0]?.count || 1;

  return (
    <Card
      title="Top Alerted Entities"
      extra={<a style={{ fontSize: 14, color: "#2563eb" }}>View All</a>}
      bordered={false}
    >
      <div>
        {data.map((entity, index) => (
          <div key={entity.name} style={{ marginBottom: 20 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 8,
                fontSize: 13,
              }}
            >
              <Space>
                <span style={{ fontWeight: 600, color: "#999" }}>{index + 1}</span>
                <span>{entity.name}</span>
              </Space>
              <span style={{ fontWeight: 600 }}>{entity.count}</span>
            </div>
            <Progress
              percent={(entity.count / maxCount) * 100}
              showInfo={false}
              strokeColor="#ff4d4f"
              trailColor="#f5f5f5"
            />
          </div>
        ))}
      </div>
    </Card>
  );
};

export default TopAlertedEntities;
