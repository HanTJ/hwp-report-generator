import React, { useState, useRef, type KeyboardEvent, useEffect } from "react";
import {
  PaperClipOutlined,
  SendOutlined,
  GlobalOutlined,
  CloseOutlined,
  ControlOutlined,
} from "@ant-design/icons";
import { Switch } from "antd";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (message: string, files: File[], webSearchEnabled: boolean) => void;
  disabled?: boolean;
}

{
  /*
  웹사이트 추천 목록 (아이콘은 임시로 이모지 사용)
  const WEBSITE_SUGGESTIONS = [
    { name: '한국은행', url: 'https://www.bok.or.kr', icon: '🏦' },
    { name: '금융감독원', url: 'https://www.fss.or.kr', icon: '📊' },
    { name: '통계청', url: 'https://kostat.go.kr', icon: '📈' },
    { name: '네이버', url: 'https://www.naver.com', icon: '🔍' },
  ];
*/
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled = false }) => {
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMultiline, setIsMultiline] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isDropdownOpen]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (selectedFiles) {
      setFiles((prev) => [...prev, ...Array.from(selectedFiles)]);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemoveFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSend = () => {
    if (message.trim() || files.length > 0) {
      onSend(message, files, webSearchEnabled);
      setMessage("");
      setFiles([]);
      setIsMultiline(false);
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;

      // Check if textarea has multiple lines (scrollHeight > 1.5rem line height)
      const lineHeight = parseFloat(getComputedStyle(textareaRef.current).lineHeight);
      const lines = Math.floor(textareaRef.current.scrollHeight / lineHeight);
      setIsMultiline(lines > 1);
    }
  };

  const handleWebsiteClick = (url: string) => {
    const websiteMessage = `${url} 웹사이트의 정보를 참고하여 분석해주세요.`;
    setMessage((prev) =>
      prev ? `${prev}\n${websiteMessage}` : websiteMessage
    );
  };

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
              <button
                className={styles.removeFileBtn}
                onClick={() => handleRemoveFile(index)}
              >
                <CloseOutlined />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Box */}
      <div
        className={`${styles.chatInputBox} ${webSearchEnabled || isMultiline ? styles.multiRow : ""}`}
      >
        <div className={styles.leftButtons}>
          <button
            className={styles.attachBtn}
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            title="파일 첨부"
          >
            <PaperClipOutlined />
          </button>

          {/* Settings Button with Dropdown */}
          <div className={styles.settingsWrapper} ref={dropdownRef}>
            <button
              className={styles.settingsBtn}
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              disabled={disabled}
              title="설정"
            >
              <ControlOutlined />
            </button>

            {isDropdownOpen && (
              <div className={styles.dropdown}>
                <div className={styles.dropdownItem}>
                  <div className={styles.dropdownLabel}>
                    <GlobalOutlined />
                    <span>웹 검색</span>
                  </div>
                  <Switch
                    checked={webSearchEnabled}
                    onChange={setWebSearchEnabled}
                    size="small"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Web Search Chip */}
          {webSearchEnabled && (
            <div className={styles.webSearchChip}>
              <GlobalOutlined />
              <span>웹 검색</span>
              <button
                className={styles.chipCloseBtn}
                onClick={() => setWebSearchEnabled(false)}
                title="웹 검색 끄기"
              >
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

        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={disabled || (!message.trim() && files.length === 0)}
          title="전송"
        >
          <SendOutlined />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".hwpx,.txt,.pdf,.doc,.docx"
          onChange={handleFileSelect}
          style={{ display: "none" }}
        />
      </div>
    </div>
  );
};

export default ChatInput;
