import React from 'react'
import styles from './ChatMessage.module.css'

interface AssistantOutlineCardProps {
    content: string
    timestamp: Date
    children?: React.ReactNode  // For action buttons
}

/**
 * AI 개요 메시지 카드
 * 
 * ChatMessage 스타일을 재사용하여 AI가 생성한 개요를 표시합니다.
 * children을 통해 하단에 액션 버튼을 추가할 수 있습니다.
 */
export const AssistantOutlineCard: React.FC<AssistantOutlineCardProps> = ({content, timestamp, children}) => {
    const formatTime = (date: Date) => {
        return date.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <div className={`${styles.chatMessage} ${styles.assistant}`}>
            <div className={styles.messageAvatar}>
                <div className={styles.assistantAvatar}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="12" fill="#E8F0FE" />
                        <path
                            d="M12 7C9.24 7 7 9.24 7 12C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12C17 9.24 14.76 7 12 7ZM12 15.5C10.07 15.5 8.5 13.93 8.5 12C8.5 10.07 10.07 8.5 12 8.5C13.93 8.5 15.5 10.07 15.5 12C15.5 13.93 13.93 15.5 12 15.5Z"
                            fill="#1976D2"
                        />
                        <path d="M11 10.5H13V11.5H11V10.5ZM11 12.5H13V13.5H11V12.5Z" fill="#1976D2" />
                    </svg>
                </div>
            </div>
            <div className={styles.messageContentWrapper}>
                <div className={styles.messageHeader}>
                    <span className={styles.messageSender}>Assistant</span>
                    <span className={styles.messageTime}>{formatTime(timestamp)}</span>
                </div>
                <div className={styles.messageContent}>
                    <p style={{whiteSpace: 'pre-wrap'}}>{content}</p>
                    {children}
                </div>
            </div>
        </div>
    )
}
