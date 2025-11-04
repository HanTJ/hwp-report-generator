/**
 * GeneratingIndicator.tsx
 * 
 * 보고서 생성 중 표시 컴포넌트
 */

import React from 'react'
import styles from './GeneratingIndicator.module.css'

export const GeneratingIndicator: React.FC = () => {
    return (
        <div className={styles.generatingIndicator}>
            <div className={styles.generatingDots}>
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>보고서 생성 중...</span>
        </div>
    )
}
