import React, { useState, useRef, useEffect } from "react";
import { message as antdMessage } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import ChatMessage from "../components/chat/ChatMessage";
import ChatInput from "../components/chat/ChatInput";
import ReportPreview from "../components/report/ReportPreview";
import ReportsDropdown from "../components/chat/ReportsDropdown";
import Sidebar from "../components/layout/Sidebar";
import styles from "./MainPage.module.css";
import MainLayout from "../components/layout/MainLayout";
import { topicApi } from "../services/topicApi";
import { messageApi } from "../services/messageApi";
import { artifactApi } from "../services/artifactApi";
import { useTopicStore } from "../stores/useTopicStore";
import { useArtifactStore } from "../stores/useArtifactStore";

interface Message {
  id: string;
  messageId: number; // 백엔드 메시지 ID
  type: "user" | "assistant";
  content: string;
  reportData?: {
    filename: string;
    reportId: number;
    messageId: number;
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

const MainPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedReport, setSelectedReport] = useState<{
    filename: string;
    content: string;
    messageId: number;
    reportId: number;
  } | null>(null);
  const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(false);
  const [isReportsDropdownOpen, setIsReportsDropdownOpen] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const lastUserMessageRef = useRef<HTMLDivElement>(null);
  const reportsDropdownRef = useRef<HTMLDivElement>(null);

  // Zustand store for topic management
  const { selectedTopicId, setSelectedTopicId, addTopic } = useTopicStore();

  // Zustand store for artifact management
  const {
    loadArtifacts,
    invalidateCache,
    artifactsByTopic,
    loadingTopics,
    selectArtifact,
    getSelectedArtifactId,
    autoSelectLatest,
  } = useArtifactStore();

  // Close reports dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        reportsDropdownRef.current &&
        !reportsDropdownRef.current.contains(event.target as Node)
      ) {
        setIsReportsDropdownOpen(false);
      }
    };

    if (isReportsDropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isReportsDropdownOpen]);

  // 선택된 토픽이 변경되면 해당 토픽의 메시지 로드
  useEffect(() => {
    const loadTopicMessages = async () => {
      if (selectedTopicId) {
        setIsLoadingMessages(true);
        try {
          // 메시지 목록 조회
          const messagesResponse = await messageApi.listMessages(
            selectedTopicId
          );

          // 기본 메시지 배열 생성
          const uiMessages: Message[] = messagesResponse.messages.map(
            (msg) => ({
              id: msg.id.toString(),
              messageId: msg.id,
              type: msg.role === "user" ? "user" : "assistant",
              content: msg.content,
              timestamp: new Date(msg.created_at),
            })
          );

          // 아티팩트 목록 불러오기
          try {
            const artifactsResponse = await artifactApi.listArtifactsByTopic(
              selectedTopicId
            );

            // 아티팩트가 있으면 메시지에 연결
            if (artifactsResponse.artifacts.length > 0) {
              // assistant 메시지만 필터링하여 artifact 내용 로드
              const assistantMessages = uiMessages.filter(
                (msg) => msg.type === "assistant"
              );

              // artifact 내용을 병렬로 로드 (assistant 메시지만)
              const artifactContents = await Promise.all(
                assistantMessages.map(async (msg) => {
                  const relatedArtifact = artifactsResponse.artifacts.find(
                    (art) =>
                      art.kind === "md" && art.message_id === msg.messageId
                  );

                  if (relatedArtifact) {
                    try {
                      const contentResponse =
                        await artifactApi.getArtifactContent(
                          relatedArtifact.id
                        );
                      return {
                        messageId: msg.messageId,
                        reportData: {
                          filename: relatedArtifact.filename,
                          reportId: relatedArtifact.id,
                          messageId: msg.messageId,
                          content: contentResponse.content,
                        },
                      };
                    } catch (error) {
                      console.error("Failed to load artifact content:", error);
                      return null;
                    }
                  }

                  return null;
                })
              );

              // artifact 내용을 메시지에 매핑
              const artifactMap = new Map(
                artifactContents
                  .filter((item) => item !== null)
                  .map((item) => [item!.messageId, item!.reportData])
              );

              const messagesWithArtifacts = uiMessages.map((msg) => {
                const reportData = artifactMap.get(msg.messageId);
                return reportData ? { ...msg, reportData } : msg;
              });

              // 아티팩트 연결 후 한 번만 업데이트
              setMessages(messagesWithArtifacts);
            } else {
              // 아티팩트가 없으면 기본 메시지만 업데이트
              setMessages(uiMessages);
            }
          } catch (error) {
            console.error("Failed to load artifacts:", error);
            // 아티팩트 로드 실패 시에도 메시지는 표시
            setMessages(uiMessages);
          }
        } catch (error: any) {
          console.error("Failed to load messages:", error);
          antdMessage.error("메시지를 불러오는데 실패했습니다.");
        } finally {
          setIsLoadingMessages(false);
        }
      } else {
        // selectedTopicId가 null이면 메시지 초기화
        setMessages([]);
        setIsLoadingMessages(false);
      }
    };

    loadTopicMessages();
  }, [selectedTopicId]);

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

  const handleReportsClick = async () => {
    if (!selectedTopicId) {
      antdMessage.info("새로운 주제를 먼저 입력하세요.");
      return;
    }

    setIsReportsDropdownOpen(true);

    try {
      const artifacts = await loadArtifacts(selectedTopicId);

      // 아직 선택된 아티팩트가 없으면 자동으로 마지막 선택
      if (!getSelectedArtifactId(selectedTopicId) && artifacts.length > 0) {
        autoSelectLatest(selectedTopicId, artifacts);
      }
    } catch (error: any) {
      antdMessage.error("보고서 목록을 불러오는데 실패했습니다.");
      console.error("Failed to load artifacts:", error);
    }
  };

  const handleArtifactSelect = (artifactId: number) => {
    if (selectedTopicId) {
      selectArtifact(selectedTopicId, artifactId);
    }
  };

  /*
   * artifact 목록에서 다운로드 핸들러
   */
  const handleArtifactDownload = async (artifact: any) => {
    try {
      antdMessage.loading({
        content: "HWPX 파일 다운로드 중...",
        key: "download",
        duration: 0,
      });

      // message_id가 있으면 메시지 기반 HWPX 다운로드 사용
      if (artifact.message_id) {
        const hwpxFilename = artifact.filename.replace(".md", ".hwpx");
        await artifactApi.downloadMessageHwpx(
          artifact.message_id,
          hwpxFilename
        );
      } else {
        antdMessage.error("HWPX 파일 다운로드에 실패했습니다.");
        return;
      }
      antdMessage.destroy("download");
      antdMessage.success("HWPX 파일이 다운로드되었습니다.");
    } catch (error: any) {
      antdMessage.error("HWPX 파일 다운로드에 실패했습니다.");
    }
  };

  // 보고서 미리보기
  const handleArtifactPreview = async (artifact: any) => {
    try {
      const contentResponse = await artifactApi.getArtifactContent(artifact.id);
      setSelectedReport({
        filename: artifact.filename,
        content: contentResponse.content,
        messageId: artifact.message_id,
        reportId: artifact.id,
      });
      setIsReportsDropdownOpen(false);
    } catch (error: any) {
      antdMessage.error("미리보기를 불러오는데 실패했습니다.");
      console.error("Failed to preview artifact:", error);
    }
  };

  /*
   * 메시지 전송 핸들러
   */
  const handleSendMessage = async (
    message: string,
    files: File[],
    webSearchEnabled: boolean
  ) => {
    // 사용자 메시지 임시 추가
    const tempUserMessage: Message = {
      id: "temp-" + Date.now(),
      messageId: 0, // 임시 ID, 서버 응답 후 실제 ID로 교체
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    // 새 대화인 경우 이전 메시지를 무시하고 새로 시작
    if (selectedTopicId === null) {
      setMessages([tempUserMessage]);
    } else {
      setMessages((prev) => [...prev, tempUserMessage]);
    }
    setIsGenerating(true);

    try {
      let currentTopicId = selectedTopicId;

      // 첫 메시지: 토픽 생성 + AI 보고서 자동 생성
      if (currentTopicId === null) {
        const generateResponse = await topicApi.generateTopic({
          input_prompt: message,
          language: "ko",
        });
        currentTopicId = generateResponse.topic_id;
        // Note: setSelectedTopicId는 메시지 로드 완료 후에 호출 (중복 로드 방지)

        // Fetch the complete topic data and add to store
        try {
          const newTopic = await topicApi.getTopic(currentTopicId);
          addTopic(newTopic);
        } catch (error) {
          console.error("Failed to fetch topic after creation:", error);
        }
      } else {
        // 2번째 메시지부터: 메시지 체이닝 (ask API)
        let selectedArtifactId = getSelectedArtifactId(currentTopicId);

        // 선택된 아티팩트가 없으면 자동으로 최신 선택
        if (!selectedArtifactId) {
          const artifacts = await loadArtifacts(currentTopicId);
          if (artifacts.length > 0) {
            autoSelectLatest(currentTopicId, artifacts);
            selectedArtifactId = getSelectedArtifactId(currentTopicId);
          }
        }

        await topicApi.askTopic(currentTopicId, {
          content: message,
          artifact_id: selectedArtifactId, // 체크된 보고서 ID 전달
          include_artifact_content: true,
        });
      }

      // 메시지 목록 재조회 (AI 응답 포함)
      const messagesResponse = await messageApi.listMessages(currentTopicId);

      // UI 업데이트
      const uiMessages: Message[] = messagesResponse.messages.map((msg) => ({
        id: msg.id.toString(),
        messageId: msg.id,
        type: msg.role === "user" ? "user" : "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));

      // 메시지가 추가되었으므로 아티팩트 캐시 무효화
      invalidateCache(currentTopicId);

      // 아티팩트 목록 불러오기 (보고서가 생성되었는지 확인)
      try {
        const artifactsResponse = await artifactApi.listArtifactsByTopic(
          currentTopicId
        );

        // 아티팩트가 있으면 메시지에 연결
        if (artifactsResponse.artifacts.length > 0) {
          const messagesWithArtifacts = await Promise.all(
            uiMessages.map(async (msg) => {
              // 이 메시지와 연결된 아티팩트 찾기 (message_id 매칭)
              const relatedArtifact = artifactsResponse.artifacts.find(
                (art) => art.kind === "md" && art.message_id === msg.messageId
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
                      messageId: msg.messageId,
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
        } else {
          // 아티팩트가 없으면 기본 메시지만 표시
          setMessages(uiMessages);
        }
      } catch (error) {
        console.error("Failed to load artifacts:", error);
        // 아티팩트 로드 실패 시에도 메시지는 표시
        setMessages(uiMessages);
      }

      // 메시지 로드 완료 후 selectedTopicId 업데이트 (useEffect 중복 실행 방지)
      if (selectedTopicId !== currentTopicId) {
        setSelectedTopicId(currentTopicId);
      }
    } catch (error: any) {
      console.error("Error sending message:", error);
      antdMessage.error("메시지 전송에 실패했습니다.");

      // 에러 메시지 추가
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        messageId: 0, // 에러 메시지는 서버에 저장되지 않음
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
    messageId: number;
    reportId: number;
  }) => {
    setSelectedReport(reportData);
  };

  /*
   * 메시지 내 보고서 다운로드 핸들러
   */
  const handleDownload = async (reportData: {
    filename: string;
    content: string;
    reportId: number;
    messageId: number;
  }) => {
    try {
      // 메시지 기반 HWPX 다운로드 (자동 생성)
      antdMessage.loading({
        content: "HWPX 파일 다운로드 중...",
        key: "download",
        duration: 0,
      });

      const hwpxFilename = reportData.filename.replace(".md", ".hwpx");
      await artifactApi.downloadMessageHwpx(reportData.messageId, hwpxFilename);

      antdMessage.destroy("download");

      // 미사용 Add to downloaded files
      const downloadedFile: DownloadedFile = {
        id: reportData.messageId,
        filename: hwpxFilename,
        downloadUrl: `#`,
        size: "알 수 없음",
        timestamp: new Date(),
      };

      setDownloadedFiles((prev) => [...prev, downloadedFile]);
      antdMessage.success("HWPX 파일이 다운로드되었습니다.");
    } catch (error: any) {
      console.error("Download failed:", error);
      antdMessage.error("HWPX 파일 다운로드에 실패했습니다.");
    }
  };

  /*
   * 보고서 미리보기 닫기
   */
  const handleClosePreview = () => {
    setSelectedReport(null);
  };

  const handleTopicSelect = async (topicId: number) => {
    setSelectedTopicId(topicId);
    console.log("Selected topic ID:", topicId);
    setIsGenerating(false);

    try {
      // 선택된 토픽의 메시지 불러오기
      const messagesResponse = await messageApi.listMessages(topicId);

      // UI 메시지 형식으로 변환
      const uiMessages: Message[] = messagesResponse.messages.map((msg) => ({
        id: msg.id.toString(),
        messageId: msg.id,
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
            // 이 메시지와 연결된 아티팩트 찾기 (message_id 매칭)
            const relatedArtifact = artifactsResponse.artifacts.find(
              (art) => art.kind === "md" && art.message_id === msg.messageId
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
                    messageId: msg.messageId,
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
      antdMessage.error("메시지를 불러오는데 실패했습니다.");
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
      {/* Dim Overlay - 모바일/태블릿에서 사이드바 열렸을 때 */}
      {isLeftSidebarOpen && (
        <div className={styles.dimOverlay} onClick={handleToggleSidebar} />
      )}

      <Sidebar
        isOpen={isLeftSidebarOpen}
        onToggle={handleToggleSidebar}
        onTopicSelect={handleTopicSelect}
        onNewTopic={handleNewTopic}
      />

      <div
        className={`${styles.mainChatPage} ${
          isLeftSidebarOpen ? styles.sidebarExpanded : styles.sidebarCollapsed
        }`}
      >
        {/* 햄버거 메뉴 버튼 - 모바일/태블릿에서만 표시 */}
        <button
          className={styles.hamburgerBtn}
          onClick={handleToggleSidebar}
          aria-label="메뉴 열기"
        >
          <MenuOutlined />
        </button>
        <div className={styles.chatContainer}>
          <div className={styles.chatContent}>
            {isLoadingMessages ? (
              // 메시지 로딩 중일 때는 빈 화면 표시
              <div></div>
            ) : messages.length === 0 ? (
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
                <h1>보고서를 생성해보세요!</h1>
                <p>주제를 입력하면 AI가 자동으로 보고서를 작성합니다.</p>
              </div>
            ) : (
              <div className={styles.chatMessages}>
                {messages.map((message, index) => {
                  const isLastUserMessage =
                    message.type === "user" && index === messages.length - 1;

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
            <ChatInput
              onSend={handleSendMessage}
              disabled={isGenerating}
              onReportsClick={handleReportsClick}
              reportsDropdown={
                isReportsDropdownOpen && selectedTopicId ? (
                  <ReportsDropdown
                    ref={reportsDropdownRef}
                    artifacts={artifactsByTopic[selectedTopicId] || []}
                    loading={loadingTopics.has(selectedTopicId)}
                    selectedArtifactId={getSelectedArtifactId(selectedTopicId)}
                    onSelect={handleArtifactSelect}
                    onClose={() => setIsReportsDropdownOpen(false)}
                    onDownload={handleArtifactDownload}
                    onPreview={handleArtifactPreview}
                  />
                ) : null
              }
            />
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

export default MainPage;
