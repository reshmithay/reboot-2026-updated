import React from "react";
import { Card, Space, Descriptions, Tag } from "antd";
import { LineChartOutlined } from "@ant-design/icons";
import { Transaction, AnomalyResult } from "@/types";

interface TransactionSnapshotProps {
    transaction: Transaction | null;
    anomaly: AnomalyResult;
}

export const TransactionSnapshot: React.FC<TransactionSnapshotProps> = ({ transaction }) => {
    return (
        <Card
            title={
                <Space>
                    <LineChartOutlined />
                    Transaction Snapshot
                </Space>
            }
            style={{ marginBottom: 24 }}
        >
            <Descriptions column={1} size="small">
                <Descriptions.Item label="Transaction Type">
                    {transaction?.transaction_type || "N/A"}
                </Descriptions.Item>
                <Descriptions.Item label="Amount">
                    <span style={{ fontWeight: 600 }}>
                        {transaction 
                            ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}` 
                            : "N/A"}
                    </span>
                </Descriptions.Item>
                <Descriptions.Item label="Blockchain Network">
                    {transaction?.blockchain_network || "N/A"}
                </Descriptions.Item>
                <Descriptions.Item label="Transaction Status">
                    <Tag color="blue">{transaction?.transaction_status || "N/A"}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="From Wallet">
                    {transaction?.from_wallet_address 
                        ? `${transaction.from_wallet_address.substring(0, 10)}...` 
                        : "N/A"}
                </Descriptions.Item>
                <Descriptions.Item label="To Wallet">
                    {transaction?.to_wallet_address 
                        ? `${transaction.to_wallet_address.substring(0, 10)}...` 
                        : "N/A"}
                </Descriptions.Item>
                <Descriptions.Item label="Block Number">
                    {transaction?.block_number || "N/A"}
                </Descriptions.Item>
                <Descriptions.Item label="Chain ID">
                    {transaction?.chain_id || "N/A"}
                </Descriptions.Item>
            </Descriptions>
        </Card>
    );
};
