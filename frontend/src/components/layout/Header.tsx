import React from 'react'
import {Layout, Button, Space} from 'antd'
import {LogoutOutlined, UserOutlined, SettingOutlined} from '@ant-design/icons'
import {useNavigate} from 'react-router-dom'
import {useAuth} from '../../hooks/useAuth'
import styles from './Header.module.css'

const {Header: AntHeader} = Layout

const Header: React.FC = () => {
    const {user, logout} = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <AntHeader className={`${styles.header} flex-between`}>
            <div className={styles.headerLeft}>
                <Button type="link" onClick={() => navigate('/')} className={styles.logoBtn}>
                    <h2 className={styles.title}>HWP 보고서 자동 생성 시스템</h2>
                </Button>
            </div>
            <Space className={styles.headerRight}>
                <div className={styles.userInfo}>
                    <UserOutlined />
                    <span className={`${styles.username} ${styles.btnText}`}>{user?.username}</span>
                </div>
                {user?.is_admin && (
                    <Button type="link" icon={<SettingOutlined />} onClick={() => navigate('/admin')} className={styles.adminBtn}>
                        <span className={styles.btnText}>관리자 페이지</span>
                    </Button>
                )}
                <Button type="primary" icon={<LogoutOutlined />} onClick={handleLogout} className={styles.logoutBtn}>
                    <span className={styles.btnText}>로그아웃</span>
                </Button>
            </Space>
        </AntHeader>
    )
}

export default Header
