import React from "react";
import { Card, Space, Timeline } from "antd";
import { ClockCircleOutlined } from "@ant-design/icons";

export interface TimelineEvent {
    time: string;
    title: string;
    description: string;
    type: "normal" | "warning" | "error";
}

interface InvestigationTimelineProps {
    events: TimelineEvent[];
}

export const InvestigationTimeline: React.FC<InvestigationTimelineProps> = ({ events }) => {
    return (
        <Card
            title={
                <Space>
                    <ClockCircleOutlined />
                    Investigation Timeline
                </Space>
            }
            style={{ marginBottom: 24 }}
        >
            <Timeline
                items={events.map((event) => ({
                    color: event.type === "error" ? "red" : event.type === "warning" ? "orange" : "blue",
                    children: (
                        <div>
                            <div style={{ fontWeight: 600, marginBottom: 4 }}>
                                {event.time} - {event.title}
                            </div>
                            <div style={{ fontSize: 12, color: "#666" }}>{event.description}</div>
                        </div>
                    ),
                }))}
            />
        </Card>
    );
};
