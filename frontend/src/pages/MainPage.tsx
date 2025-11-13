import {useState, useRef, useEffect} from 'react'
import {message as antdMessage} from 'antd'
import {MenuOutlined} from '@ant-design/icons'
import {OutlineMessage} from '../components/OutlineMessage'
import {topicApi} from '../services/topicApi'
import ChatMessage from '../components/chat/ChatMessage'
import ChatInput, {type ChatInputHandle} from '../components/chat/ChatInput'
import ReportPreview from '../components/report/ReportPreview'
import ReportsDropdown from '../components/chat/ReportsDropdown'
import {ChatWelcome} from '../components/chat/ChatWelcome'
import {GeneratingIndicator} from '../components/chat/GeneratingIndicator'
import Sidebar from '../components/layout/Sidebar'
import styles from './MainPage.module.css'
import MainLayout from '../components/layout/MainLayout'
import {artifactApi} from '../services/artifactApi'
import {useTopicStore} from '../stores/useTopicStore'
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

const MainPage = () => {
    // 주제 관리 (임시 topicId 관리 포함)
    const {selectedTopicId, setSelectedTopicId, resetTempCounter, handleTopicPlanWithMessages} = useTopicStore()

    // 메시지 관리 (outline 메시지 추가 기능 포함)
    const {
        addMessages,
        getMessagesUI,
        setMessages,
        isLoadingMessages,
        isGeneratingMessage,
        isDeletingMessage,
        fetchMessages,
        refreshMessages,
        setIsLoadingMessages
    } = useMessageStore()

    // 현재 topic의 메시지 가져오기 (UI 모델로 자동 변환)
    const messages = selectedTopicId ? getMessagesUI(selectedTopicId) : []

    // 선택된 주제가 변경되면 메시지 자동 조회
    useEffect(() => {
        if (selectedTopicId) {
            // api 호출하여 메시지를 불러온 후 상태에 설정
            fetchMessages(selectedTopicId)
        }
    }, [selectedTopicId])

    // Outline 모드 상태 (단순화)
    const [isOutlineMode, setIsOutlineMode] = useState(false)

    // 아티팩트(보고서) 관련 핸들러
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

    // 채팅 액션 훅
    const {handleSendMessage: sendMessage, handleDeleteMessage: deleteMessage} = useChatActions({
        selectedTopicId,
        setSelectedTopicId,
        setMessages,
        refreshMessages
    })

    /**
     * 메시지 전송 래퍼 함수
     * 첫 메시지일 경우 개요 모드(임시 topicId 생성)로 전환
     */
    const handleSendMessage = async (message: string, files: File[], webSearchEnabled: boolean) => {
        // 보고서 생성 이전인 개요인 경우, 메시지 전송
        if (selectedTopicId === null) {
            setIsOutlineMode(true)
            // TODO: template_id 지정 (현재는 1)
            await handleTopicPlanWithMessages(1, message, addMessages)
        } else {
            // 보고서 생성 이후로 토픽이 만들어진 이후인 경우, 메시지 전송
            await sendMessage(message, files, webSearchEnabled)
        }
    }

    // UI 상태
    const chatInputRef = useRef<ChatInputHandle>(null)

    // 보고서 미리보기 상태
    const [selectedReport, setSelectedReport] = useState<{
        filename: string
        content: string
        messageId: number
        reportId: number
    } | null>(null)

    // 다운로드된 파일 목록
    const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([])

    // 사이드바 열림 상태
    const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(false)

    // 마지막 사용자 메시지 참조 (스크롤용)
    const lastUserMessageRef = useRef<HTMLDivElement>(null)

    // 보고서 드롭다운 참조
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
            if (lastMessage.role === 'user') {
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
     * 새 토픽 시작 시
     */
    const handleNewTopik = () => {
        setIsOutlineMode(true)
        setSelectedTopicId(null)
        resetTempCounter()
        // 메시지는 selectedTopicId가 null이면 빈 배열 반환 (자동 처리)
    }

    /**
     * "예" 클릭 → 보고서 생성 (실제 API)
     */
    const handleGenerateFromOutline = async () => {
        if (!selectedTopicId || selectedTopicId >= 0) {
            antdMessage.error('개요 모드가 아닙니다.')
            return
        }

        try {
            setIsLoadingMessages(true)

            // 마지막 outline 메시지의 content 가져오기
            const currentMessages = getMessagesUI(selectedTopicId)
            const lastMessage = currentMessages[currentMessages.length - 1]

            if (!lastMessage || !lastMessage.content) {
                antdMessage.error('메시지가 없습니다.')
                return
            }

            antdMessage.loading({
                content: '보고서 생성 중...',
                key: 'generate',
                duration: 0
            })

            // 주제 생성 및 MD 파일 응답하는 API 호출
            const response = await topicApi.generateTopic({
                input_prompt: lastMessage.content,
                language: 'ko'
            })

            antdMessage.destroy('generate')
            antdMessage.success('보고서가 생성되었습니다.')

            // 1. 개요 모드 종료
            setIsOutlineMode(false)

            // 2. 생성된 실제 Topic ID로 전환
            // ✅ 중요: 임시 topicId의 메시지는 유지됨 (삭제하지 않음)
            // fetchMessages가 실행되면 MSW가 pending 메시지 + 보고서 메시지를 함께 반환
            setSelectedTopicId(response.topic_id)

            // 3. fetchMessages는 useEffect에서 자동 실행됨
        } catch (error: any) {
            console.error('보고서 생성 실패:', error)
            antdMessage.destroy('generate')
            antdMessage.error('보고서 생성에 실패했습니다.')
        } finally {
            setIsLoadingMessages(false)
        }
    }

    /**
     * "아니오" 클릭 → 계속 대화
     */
    const handleContinueOutline = () => {
        antdMessage.info('추가 메시지를 입력해주세요.')
        // 입력창에 포커스
        chatInputRef.current?.focus()
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

            <Sidebar isOpen={isLeftSidebarOpen} onToggle={handleToggleSidebar} onTopicSelect={setSelectedTopicId} onNewTopic={handleNewTopik} />

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
                        ) : isOutlineMode ? (
                            // 개요 모드 - 통합된 메시지 사용
                            <div className={styles.chatMessages}>
                                {messages.map((message, index) => (
                                    <OutlineMessage
                                        key={index}
                                        message={message}
                                        onGenerateReport={handleGenerateFromOutline}
                                        onContinue={handleContinueOutline}
                                    />
                                ))}
                                {isLoadingMessages && <GeneratingIndicator />}
                            </div>
                        ) : messages.length === 0 ? (
                            <ChatWelcome />
                        ) : (
                            <div className={styles.chatMessages}>
                                {messages.map((message, index) => {
                                    const isLastUserMessage = message.role === 'user' && index === messages.length - 1

                                    return (
                                        <div key={message.id || index} ref={isLastUserMessage ? lastUserMessageRef : null}>
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
                            ref={chatInputRef}
                            onSend={handleSendMessage}
                            disabled={isGeneratingMessage || isLoadingMessages}
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
