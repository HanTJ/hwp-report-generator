import React from 'react'
import {Button, Space} from 'antd'

interface OutlineActionButtonsProps {
    onGenerateReport: () => void
    onContinue: () => void
    showButtons: boolean // 버튼을 보여줄지 여부
}

/**
 * 개요 확인 액션 버튼
 *
 * "보고서를 만드시겠습니까?" 질문과 함께 "예/아니오" 버튼을 표시합니다.
 * show가 false이면 아무것도 렌더링하지 않습니다.
 */
export const OutlineActionButtons = ({onGenerateReport, onContinue, showButtons}: OutlineActionButtonsProps) => {
    if (!showButtons) {
        return null
    }

    return (
        <div style={{marginTop: 16, paddingTop: 16, borderTop: '1px solid #e8e8e8'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '2rem'}}>
                <span style={{fontWeight: 500}}>보고서를 만드시겠습니까?</span>
                <Space>
                    <Button onClick={onContinue}>수정</Button>
                    <Button type="primary" onClick={onGenerateReport}>
                        생성
                    </Button>
                </Space>
            </div>
        </div>
    )
}
