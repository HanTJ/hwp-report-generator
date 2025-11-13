import {useState, useEffect} from 'react'
import {Modal, Button, Tag} from 'antd'
import {TagsOutlined} from '@ant-design/icons'
import {templateApi} from '../../services/templateApi'
import type {TemplateDetail} from '../../types/template'
import {formatFileSize, formatDate} from '../../utils/formatters'
import styles from './TemplateDetailModal.module.css'

/**
 * TemplateDetailModal.tsx
 *
 * ⭐ 템플릿 상세 정보 모달
 *
 * 역할:
 * 1. 템플릿 상세 정보 표시 (제목, 파일명, 파일 크기, 플레이스홀더 목록, 생성일)
 * 2. 모달 열기/닫기
 *
 * 표시 정보:
 * - 기본 정보: 제목, 파일명, 파일 크기, 생성일
 * - 플레이스홀더 목록: {{KEY}} 형태로 표시
 */

interface TemplateDetailModalProps {
    open: boolean
    templateId: number | null
    onClose: () => void
}

const TemplateDetailModal: React.FC<TemplateDetailModalProps> = ({open, templateId, onClose}) => {
    const [template, setTemplate] = useState<TemplateDetail | null>(null)
    const [loading, setLoading] = useState(false)

    // 템플릿 상세 정보 로드
    const loadTemplate = async () => {
        if (!templateId) return

        setLoading(true)
        try {
            const data = await templateApi.getTemplate(templateId)
            setTemplate(data)
        } catch (error: any) {
            console.log('TemplateDetailModal > loadTemplate', error)
            onClose()
        } finally {
            setLoading(false)
        }
    }

    // 모달 열릴 때 데이터 로드
    useEffect(() => {
        if (open && templateId) {
            loadTemplate()
        }
    }, [open, templateId])

    return (
        <Modal
            title="템플릿 상세"
            open={open}
            onCancel={onClose}
            width={700}
            footer={[
                <Button key="close" onClick={onClose}>
                    닫기
                </Button>
            ]}>
            {loading ? (
                <div className={styles.loadingContainer}>
                    <p>템플릿 정보를 불러오는 중...</p>
                </div>
            ) : template ? (
                <div className={styles.content}>
                    <div className={styles.section}>
                        <h3 className={styles.sectionTitle}>기본 정보</h3>
                        <table className={styles.infoTable}>
                            <tbody>
                                <tr>
                                    <td className={styles.infoLabel}>제목</td>
                                    <td className={styles.infoValue}>{template.title}</td>
                                </tr>
                                <tr>
                                    <td className={styles.infoLabel}>파일명</td>
                                    <td className={styles.infoValue}>{template.filename}</td>
                                </tr>
                                <tr>
                                    <td className={styles.infoLabel}>파일 크기</td>
                                    <td className={styles.infoValue}>{formatFileSize(template.file_size)}</td>
                                </tr>
                                <tr>
                                    <td className={styles.infoLabel}>생성일</td>
                                    <td className={styles.infoValue}>{formatDate(new Date(template.created_at).getTime() / 1000)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div className={styles.section}>
                        <h3 className={styles.sectionTitle}>
                            <TagsOutlined className={styles.sectionIcon} />
                            플레이스홀더
                        </h3>
                        {template.placeholders.length > 0 ? (
                            <div className={styles.tagContainer}>
                                {template.placeholders.map((ph, index) => (
                                    <Tag key={index}>{`${ph.key}`}</Tag>
                                ))}
                            </div>
                        ) : (
                            <p className={styles.emptyText}>플레이스홀더가 없습니다.</p>
                        )}
                    </div>

                    <div className={styles.notice}>
                        <p className={styles.noticeText}>
                            이 템플릿은 보고서 생성 시 사용할 수 있습니다. 플레이스홀더는 자동으로 실제 내용으로 대체됩니다.
                        </p>
                    </div>
                </div>
            ) : (
                <div className={styles.emptyContainer}>템플릿 정보를 찾을 수 없습니다.</div>
            )}
        </Modal>
    )
}

export default TemplateDetailModal
