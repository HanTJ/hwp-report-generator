import React, { useState, useEffect } from "react";
import {
  PlusOutlined,
  MessageOutlined,
  LeftOutlined,
  RightOutlined,
  MoreOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { message } from "antd";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { topicApi } from "../../services/topicApi";
import type { Topic } from "../../types/topic";
import styles from "./Sidebar.module.css";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  selectedTopicId: number | null;
  onTopicSelect: (topicId: number) => void;
  onNewTopic: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  selectedTopicId,
  onTopicSelect,
  onNewTopic,
}) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    setLoading(true);
    try {
      const response = await topicApi.listTopics("active", 1, 10);
      setTopics(response.topics);
    } catch (error: any) {
      message.error("토픽 목록을 불러오는데 실패했습니다.");
      console.error("Failed to load topics:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "방금 전";
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;

    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
    });
  };

  const handleAdminClick = () => {
    navigate("/admin");
  };

  const handleLogout = () => {
    logout();
    message.success("로그아웃되었습니다.");
    navigate("/login");
  };

  return (
    <nav
      className={`${styles.sidebar} ${isOpen ? styles.open : styles.collapsed}`}
    >
      {/* Collapsed State (닫힌 상태) */}
      {!isOpen && (
        <>
          <div className={styles.collapsedContent}>
            <button
              className={styles.iconBtn}
              onClick={onToggle}
              title="사이드바 열기"
            >
              <RightOutlined />
            </button>
            <button
              className={styles.iconBtn}
              onClick={onNewTopic}
              title="새로운 주제"
            >
              <div className={styles.plusCircle}>
                <PlusOutlined />
              </div>
            </button>
          </div>

          {/* Bottom Menu - Collapsed */}
          <div className={styles.bottomMenu}>
            {user?.is_admin && (
              <button
                className={styles.iconBtn}
                onClick={handleAdminClick}
                title="관리자 페이지"
              >
                <SettingOutlined />
              </button>
            )}
            <button
              className={styles.iconBtn}
              title={user?.username || "사용자"}
            >
              <UserOutlined />
            </button>
            <button
              className={styles.iconBtn}
              onClick={handleLogout}
              title="로그아웃"
            >
              <LogoutOutlined />
            </button>
          </div>
        </>
      )}

      {/* Expanded State (열린 상태) */}
      {isOpen && (
        <>
          {/* Row 1: 왼쪽 화살표, 로고 */}
          <div className={styles.sidebarHeader}>
            <button
              className={styles.iconBtn}
              onClick={onToggle}
              title="사이드바 닫기"
            >
              <LeftOutlined />
            </button>
            <div className={styles.logo}>
              <img src="/src/assets/logo.png" alt="Logo" />
            </div>
          </div>

          <div className={styles.sidebarContent}>
            {/* + 버튼 새로운 주제 */}
            <button
              className={styles.newTopicBtn}
              onClick={onNewTopic}
              title="새로운 주제"
            >
              <div className={styles.plusCircle}>
                <PlusOutlined />
              </div>
              <span>새로운 주제</span>
            </button>

            {/* Row 3: 최근 항목 */}
            <div className={styles.recentLabel}>최근 항목</div>

            {/* 토픽 리스트 */}
            <div className={styles.topicList}>
              {loading ? (
                <div className={styles.loadingState}>
                  <div className={styles.loadingSpinner} />
                  <span>불러오는 중...</span>
                </div>
              ) : topics.length === 0 ? (
                <div className={styles.emptyState}>
                  <MessageOutlined />
                  <p>아직 대화가 없습니다</p>
                  <p className={styles.emptyHint}>새 대화를 시작해보세요</p>
                </div>
              ) : (
                topics.map((topic) => (
                  <button
                    key={topic.id}
                    className={`${styles.topicItem} ${
                      selectedTopicId === topic.id ? styles.selected : ""
                    }`}
                    onClick={() => onTopicSelect(topic.id)}
                  >
                    <div className={styles.topicIcon}>
                      <MessageOutlined />
                    </div>
                    <div className={styles.topicInfo}>
                      <div className={styles.topicTitle}>
                        {topic.generated_title || topic.input_prompt}
                      </div>
                      <div className={styles.topicMeta}>
                        {formatDate(topic.updated_at)}
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>

            {/* 더보기 버튼 */}
            <button className={styles.moreBtn}>
              <MoreOutlined />
              <span>더보기</span>
            </button>
          </div>

          {/* Bottom Menu - Expanded */}
          <div className={styles.bottomMenuExpanded}>
            {user?.is_admin && (
              <button className={styles.menuItem} onClick={handleAdminClick}>
                <SettingOutlined />
                <span>관리자 페이지</span>
              </button>
            )}
            <button className={styles.menuItem}>
              <UserOutlined />
              <span>{user?.username || "사용자"}</span>
            </button>
            <button className={styles.menuItem} onClick={handleLogout}>
              <LogoutOutlined />
              <span>로그아웃</span>
            </button>
          </div>
        </>
      )}
    </nav>
  );
};

export default Sidebar;
