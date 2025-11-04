import React, {useState} from 'react'
import {Form, Input, Button, Card, message} from 'antd'
import {UserOutlined, LockOutlined} from '@ant-design/icons'
import {useNavigate, Link} from 'react-router-dom'
import {useAuth} from '../hooks/useAuth'
import type {LoginRequest} from '../types/auth'
import styles from './LoginPage.module.css'

const LoginPage: React.FC = () => {
    const [loading, setLoading] = useState(false)
    const {login} = useAuth()
    const navigate = useNavigate()

    const onFinish = async (values: LoginRequest) => {
        setLoading(true)
        try {
            await login(values)
            message.success('로그인 성공!')
            navigate('/')
        } catch (error: any) {
            message.error(error.response?.data?.detail || '로그인에 실패했습니다.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className={styles.container}>
            <Card className={styles.card}>
                <div className={styles.header}>
                    <h1>HWP 보고서 자동 생성 시스템</h1>
                </div>

                <Form name="login" onFinish={onFinish} autoComplete="off" layout="vertical">
                    <Form.Item
                        label="이메일"
                        name="email"
                        rules={[
                            {required: true, message: '이메일을 입력해주세요!'},
                            {type: 'email', message: '올바른 이메일 형식이 아닙니다!'}
                        ]}>
                        <Input prefix={<UserOutlined />} placeholder="이메일을 입력하세요" size="large" />
                    </Form.Item>

                    <Form.Item label="비밀번호" name="password" rules={[{required: true, message: '비밀번호를 입력해주세요!'}]}>
                        <Input.Password prefix={<LockOutlined />} placeholder="비밀번호를 입력하세요" size="large" />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} block size="large">
                            로그인
                        </Button>
                    </Form.Item>

                    <div className={styles.footer}>
                        <span>계정이 없으신가요? </span>
                        <Link to="/register">회원가입</Link>
                    </div>
                </Form>
            </Card>
        </div>
    )
}

export default LoginPage
