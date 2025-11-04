import React, {forwardRef, use} from 'react'
import {DownloadOutlined, FileTextOutlined, CloseOutlined} from '@ant-design/icons'
import {Spin} from 'antd'
import styles from './ReportsDropdown.module.css'
import {useArtifactStore, type Artifact} from '../../stores/useArtifactStore'

interface ReportsDropdownProps {
    artifacts: Artifact[]
    loading: boolean
    selectedArtifactId: number | null
    onSelect: (artifactId: number) => void
    onClose: () => void
    onDownload: (artifact: Artifact) => void
    onPreview: (artifact: Artifact) => void
}

const ReportsDropdown = forwardRef<HTMLDivElement, ReportsDropdownProps>(
    ({artifacts, loading, selectedArtifactId, onSelect, onClose, onDownload, onPreview}, ref) => {
        const formatFileSize = (bytes: number): string => {
            if (bytes < 1024) return `${bytes} B`
            if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
            return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
        }

        const formatDate = (dateString: string): string => {
            const date = new Date(dateString)
            return date.toLocaleDateString('ko-KR', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        }

        return (
            <div ref={ref} className={styles.dropdown}>
                <div className={styles.dropdownHeader}>
                    <h4>참조 보고서 선택</h4>
                    <button className={styles.closeBtn} onClick={onClose} title="닫기">
                        <CloseOutlined />
                    </button>
                </div>

                <div className={styles.dropdownBody}>
                    {loading ? (
                        <div className={styles.loadingState}>
                            <Spin size="small" />
                            <span>보고서 목록 불러오는 중...</span>
                        </div>
                    ) : artifacts.length === 0 ? (
                        <div className={styles.emptyState}>
                            <FileTextOutlined />
                            <p>생성된 보고서가 없습니다.</p>
                        </div>
                    ) : (
                        <div className={styles.artifactList}>
                            {/* 최신순으로 위에서 아래로 표시 (backend에서 DESC 정렬) */}
                            {artifacts.map((artifact) => (
                                <div
                                    key={artifact.id}
                                    className={`${styles.artifactItem} ${selectedArtifactId === artifact.id ? styles.selected : ''}`}
                                    onClick={() => onSelect(artifact.id)}>
                                    {/* Radio Button */}
                                    <div className={styles.radioWrapper}>
                                        <input
                                            type="radio"
                                            name="artifact-select"
                                            className={styles.radio}
                                            checked={selectedArtifactId === artifact.id}
                                            onChange={() => onSelect(artifact.id)}
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                    </div>

                                    <div className={styles.artifactIcon}>
                                        <FileTextOutlined />
                                    </div>
                                    <div className={styles.artifactInfo}>
                                        <div className={styles.artifactName}>{artifact.filename}</div>
                                        <div className={styles.artifactMeta}>
                                            <span>{formatFileSize(artifact.file_size)}</span>
                                            <span>•</span>
                                            <span>{formatDate(artifact.created_at)}</span>
                                            <span>•</span>
                                            <span className={styles.artifactKind}>{artifact.kind.toUpperCase()}</span>
                                        </div>
                                    </div>
                                    <div className={styles.artifactActions}>
                                        {artifact.kind === 'md' && (
                                            <button
                                                className={styles.actionBtn}
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    onPreview(artifact)
                                                }}
                                                title="미리보기">
                                                미리보기
                                            </button>
                                        )}
                                        <button
                                            className={styles.actionBtn}
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                onDownload(artifact)
                                            }}
                                            title="다운로드">
                                            <DownloadOutlined />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        )
    }
)

ReportsDropdown.displayName = 'ReportsDropdown'

export default ReportsDropdown
