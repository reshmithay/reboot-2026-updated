import React from "react";
import { Card, Table, Button, Space, Tag } from "antd";
import { EyeOutlined, MoreOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { AlertTableData, getRiskScoreColor, getStatusColor } from "../../utils/dashboardUtils";

interface RecentAlertsTableProps {
  data: AlertTableData[];
}

const RecentAlertsTable: React.FC<RecentAlertsTableProps> = ({ data }) => {
  const navigate = useNavigate();

  const columns = [
    {
      title: "Alert ID",
      dataIndex: "alertId",
      key: "alertId",
      render: (text: string) => <a style={{ color: "#2563eb" }}>{text}</a>,
    },
    {
      title: "Time",
      dataIndex: "time",
      key: "time",
    },
    {
      title: "Entity / Account",
      dataIndex: "entity",
      key: "entity",
    },
    {
      title: "Alert Type",
      dataIndex: "type",
      key: "type",
    },
    {
      title: "Risk Score",
      dataIndex: "riskScore",
      key: "riskScore",
      render: (score: number) => <Tag color={getRiskScoreColor(score)}>{score}</Tag>,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag>,
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: any, record: AlertTableData) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/narrative/${record.transactionId}`)}
          />
          <Button type="text" icon={<MoreOutlined />} />
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="Recent High Risk Alerts"
      extra={<a style={{ fontSize: 14, color: "#2563eb" }}>View All Alerts →</a>}
      bordered={false}
    >
      <Table columns={columns} dataSource={data} pagination={false} size="small" />
    </Card>
  );
};

export default RecentAlertsTable;
