import React, { ReactNode, useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Avatar, Badge, Button, Drawer } from "antd";
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
  CloseOutlined,
} from "@ant-design/icons";

const { Header, Sider, Content } = Layout;

interface LayoutProps {
  children: ReactNode;
}

export const MainLayout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) setCollapsed(true);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Close drawer on route change (mobile)
  useEffect(() => {
    setDrawerOpen(false);
  }, [location.pathname]);

  const menuItems = [
    { key: "/compliance", icon: <SafetyOutlined />, label: "Screening" },
    { key: "/transactions", icon: <SwapOutlined />, label: "Transactions" },
    { key: "/clients", icon: <TeamOutlined />, label: "Clients" },
    { key: "/anomalies", icon: <WarningOutlined />, label: "Anomalies" },
    { key: "/dashboard", icon: <DashboardOutlined />, label: "Dashboard" },
    {
      key: "/advanced-analysis",
      icon: <ExperimentOutlined />,
      label: "Advance Analysis",
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const selectedKey =
    menuItems.find(
      (item) =>
        location.pathname === item.key ||
        (location.pathname === "/" && item.key === "/compliance"),
    )?.key || "/compliance";

  const menuContent = (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      items={menuItems}
      onClick={handleMenuClick}
      style={{ borderRight: 0, paddingTop: 16 }}
    />
  );

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* ── Header ─────────────────────────────────────────────── */}
      <Header
        style={{
          position: "fixed",
          top: 0,
          zIndex: 1000,
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 16px",
          backgroundColor: "#fff",
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Button
            type="text"
            icon={
              isMobile ? (
                <MenuUnfoldOutlined />
              ) : collapsed ? (
                <MenuUnfoldOutlined />
              ) : (
                <MenuFoldOutlined />
              )
            }
            onClick={() =>
              isMobile ? setDrawerOpen(true) : setCollapsed(!collapsed)
            }
            style={{ fontSize: 16, width: 40, height: 40 }}
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
              flexShrink: 0,
            }}
          >
            BA
          </div>
          <span
            style={{
              fontSize: isMobile ? 15 : 18,
              fontWeight: 600,
              color: "#1f2937",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              maxWidth: isMobile ? 160 : "none",
            }}
          >
            Blockchain Anomaly AI
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Badge count={5} offset={[-4, 4]}>
            <Button type="text" icon={<BellOutlined />} size="large" />
          </Badge>
          <Avatar
            style={{ backgroundColor: "#d1d5db" }}
            size={isMobile ? "default" : "large"}
          />
        </div>
      </Header>

      <Layout style={{ marginTop: 64 }}>
        {/* ── Desktop Sider ───────────────────────────────────── */}
        {!isMobile && (
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
            {menuContent}
          </Sider>
        )}

        {/* ── Mobile Drawer ────────────────────────────────────── */}
        {isMobile && (
          <Drawer
            placement="left"
            open={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            width={240}
            styles={{ body: { padding: 0 } }}
            title={
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div
                  style={{
                    width: 28,
                    height: 28,
                    background: "#2563eb",
                    borderRadius: 6,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "white",
                    fontWeight: "bold",
                    fontSize: 12,
                  }}
                >
                  BA
                </div>
                <span style={{ fontWeight: 600, fontSize: 15 }}>Menu</span>
              </div>
            }
            closeIcon={<CloseOutlined />}
          >
            {menuContent}
          </Drawer>
        )}

        {/* ── Content ─────────────────────────────────────────── */}
        <Layout
          style={{
            marginLeft: isMobile ? 0 : collapsed ? 80 : 256,
            transition: "margin-left 0.2s",
          }}
        >
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
