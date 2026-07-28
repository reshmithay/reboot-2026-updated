import React, { ReactNode, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Avatar, Badge, Button } from "antd";
import {
  SafetyOutlined,
  SwapOutlined,
  TeamOutlined,
  WarningOutlined,
  DashboardOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ExperimentOutlined,
} from "@ant-design/icons";

const { Header, Sider, Content } = Layout;

interface LayoutProps {
  children: ReactNode;
}

export const MainLayout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: "/compliance",
      icon: <SafetyOutlined />,
      label: "Compliance",
    },
    {
      key: "/transactions",
      icon: <SwapOutlined />,
      label: "Transactions",
    },
    {
      key: "/clients",
      icon: <TeamOutlined />,
      label: "Clients",
    },
    {
      key: "/anomalies",
      icon: <WarningOutlined />,
      label: "Anomalies",
    },
    {
      key: "/dashboard",
      icon: <DashboardOutlined />,
      label: "Dashboard",
    },
    {
      key: "/advanced-analysis",
      icon: <ExperimentOutlined />,
      label: "Advance Analysis",
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  // Get current selected key from location
  const selectedKey = menuItems.find(item => 
    location.pathname === item.key || location.pathname === "/" && item.key === "/compliance"
  )?.key || "/compliance";

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          position: "fixed",
          top: 0,
          zIndex: 1000,
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          backgroundColor: "#fff",
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: "16px", width: 40, height: 40 }}
          />
          <div
            style={{
              width: 32,
              height: 32,
              background: "#2563eb",
              borderRadius: 8,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: "bold",
              fontSize: 14,
            }}
          >
            BA
          </div>
          <span style={{ fontSize: 18, fontWeight: 600, color: "#1f2937" }}>
            Blockchain Anomaly AI
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <Badge count={5} offset={[-4, 4]}>
            <Button type="text" icon={<BellOutlined />} size="large" />
          </Badge>
          <Avatar style={{ backgroundColor: "#d1d5db" }} size="large" />
        </div>
      </Header>

      <Layout style={{ marginTop: 64 }}>
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          style={{
            overflow: "auto",
            height: "calc(100vh - 64px)",
            position: "fixed",
            left: 0,
            top: 64,
            bottom: 0,
            backgroundColor: "#fff",
            borderRight: "1px solid #f0f0f0",
          }}
          width={256}
        >
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ borderRight: 0, paddingTop: 16 }}
          />
        </Sider>

        <Layout style={{ marginLeft: collapsed ? 80 : 256, transition: "margin-left 0.2s" }}>
          <Content
            style={{
              margin: 0,
              padding: 0,
              minHeight: "calc(100vh - 64px)",
              backgroundColor: "#f9fafb",
            }}
          >
            {children}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};
