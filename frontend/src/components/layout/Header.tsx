import React from "react";
import { Layout, Button, Space } from "antd";
import {
  LogoutOutlined,
  UserOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import styles from "./Header.module.css";

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <AntHeader className={`${styles.header} flex-between`}>
      <div>
        <h2>HWP 보고서 자동 생성 시스템</h2>
        <p>Claude AI를 활용한 금융 업무보고서 자동 생성</p>
      </div>
      <Space>
        <UserOutlined />
        <span>{user?.username}</span>
        {user?.is_admin && (
          <Button
            type="link"
            icon={<SettingOutlined />}
            onClick={() => navigate("/admin")}
          >
            관리자 페이지
          </Button>
        )}
        <Button type="primary" icon={<LogoutOutlined />} onClick={handleLogout}>
          로그아웃
        </Button>
      </Space>
    </AntHeader>
  );
};

export default Header;
