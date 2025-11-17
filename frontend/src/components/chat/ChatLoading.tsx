import React from 'react'
import styles from './ChatLoading.module.css'

/**
 * ChatLoading.tsx
 *
 * 주제를 선택하여 대화 내용 불러올 때, 로딩 표시 컴포넌트
 */
export const ChatLoading: React.FC = () => {
    return (
        <div className={styles.chatLoading}>
            <div className={styles.loadingIcon}>
                <div className={styles.spinner} />
            </div>
            <h2>대화 내용을 불러오는 중...</h2>
            <p>잠시만 기다려주세요.</p>
        </div>
    )
}
