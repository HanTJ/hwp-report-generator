import React from "react";
import { FileTextOutlined, DownloadOutlined } from "@ant-design/icons";
import { useAuth } from "../../hooks/useAuth";
import styles from "./ChatMessage.module.css";

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
  reportData?: {
    filename: string;
    reportId: number;
    content: string;
  };
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
  onReportClick: (reportData: {
    filename: string;
    content: string;
    reportId: number;
  }) => void;
  onDownload: (reportData: { filename: string; reportId: number }) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onReportClick,
  onDownload,
}) => {
  const { user } = useAuth();
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className={`${styles.chatMessage} ${styles[message.type]}`}>
      <div className={styles.messageAvatar}>
        {message.type === "user" ? (
          <div className={styles.userAvatar}>U</div>
        ) : (
          <div className={styles.assistantAvatar}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="12" fill="#E8F0FE" />
              <path
                d="M12 7C9.24 7 7 9.24 7 12C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12C17 9.24 14.76 7 12 7ZM12 15.5C10.07 15.5 8.5 13.93 8.5 12C8.5 10.07 10.07 8.5 12 8.5C13.93 8.5 15.5 10.07 15.5 12C15.5 13.93 13.93 15.5 12 15.5Z"
                fill="#1976D2"
              />
              <path
                d="M11 10.5H13V11.5H11V10.5ZM11 12.5H13V13.5H11V12.5Z"
                fill="#1976D2"
              />
            </svg>
          </div>
        )}
      </div>

      <div className={styles.messageContentWrapper}>
        <div className={styles.messageHeader}>
          <span className={styles.messageSender}>
            {message.type === "user" ? (
              <span>{user?.username || "사용자"} </span>
            ) : (
              "Assistant"
            )}
          </span>
          <span className={styles.messageTime}>
            {formatTime(message.timestamp)}
          </span>
        </div>

        <div className={styles.messageContent}>
          <p>
            {message.reportData ? (
              // reportData가 있으면 간단한 안내 메시지만 표시
              "보고서가 성공적으로 생성되었습니다!"
            ) : (
              // reportData가 없으면 전체 내용 표시
              message.content.split("\n").map((line, index) => (
                <React.Fragment key={index}>
                  {line}
                  {index < message.content.split("\n").length - 1 && <br />}
                </React.Fragment>
              ))
            )}
          </p>

          {message.reportData && (
            <div className={styles.reportAttachment}>
              <div
                className={styles.reportFile}
                onClick={() => onReportClick(message.reportData!)}
              >
                <div className={styles.reportIcon}>
                  <FileTextOutlined />
                </div>
                <div className={styles.reportInfo}>
                  <div className={styles.reportFilename}>
                    {message.reportData.filename}
                  </div>
                  <div className={styles.reportMeta}>
                    HWPX 파일 • 클릭하여 미리보기
                  </div>
                </div>
              </div>
              <button
                className={styles.reportDownloadBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  onDownload({
                    filename: message.reportData!.filename,
                    reportId: message.reportData!.reportId,
                  });
                }}
                title="다운로드"
              >
                <DownloadOutlined />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
