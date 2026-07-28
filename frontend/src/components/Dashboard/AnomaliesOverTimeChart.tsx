import React from "react";
import { Card, Space, Select } from "antd";
import { QuestionCircleOutlined } from "@ant-design/icons";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { TimeSeriesData } from "../../utils/dashboardUtils";

interface AnomaliesOverTimeChartProps {
    data: TimeSeriesData[];
}

const AnomaliesOverTimeChart: React.FC<AnomaliesOverTimeChartProps> = ({ data }) => {
    return (
        <Card
            style={{
                height: '-webkit-fill-available'
            }}
            title={
                <Space>
                    Anomalies Over Time
                    <QuestionCircleOutlined style={{ fontSize: 14, color: "#999" }} />
                </Space>
            }
            extra={<Select defaultValue="daily" options={[{ value: "daily", label: "Daily" }]} />}
            bordered={false}
        >
            <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ff4757" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#ff4757" stopOpacity={0.05} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" stroke="#999" style={{ fontSize: 12 }} />
                    <YAxis stroke="#999" style={{ fontSize: 12 }} />
                    <Tooltip
                        contentStyle={{ background: "#000", border: "none", borderRadius: 8, fontSize: 12 }}
                        labelStyle={{ color: "#fff" }}
                    />
                    <Area
                        type="monotone"
                        dataKey="anomalies"
                        stroke="#ff4757"
                        strokeWidth={2}
                        fill="url(#colorAnomalies)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </Card>
    );
};

export default AnomaliesOverTimeChart;
