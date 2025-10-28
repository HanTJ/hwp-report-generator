import React from "react";
import { Layout } from "antd";
import Header from "./Header";
import Footer from "./Footer";

const { Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header />
      <Content style={{ padding: "24px", background: "#f0f2f5" }}>
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>{children}</div>
      </Content>
      <Footer />
    </Layout>
  );
};

export default MainLayout;
