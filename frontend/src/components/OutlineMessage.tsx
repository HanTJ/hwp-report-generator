import type {MessageUI} from '../models/ui/MessageUI'
import {AssistantOutlineCard} from './chat/AssistantOutlineCard'
import {OutlineActionButtons} from './chat/OutlineActionButtons'
import {useState} from 'react'

interface OutlineMessageProps {
    message: MessageUI // outline 모드의 MessageUI
    onGenerateReport: () => void
    onContinue?: () => void
}

/**
 * 개요(Outline) 메시지 컴포넌트
 *
 * outline 모드의 MessageUI를 표시합니다.
 * - User message: 사용자가 입력한 메시지
 * - Assistant message: AI가 생성한 outline (content에 저장됨)
 * - Action buttons: "예/아니오" 버튼 (최신 assistant 메시지에만 표시)
 */
export const OutlineMessage = ({message, onGenerateReport, onContinue}: OutlineMessageProps) => {
    const [showButtons, setShowButtons] = useState(true)

    const handleGenerateReport = () => {
        setShowButtons(false)
        onGenerateReport()
    }

    const handleContinue = () => {
        setShowButtons(false)
        onContinue?.()
    }

    // Assistant 메시지: 개요 내용 + 버튼
    return (
        <AssistantOutlineCard content={message.content} timestamp={message.timestamp}>
            <OutlineActionButtons onGenerateReport={handleGenerateReport} onContinue={handleContinue} showButtons={showButtons} />
        </AssistantOutlineCard>
    )
}
