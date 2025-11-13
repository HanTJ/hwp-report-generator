import React from 'react'
import styles from './ChatMessage.module.css'

interface UserMessageCardProps {
    content: string
    timestamp: Date
}

/**
 * 사용자 메시지 카드
 * 
 * ChatMessage 스타일을 재사용하여 사용자 메시지를 표시합니다.
 */
export const UserMessageCard: React.FC<UserMessageCardProps> = ({content, timestamp}) => {
    const formatTime = (date: Date) => {
        return date.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <div className={`${styles.chatMessage} ${styles.user}`}>
            <div className={styles.messageAvatar}>
                <div className={styles.userAvatar}>U</div>
            </div>
            <div className={styles.messageContentWrapper}>
                <div className={styles.messageHeader}>
                    <span className={styles.messageSender}>사용자</span>
                    <span className={styles.messageTime}>{formatTime(timestamp)}</span>
                </div>
                <div className={styles.messageContent}>
                    <p style={{whiteSpace: 'pre-wrap'}}>{content}</p>
                </div>
            </div>
        </div>
    )
}
