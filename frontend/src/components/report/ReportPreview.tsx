import React, {useMemo, useState} from 'react'
import {CheckOutlined, CloseOutlined, DownloadOutlined, EditOutlined, ReloadOutlined} from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import styles from './ReportPreview.module.css'

interface ReportPreviewProps {
    report: {
        filename: string
        content: string
        messageId: number
        reportId: number
    }
    onClose: () => void
    onDownload: () => void
    onRegenerate?: () => void
}

interface Section {
    title: string
    content: string
}

const ReportPreview = ({report, onClose, onDownload, onRegenerate}: ReportPreviewProps) => {
    // ## 헤더 기준으로 섹션 파싱
    const sections = useMemo(() => {
        const result: Section[] = []
        const lines = report.content.split('\n')
        let currentTitle = ''
        let currentContent: string[] = []

        lines.forEach((line) => {
            // ## 헤더 감지 (H2)
            const headerMatch = line.match(/^##\s+(.+)/)
            if (headerMatch) {
                // 이전 섹션 저장
                if (currentTitle || currentContent.length > 0) {
                    result.push({
                        title: currentTitle || '서문',
                        content: currentContent.join('\n').trim()
                    })
                }
                // 새 섹션 시작
                currentTitle = headerMatch[1]
                currentContent = []
            } else {
                currentContent.push(line)
            }
        })

        // 마지막 섹션 저장
        if (currentTitle || currentContent.length > 0) {
            result.push({
                title: currentTitle || '서문',
                content: currentContent.join('\n').trim()
            })
        }

        // 섹션이 없는 경우 전체를 하나의 섹션으로
        if (result.length === 0) {
            result.push({
                title: '전체 내용',
                content: report.content
            })
        }

        return result
    }, [report.content])

    // 각 섹션별 편집 상태 관리
    const [editingStates, setEditingStates] = useState<{[key: string]: boolean}>({})
    const [editedContents, setEditedContents] = useState<{[key: string]: string}>({})

    const handleEditClick = (title: string, content: string) => {
        setEditingStates({...editingStates, [title]: true})
        setEditedContents({...editedContents, [title]: content})
    }

    const handleCompleteClick = (title: string) => {
        setEditingStates({...editingStates, [title]: false})
        // TODO: 백엔드에 저장하거나 상위 컴포넌트로 변경사항 전달
    }

    const handleContentChange = (title: string, value: string) => {
        setEditedContents({...editedContents, [title]: value})
    }

    const getDisplayContent = (section: Section) => {
        return editedContents[section.title] !== undefined ? editedContents[section.title] : section.content
    }

    return (
        <div className={styles.reportPreviewSidebar}>
            <div className={styles.previewHeader}>
                <div className={styles.previewTitle}>
                    <span>보고서 미리보기</span>
                </div>
                <div className={styles.previewActions}>
                    {/* TODO: 재생성 구현 필요 */}
                    {true && (
                        <button className={`${styles.previewActionBtn} ${styles.regenerate}`} onClick={onRegenerate} title="보고서 재생성">
                            <ReloadOutlined />
                        </button>
                    )}
                    <button className={`${styles.previewActionBtn} ${styles.download}`} onClick={onDownload} title="다운로드">
                        <DownloadOutlined />
                    </button>
                    <button className={`${styles.previewActionBtn} ${styles.close}`} onClick={onClose} title="닫기">
                        <CloseOutlined />
                    </button>
                </div>
            </div>

            <div className={styles.previewContent}>
                <div className={styles.previewFilename}>{report.filename}</div>
                <div className={styles.previewSections}>
                    {sections.map((section, index) => (
                        <div key={`${section.title}-${index}`} className={styles.section}>
                            <div className={styles.sectionHeader}>
                                <h2 className={styles.sectionTitle}>{section.title}</h2>
                                <button
                                    className={styles.sectionEditBtn}
                                    onClick={() =>
                                        editingStates[section.title]
                                            ? handleCompleteClick(section.title)
                                            : handleEditClick(section.title, section.content)
                                    }
                                    title={editingStates[section.title] ? '완료' : '수정'}>
                                    {editingStates[section.title] ? <CheckOutlined /> : <EditOutlined />}
                                </button>
                            </div>

                            <div className={styles.sectionContent}>
                                {editingStates[section.title] ? (
                                    <textarea
                                        className={styles.sectionTextarea}
                                        value={getDisplayContent(section)}
                                        onChange={(e) => handleContentChange(section.title, e.target.value)}
                                    />
                                ) : (
                                    <div className={styles.markdown}>
                                        <ReactMarkdown>{getDisplayContent(section)}</ReactMarkdown>
                                    </div>
                                )}
                            </div>

                            {index < sections.length - 1 && <div className={styles.sectionDivider} />}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default ReportPreview
