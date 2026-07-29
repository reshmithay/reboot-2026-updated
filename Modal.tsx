import React from "react";
import { Modal as AntModal, Tabs, Button, Upload, message } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import type { UploadProps } from "antd";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = "md",
}) => {
  const widthMap = {
    sm: 400,
    md: 600,
    lg: 800,
    xl: 1200,
  };

  return (
    <AntModal
      title={title}
      open={isOpen}
      onCancel={onClose}
      footer={footer}
      width={widthMap[size]}
    >
      {children}
    </AntModal>
  );
};

interface BulkScreeningModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScreen: (file: File) => void;
  loading?: boolean;
}

export const BulkScreeningModal: React.FC<BulkScreeningModalProps> = ({
  isOpen,
  onClose,
  onScreen,
  loading = false,
}) => {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [activeTab, setActiveTab] = React.useState("addresses");

  const uploadProps: UploadProps = {
    name: "file",
    accept: ".csv",
    maxCount: 1,
    beforeUpload: (file) => {
      if (!file.name.endsWith(".csv")) {
        message.error("You can only upload CSV files!");
        return false;
      }
      const isLt4M = file.size / 1024 / 1024 < 4;
      if (!isLt4M) {
        message.error("File must be smaller than 4MB!");
        return false;
      }
      setSelectedFile(file);
      return false; // Prevent auto upload
    },
    onRemove: () => {
      setSelectedFile(null);
    },
  };

  const handleScreen = () => {
    if (selectedFile) {
      onScreen(selectedFile);
      setSelectedFile(null);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Bulk Screening"
      size="md"
      footer={
        <>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="primary"
            onClick={handleScreen}
            disabled={!selectedFile || loading}
            loading={loading}
          >
            {loading ? "Screening…" : "Screen"}
          </Button>
        </>
      }
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: "addresses",
            label: "Addresses",
          },
          {
            key: "transactions",
            label: "Transactions",
          },
        ]}
      />

      <div style={{ marginTop: 16 }}>
        <p style={{ marginBottom: 16, color: "#666" }}>
          Upload a CSV file to screen {activeTab}
        </p>

        <Upload.Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <UploadOutlined style={{ fontSize: 48, color: "#999" }} />
          </p>
          <p className="ant-upload-text">
            Click or drag file to this area to upload
          </p>
          <p className="ant-upload-hint">
            CSV only (max. 4MB, max. 100 {activeTab})
          </p>
        </Upload.Dragger>
      </div>
    </Modal>
  );
};
