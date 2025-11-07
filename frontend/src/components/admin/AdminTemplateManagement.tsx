/**
 * AdminTemplateManagement.tsx
 *
 * 관리자 템플릿 관리 컴포넌트
 * - 전체 사용자의 템플릿 목록 조회
 */

import React, {useState, useEffect} from 'react'
import {Card, Table, Button, message, Space} from 'antd'
import {ReloadOutlined, EyeOutlined} from '@ant-design/icons'
import type {ColumnsType} from 'antd/es/table'
import {templateApi} from '../../services/templateApi'
import type {AdminTemplateItem} from '../../types/template'
import TemplateDetailModal from '../template/TemplateDetailModal'
import {formatDate, formatFileSize} from '../../utils/formatters'

const AdminTemplateManagement: React.FC = () => {
    const [templates, setTemplates] = useState<AdminTemplateItem[]>([])
    const [loading, setLoading] = useState(false)
    const [detailModalOpen, setDetailModalOpen] = useState(false)
    const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null)

    // 템플릿 목록 로드
    const loadTemplates = async () => {
        setLoading(true)
        try {
            const data = await templateApi.listAllTemplates()
            setTemplates(data)
        } catch (error: any) {
            message.error(error.message || '템플릿 목록을 불러오는데 실패했습니다.')
        } finally {
            setLoading(false)
        }
    }

    // 초기 로드
    useEffect(() => {
        loadTemplates()
    }, [])

    // 템플릿 상세 보기
    const handleViewDetail = (templateId: number) => {
        setSelectedTemplateId(templateId)
        setDetailModalOpen(true)
    }

    // Table 컬럼 정의
    const columns: ColumnsType<AdminTemplateItem> = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: 70
        },
        {
            title: '제목',
            dataIndex: 'title',
            key: 'title',
            width: 200,
            ellipsis: true
        },
        {
            title: '사용자',
            dataIndex: 'username',
            key: 'username',
            width: 90,
            ellipsis: true
        },
        {
            title: '파일 크기',
            dataIndex: 'file_size',
            key: 'file_size',
            width: 110,
            render: (size: number) => formatFileSize(size)
        },
        {
            title: '플레이스홀더 수',
            dataIndex: 'placeholder_count',
            key: 'placeholder_count',
            width: 130,
            render: (count: number) => `${count}개`
        },
        {
            title: '생성일',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 180,
            render: (date: string) => {
                const timestamp = new Date(date).getTime() / 1000
                return formatDate(timestamp)
            }
        },
        {
            title: '액션',
            key: 'action',
            width: 100,
            render: (_, record) => (
                <Space>
                    <Button size="small" icon={<EyeOutlined />} onClick={() => handleViewDetail(record.id)}>
                        상세
                    </Button>
                </Space>
            )
        }
    ]

    return (
        <>
            <Card
                title="템플릿 관리"
                bordered={false}
                extra={
                    <Button icon={<ReloadOutlined />} onClick={() => loadTemplates()} loading={loading}>
                        새로고침
                    </Button>
                }>
                <Table
                    columns={columns}
                    dataSource={templates}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        pageSize: 10,
                        showSizeChanger: true,
                        showTotal: (total) => `총 ${total}개`,
                        pageSizeOptions: ['10', '20', '50']
                    }}
                />
            </Card>

            {/* 상세 모달 */}
            <TemplateDetailModal open={detailModalOpen} templateId={selectedTemplateId} onClose={() => setDetailModalOpen(false)} />
        </>
    )
}

export default AdminTemplateManagement
