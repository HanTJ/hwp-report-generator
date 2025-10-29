import React from "react";
import { Layout } from "antd";
import Header from "./Header";
import Footer from "./Footer";
import styles from "./MainLayout.module.css";

const { Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout className={styles.main}>
      <Header />
      <Content className={styles.content}>
        <div>{children}</div>
      </Content>
      <Footer />
    </Layout>
  );
};

export default MainLayout;
