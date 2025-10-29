import React, { useState, useRef, useEffect } from "react";
import ChatMessage from "../components/chat/ChatMessage";
import ChatInput from "../components/chat/ChatInput";
import ReportPreview from "../components/report/ReportPreview";
import DownloadedFiles from "../components/report/DownloadedFiles";
import styles from "./MainChatPage.module.css";
import MainLayout from "../components/layout/MainLayout";

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

interface DownloadedFile {
  id: number;
  filename: string;
  downloadUrl: string;
  size: string;
  timestamp: Date;
}

const MainChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedReport, setSelectedReport] = useState<{
    filename: string;
    content: string;
    reportId: number;
  } | null>(null);
  const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const lastUserMessageRef = useRef<HTMLDivElement>(null);

  // 두 번째 메시지부터 마지막 사용자 메시지를 헤더 아래로 스크롤
  useEffect(() => {
    if (messages.length > 2 && lastUserMessageRef.current) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.type === "user") {
        setTimeout(() => {
          lastUserMessageRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }, 100);
      }
    }
  }, [messages]);

  const handleSendMessage = async (
    message: string,
    files: File[],
    webSearchEnabled: boolean
  ) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsGenerating(true);

    try {
      // TODO: Call API to generate report
      // For now, simulate with a timeout
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Mock report generation disabled for now
      const mockReportContent = `제목: ${message}
      
      // 배경 및 목적:
      // 이 보고서는 ${message}에 대한 분석을 제공합니다.
      //
      // 주요 내용:
      // 1. 현황 분석
      // 2. 주요 이슈
      // 3. 개선 방안
      //
      // 결론 및 제언:
      // 향후 전략 방향을 제시합니다.`;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "보고서가 생성되었습니다.",
        reportData: {
          filename: `${message.slice(0, 20)}_보고서.hwpx`,
          reportId: Date.now(),
          content: mockReportContent,
        },
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error generating report:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "보고서 생성 중 오류가 발생했습니다.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReportClick = (reportData: {
    filename: string;
    content: string;
    reportId: number;
  }) => {
    setSelectedReport(reportData);
  };

  const handleDownload = (reportData: {
    filename: string;
    reportId: number;
  }) => {
    // Add to downloaded files
    const downloadedFile: DownloadedFile = {
      id: reportData.reportId,
      filename: reportData.filename,
      downloadUrl: `#`, // TODO: Add actual download URL
      size: "125 KB",
      timestamp: new Date(),
    };

    setDownloadedFiles((prev) => [...prev, downloadedFile]);

    // TODO: Trigger actual download
    console.log("Downloading:", reportData.filename);
  };

  const handleClosePreview = () => {
    setSelectedReport(null);
  };

  return (
    <MainLayout>
      <div className={styles.mainChatPage}>
        <div className={styles.chatContainer}>
          <div className={styles.chatContent}>
            {messages.length === 0 ? (
              <div className={styles.chatWelcome}>
                <div className={styles.welcomeIcon}>
                  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                    <circle cx="24" cy="24" r="24" fill="#E8F0FE" />
                    <path
                      d="M24 14C18.48 14 14 18.48 14 24C14 29.52 18.48 34 24 34C29.52 34 34 29.52 34 24C34 18.48 29.52 14 24 14ZM24 32C19.59 32 16 28.41 16 24C16 19.59 19.59 16 24 16C28.41 16 32 19.59 32 24C32 28.41 28.41 32 24 32Z"
                      fill="#1976D2"
                    />
                    <path
                      d="M22 21H26V23H22V21ZM22 25H26V27H22V25Z"
                      fill="#1976D2"
                    />
                  </svg>
                </div>
                <h1>보고서를 생성해보세요</h1>
                <p>주제를 입력하면 AI가 자동으로 보고서를 작성합니다</p>
              </div>
            ) : (
              <div className={styles.chatMessages}>
                {messages.map((message, index) => {
                  const isLastUserMessage =
                    message.type === "user" &&
                    index === messages.length - 1;

                  return (
                    <div
                      key={message.id}
                      ref={isLastUserMessage ? lastUserMessageRef : null}
                    >
                      <ChatMessage
                        message={message}
                        onReportClick={handleReportClick}
                        onDownload={handleDownload}
                      />
                    </div>
                  );
                })}
                {isGenerating && (
                  <div className={styles.generatingIndicator}>
                    <div className={styles.generatingDots}>
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span>보고서 생성 중...</span>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className={styles.chatInputWrapper}>
            {downloadedFiles.length > 0 && (
              <DownloadedFiles files={downloadedFiles} />
            )}
            <ChatInput onSend={handleSendMessage} disabled={isGenerating} />
          </div>
        </div>

        {selectedReport && (
          <ReportPreview
            report={selectedReport}
            onClose={handleClosePreview}
            onDownload={() => handleDownload(selectedReport)}
          />
        )}
      </div>
    </MainLayout>
  );
};

export default MainChatPage;
