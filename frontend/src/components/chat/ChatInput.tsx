import React, {useState, useRef, useEffect, forwardRef, useImperativeHandle, type KeyboardEvent} from 'react'
import {PaperClipOutlined, SendOutlined, GlobalOutlined, CloseOutlined, ControlOutlined, FileTextOutlined} from '@ant-design/icons'
import styles from './ChatInput.module.css'
import SettingsDropdown from './SettingsDropdown'

interface ChatInputProps {
    onSend: (message: string, files: File[], webSearchEnabled: boolean) => void
    disabled?: boolean
    onReportsClick?: () => void
    reportsDropdown?: React.ReactNode
}

export interface ChatInputHandle {
    focus: () => void
}

const ChatInput = forwardRef<ChatInputHandle, ChatInputProps>(({onSend, disabled = false, onReportsClick, reportsDropdown}, ref) => {
    const [message, setMessage] = useState('')
    const [files, setFiles] = useState<File[]>([])
    const [webSearchEnabled, setWebSearchEnabled] = useState(false)
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const textareaRef = useRef<HTMLTextAreaElement>(null)

    // 외부에서 포커스를 줄 수 있도록 노출
    useImperativeHandle(ref, () => ({
        focus: () => {
            textareaRef.current?.focus()
        }
    }))
    const dropdownRef = useRef<HTMLDivElement>(null)

    /*
     * 드롭다운 외부 클릭 시 닫기 핸들러
     */
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false)
            }
        }

        if (isDropdownOpen) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [isDropdownOpen])

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = event.target.files
        if (selectedFiles) {
            setFiles((prev) => [...prev, ...Array.from(selectedFiles)])
        }
        // Reset input
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    const handleRemoveFile = (index: number) => {
        setFiles((prev) => prev.filter((_, i) => i !== index))
    }

    /*
     * 메시지 전송 핸들러
     */
    const handleSend = () => {
        if (message.trim() || files.length > 0) {
            onSend(message, files, webSearchEnabled)
            setMessage('')
            setFiles([])
            // Reset textarea height
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto'
            }
        }
    }

    /*
     * 엔터키 입력 시, 메시지 전송 핸들러
     */
    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value)
        // Auto-resize textarea
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
        }
    }

    const handleWebsiteClick = (url: string) => {
        const websiteMessage = `${url} 웹사이트의 정보를 참고하여 분석해주세요.`
        setMessage((prev) => (prev ? `${prev}\n${websiteMessage}` : websiteMessage))
    }

    /*
     * 웹 검색 스위치 핸들러
     */
    const handleWebSearchChange = (enabled: boolean) => {
        setWebSearchEnabled(enabled)
        setIsDropdownOpen(false)
    }

    return (
        <div className={styles.chatInputContainer}>
            {/* Website Suggestions */}
            {/*
        {webSearchEnabled && (
          <div className={styles.websiteSuggestions}>
            {WEBSITE_SUGGESTIONS.map((website) => (
              <button
                key={website.url}
                className={styles.websiteBtn}
                onClick={() => handleWebsiteClick(website.url)}
                disabled={disabled}
              >
                <span className={styles.websiteIcon}>{website.icon}</span>
                <span className={styles.websiteName}>{website.name}</span>
              </button>
            ))}
          </div>
        )}
      */}

            {/* Uploaded Files */}
            {files.length > 0 && (
                <div className={styles.uploadedFiles}>
                    {files.map((file, index) => (
                        <div key={index} className={styles.uploadedFile}>
                            <PaperClipOutlined />
                            <span className={styles.fileName}>{file.name}</span>
                            <button className={styles.removeFileBtn} onClick={() => handleRemoveFile(index)}>
                                <CloseOutlined />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Input Box */}
            <div className={`${styles.chatInputBox} ${styles.multiRow}`}>
                <div className={styles.leftButtons}>
                    <button className={styles.attachBtn} onClick={() => fileInputRef.current?.click()} disabled={disabled} title="파일 첨부">
                        <PaperClipOutlined />
                    </button>

                    {/* Reports Button with Dropdown */}
                    <div className={styles.reportsWrapper}>
                        <button className={styles.reportsBtn} onClick={onReportsClick} disabled={disabled} title="참조 보고서 선택">
                            <FileTextOutlined />
                        </button>
                        {/* Reports Dropdown */}
                        {reportsDropdown}
                    </div>

                    {/* Settings Button with Dropdown */}
                    <div className={styles.settingsWrapper}>
                        <button className={styles.settingsBtn} onClick={() => setIsDropdownOpen(!isDropdownOpen)} disabled={disabled} title="설정">
                            <ControlOutlined />
                        </button>

                        {isDropdownOpen && (
                            <SettingsDropdown ref={dropdownRef} webSearchEnabled={webSearchEnabled} onWebSearchChange={handleWebSearchChange} />
                        )}
                    </div>

                    {/* Web Search Chip */}
                    {webSearchEnabled && (
                        <div className={styles.webSearchChip}>
                            <GlobalOutlined />
                            <span>웹 검색</span>
                            <button className={styles.chipCloseBtn} onClick={() => setWebSearchEnabled(false)} title="웹 검색 끄기">
                                <CloseOutlined />
                            </button>
                        </div>
                    )}
                </div>

                <textarea
                    ref={textareaRef}
                    className={styles.chatTextarea}
                    placeholder="보고서 주제를 입력하세요... (Shift+Enter로 줄바꿈)"
                    value={message}
                    onChange={handleTextareaChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled}
                    rows={1}
                />

                <button className={styles.sendBtn} onClick={handleSend} disabled={disabled || (!message.trim() && files.length === 0)} title="전송">
                    <SendOutlined />
                </button>

                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".hwpx,.txt,.pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    style={{display: 'none'}}
                />
            </div>
        </div>
    )
})

ChatInput.displayName = 'ChatInput'

export default ChatInput
