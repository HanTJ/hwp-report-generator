import React, { useState, useRef, useEffect } from "react";
import { message as antdMessage } from "antd";
import ChatMessage from "../components/chat/ChatMessage";
import ChatInput from "../components/chat/ChatInput";
import ReportPreview from "../components/report/ReportPreview";
import DownloadedFiles from "../components/report/DownloadedFiles";
import Sidebar from "../components/layout/Sidebar";
import styles from "./MainChatPage.module.css";
import MainLayout from "../components/layout/MainLayout";
import { topicApi } from "../services/topicApi";
import { messageApi } from "../services/messageApi";
import { artifactApi } from "../services/artifactApi";
import type { Message as MessageType } from "../types/message";
import type { Artifact } from "../types/artifact";

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
  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(false);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
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
    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: "temp-" + Date.now(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);
    setIsGenerating(true);

    try {
      let currentTopicId = selectedTopicId;

      // 첫 메시지: 토픽 생성
      if (currentTopicId === null) {
        const topic = await topicApi.createTopic({
          input_prompt: message,
          language: "ko",
        });
        currentTopicId = topic.id;
        setSelectedTopicId(topic.id);
      }

      // 사용자 메시지 전송
      await messageApi.createMessage(currentTopicId, {
        role: "user",
        content: message,
      });

      // AI가 응답 생성할 시간 대기 (1.5초)
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // 메시지 목록 재조회 (AI 응답 포함)
      const messagesResponse = await messageApi.listMessages(currentTopicId);

      // UI 업데이트
      const uiMessages: Message[] = messagesResponse.messages.map((msg) => ({
        id: msg.id.toString(),
        type: msg.role === "user" ? "user" : "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));

      setMessages(uiMessages);

      // 아티팩트 목록 불러오기 (보고서가 생성되었는지 확인)
      try {
        const artifactsResponse = await artifactApi.listArtifactsByTopic(
          currentTopicId
        );

        // 아티팩트가 있으면 메시지에 연결
        if (artifactsResponse.artifacts.length > 0) {
          const messagesWithArtifacts = await Promise.all(
            uiMessages.map(async (msg) => {
              // 이 메시지와 연결된 아티팩트 찾기 (가장 최근 MD 파일)
              const relatedArtifact = artifactsResponse.artifacts.find(
                (art) => art.kind === "md"
              );

              if (relatedArtifact && msg.type === "assistant") {
                try {
                  const contentResponse = await artifactApi.getArtifactContent(
                    relatedArtifact.id
                  );
                  return {
                    ...msg,
                    reportData: {
                      filename: relatedArtifact.filename,
                      reportId: relatedArtifact.id,
                      content: contentResponse.content,
                    },
                  };
                } catch (error) {
                  console.error("Failed to load artifact content:", error);
                  return msg;
                }
              }

              return msg;
            })
          );

          setMessages(messagesWithArtifacts);
        }
      } catch (error) {
        console.error("Failed to load artifacts:", error);
        // 아티팩트 로딩 실패해도 메시지는 표시
      }
    } catch (error: any) {
      console.error("Error sending message:", error);
      antdMessage.error(error.message || "메시지 전송에 실패했습니다.");

      // 에러 메시지 추가
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.",
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

  const handleDownload = async (reportData: {
    filename: string;
    reportId: number;
  }) => {
    try {
      // 실제 파일 다운로드 실행
      await artifactApi.downloadArtifact(reportData.reportId);

      // Add to downloaded files
      const downloadedFile: DownloadedFile = {
        id: reportData.reportId,
        filename: reportData.filename,
        downloadUrl: `#`,
        size: "125 KB", // TODO: Get actual file size from artifact metadata
        timestamp: new Date(),
      };

      setDownloadedFiles((prev) => [...prev, downloadedFile]);
      antdMessage.success("파일이 다운로드되었습니다.");
    } catch (error: any) {
      console.error("Download failed:", error);
      antdMessage.error(error.message || "파일 다운로드에 실패했습니다.");
    }
  };

  const handleClosePreview = () => {
    setSelectedReport(null);
  };

  const handleTopicSelect = async (topicId: number) => {
    setSelectedTopicId(topicId);
    setIsGenerating(true);

    try {
      // 선택된 토픽의 메시지 불러오기
      const messagesResponse = await messageApi.listMessages(topicId);

      // UI 메시지 형식으로 변환
      const uiMessages: Message[] = messagesResponse.messages.map((msg) => ({
        id: msg.id.toString(),
        type: msg.role === "user" ? "user" : "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));

      setMessages(uiMessages);

      // 아티팩트 목록 불러오기
      const artifactsResponse = await artifactApi.listArtifactsByTopic(topicId);

      // 아티팩트가 있으면 메시지에 연결
      if (artifactsResponse.artifacts.length > 0) {
        const messagesWithArtifacts = await Promise.all(
          uiMessages.map(async (msg) => {
            // 이 메시지와 연결된 아티팩트 찾기 (가장 최근 MD 파일)
            const relatedArtifact = artifactsResponse.artifacts.find(
              (art) => art.kind === "md"
            );

            if (relatedArtifact && msg.type === "assistant") {
              try {
                const contentResponse = await artifactApi.getArtifactContent(
                  relatedArtifact.id
                );
                return {
                  ...msg,
                  reportData: {
                    filename: relatedArtifact.filename,
                    reportId: relatedArtifact.id,
                    content: contentResponse.content,
                  },
                };
              } catch (error) {
                console.error("Failed to load artifact content:", error);
                return msg;
              }
            }

            return msg;
          })
        );

        setMessages(messagesWithArtifacts);
      }
    } catch (error: any) {
      console.error("Error loading topic messages:", error);
      antdMessage.error(error.message || "토픽 메시지를 불러오는데 실패했습니다.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleNewTopic = () => {
    setSelectedTopicId(null);
    setMessages([]);
  };

  const handleToggleSidebar = () => {
    setIsLeftSidebarOpen(!isLeftSidebarOpen);
  };

  return (
    <MainLayout sidebarCollapsed={!isLeftSidebarOpen}>
      <Sidebar
        isOpen={isLeftSidebarOpen}
        onToggle={handleToggleSidebar}
        selectedTopicId={selectedTopicId}
        onTopicSelect={handleTopicSelect}
        onNewTopic={handleNewTopic}
      />

      <div className={`${styles.mainChatPage} ${isLeftSidebarOpen ? styles.sidebarExpanded : styles.sidebarCollapsed}`}>
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
