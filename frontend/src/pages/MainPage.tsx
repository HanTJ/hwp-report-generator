import React, {useState, useRef, useEffect} from 'react'
import {message as antdMessage} from 'antd'
import {MenuOutlined} from '@ant-design/icons'
import ChatMessage from '../components/chat/ChatMessage'
import ChatInput from '../components/chat/ChatInput'
import ReportPreview from '../components/report/ReportPreview'
import ReportsDropdown from '../components/chat/ReportsDropdown'
import {ChatWelcome} from '../components/chat/ChatWelcome'
import {GeneratingIndicator} from '../components/chat/GeneratingIndicator'
import Sidebar from '../components/layout/Sidebar'
import styles from './MainPage.module.css'
import MainLayout from '../components/layout/MainLayout'
import {artifactApi} from '../services/artifactApi'
import {useTopicStore} from '../stores/useTopicStore'
import {useMessages} from '../hooks/useMessages'
import {useMessageStore} from '../stores/useMessageStore'
import {useArtifactHandlers} from '../hooks/useArtifactHandlers'
import {useChatActions} from '../hooks/useChatActions'

interface DownloadedFile {
    id: number
    filename: string
    downloadUrl: string
    size: string
    timestamp: Date
}

const MainPage: React.FC = () => {
    // 🎯 Custom Hooks로 상태 관리 간소화
    const {selectedTopicId, setSelectedTopicId} = useTopicStore()
    const {messages, setMessages, isLoadingMessages, refreshMessages} = useMessages(selectedTopicId)
    const {isGeneratingMessage, isDeletingMessage} = useMessageStore()

    const {
        isReportsDropdownOpen,
        setIsReportsDropdownOpen,
        getMarkdownArtifacts,
        getSelectedArtifactId,
        loadingTopics,
        handleReportsClick,
        handleArtifactSelect,
        handleArtifactDownload,
        handleArtifactPreview
    } = useArtifactHandlers()

    const {handleSendMessage: sendMessage, handleDeleteMessage: deleteMessage} = useChatActions({
        selectedTopicId,
        setSelectedTopicId,
        setMessages,
        refreshMessages
    })

    // UI 상태
    const [selectedReport, setSelectedReport] = useState<{
        filename: string
        content: string
        messageId: number
        reportId: number
    } | null>(null)
    const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([])
    const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(false)

    const lastUserMessageRef = useRef<HTMLDivElement>(null)
    const reportsDropdownRef = useRef<HTMLDivElement>(null)

    // Close reports dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (reportsDropdownRef.current && !reportsDropdownRef.current.contains(event.target as Node)) {
                setIsReportsDropdownOpen(false)
            }
        }

        if (isReportsDropdownOpen) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [isReportsDropdownOpen])

    // 두 번째 메시지부터 마지막 사용자 메시지를 헤더 아래로 스크롤
    useEffect(() => {
        if (messages.length > 2 && lastUserMessageRef.current) {
            const lastMessage = messages[messages.length - 1]
            if (lastMessage.type === 'user') {
                setTimeout(() => {
                    lastUserMessageRef.current?.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    })
                }, 100)
            }
        }
    }, [messages])

    /**
     * 메시지 내 보고서 클릭 - 미리보기 열기
     */
    const handleReportClick = (reportData: {filename: string; content: string; messageId: number; reportId: number}) => {
        setSelectedReport(reportData)
    }

    /**
     * 메시지 내 보고서 다운로드 핸들러
     */
    const handleDownload = async (reportData: {filename: string; content: string; reportId: number; messageId: number}) => {
        try {
            antdMessage.loading({
                content: 'HWPX 파일 다운로드 중...',
                key: 'download',
                duration: 0
            })

            const hwpxFilename = reportData.filename.replace('.md', '.hwpx')
            await artifactApi.downloadMessageHwpx(reportData.messageId, hwpxFilename)

            antdMessage.destroy('download')

            const downloadedFile: DownloadedFile = {
                id: reportData.messageId,
                filename: hwpxFilename,
                downloadUrl: `#`,
                size: '알 수 없음',
                timestamp: new Date()
            }

            setDownloadedFiles((prev) => [...prev, downloadedFile])
            antdMessage.success('HWPX 파일이 다운로드되었습니다.')
        } catch (error: any) {
            console.error('Download failed:', error)
            antdMessage.error('HWPX 파일 다운로드에 실패했습니다.')
        }
    }

    /**
     * 메시지 삭제 핸들러 (useChatActions 훅 래핑)
     */
    const handleDeleteMessage = async (messageId: number) => {
        await deleteMessage(messageId, setSelectedReport, selectedReport, messages)
    }

    /**
     * 보고서 미리보기 닫기
     */
    const handleClosePreview = () => {
        setSelectedReport(null)
    }

    /**
     * 새 토픽 시작
     */
    const handleNewTopic = () => {
        setSelectedTopicId(null)
        setMessages([])
    }

    /**
     * 사이드바 토글
     */
    const handleToggleSidebar = () => {
        setIsLeftSidebarOpen(!isLeftSidebarOpen)
    }

    return (
        <MainLayout sidebarCollapsed={!isLeftSidebarOpen}>
            {/* Dim Overlay - 모바일/태블릿에서 사이드바 열렸을 때 */}
            {isLeftSidebarOpen && <div className={styles.dimOverlay} onClick={handleToggleSidebar} />}

            <Sidebar isOpen={isLeftSidebarOpen} onToggle={handleToggleSidebar} onTopicSelect={setSelectedTopicId} onNewTopic={handleNewTopic} />

            <div className={`${styles.mainChatPage} ${isLeftSidebarOpen ? styles.sidebarExpanded : styles.sidebarCollapsed}`}>
                {/* 햄버거 메뉴 버튼 - 모바일/태블릿에서만 표시 */}
                <button className={styles.hamburgerBtn} onClick={handleToggleSidebar} aria-label="메뉴 열기">
                    <MenuOutlined />
                </button>
                <div className={styles.chatContainer}>
                    <div className={styles.chatContent}>
                        {isLoadingMessages ? (
                            // 메시지 로딩 중일 때는 빈 화면 표시
                            <div></div>
                        ) : messages.length === 0 ? (
                            <ChatWelcome />
                        ) : (
                            <div className={styles.chatMessages}>
                                {messages.map((message, index) => {
                                    const isLastUserMessage = message.type === 'user' && index === messages.length - 1

                                    return (
                                        <div key={message.id} ref={isLastUserMessage ? lastUserMessageRef : null}>
                                            <ChatMessage
                                                message={message}
                                                onReportClick={handleReportClick}
                                                onDownload={handleDownload}
                                                onDelete={handleDeleteMessage}
                                                isGenerating={isGeneratingMessage}
                                                isDeleting={isDeletingMessage}
                                            />
                                        </div>
                                    )
                                })}
                                {isGeneratingMessage && <GeneratingIndicator />}
                            </div>
                        )}
                    </div>

                    <div className={styles.chatInputWrapper}>
                        <ChatInput
                            onSend={sendMessage}
                            disabled={isGeneratingMessage}
                            onReportsClick={() => handleReportsClick(selectedTopicId)}
                            reportsDropdown={
                                isReportsDropdownOpen && selectedTopicId ? (
                                    <ReportsDropdown
                                        ref={reportsDropdownRef}
                                        artifacts={getMarkdownArtifacts(selectedTopicId)}
                                        loading={loadingTopics.has(selectedTopicId)}
                                        selectedArtifactId={getSelectedArtifactId(selectedTopicId)}
                                        onSelect={(id) => handleArtifactSelect(selectedTopicId, id)}
                                        onClose={() => setIsReportsDropdownOpen(false)}
                                        onDownload={(art) => handleArtifactDownload(art, selectedTopicId)}
                                        onPreview={(art) => handleArtifactPreview(art, setSelectedReport)}
                                    />
                                ) : null
                            }
                        />
                    </div>
                </div>

                {selectedReport && (
                    <ReportPreview report={selectedReport} onClose={handleClosePreview} onDownload={() => handleDownload(selectedReport)} />
                )}
            </div>
        </MainLayout>
    )
}

export default MainPage
