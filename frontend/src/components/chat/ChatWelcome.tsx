/**
 * ChatWelcome.tsx
 *
 * 채팅 시작 전 환영 화면
 */

import React from 'react'
import {useTopicStore} from '../../stores/useTopicStore'
import styles from './ChatWelcome.module.css'

export const ChatWelcome = () => {
    // store에서 선택된 템플릿 정보 가져오기
    const selectedTemplate = useTopicStore((state) => state.selectedTemplate)

    return (
        <div className={styles.chatWelcome}>
            <div className={styles.welcomeIcon}>
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                    <circle cx="24" cy="24" r="24" fill="#E8F0FE" />
                    <path
                        d="M24 14C18.48 14 14 18.48 14 24C14 29.52 18.48 34 24 34C29.52 34 34 29.52 34 24C34 18.48 29.52 14 24 14ZM24 32C19.59 32 16 28.41 16 24C16 19.59 19.59 16 24 16C28.41 16 32 19.59 32 24C32 28.41 28.41 32 24 32Z"
                        fill="#1976D2"
                    />
                    <path d="M22 21H26V23H22V21ZM22 25H26V27H22V25Z" fill="#1976D2" />
                </svg>
            </div>
            <h1>보고서를 생성해보세요!</h1>
            <p>주제를 입력하면 AI가 자동으로 보고서를 작성합니다.</p>
            {selectedTemplate && (
                <p className={styles.templateInfo}>
                    (현재 템플릿: {selectedTemplate.title})
                </p>
            )}
        </div>
    )
}
