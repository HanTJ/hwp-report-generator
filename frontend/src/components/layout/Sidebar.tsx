import React, { useEffect } from "react";
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
import { useTopicStore } from "../../stores/useTopicStore";
import { UI_CONFIG } from "../../constants";
import styles from "./Sidebar.module.css";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onTopicSelect: (topicId: number) => void;
  onNewTopic: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  onTopicSelect,
  onNewTopic,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Use Zustand store for topic management - Sidebar용 상태만 사용
  const { sidebarTopics, sidebarLoading, selectedTopicId, loadSidebarTopics } =
    useTopicStore();

  // 초기 로드 - Sidebar용 토픽 로드 (항상 첫 페이지)
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        await loadSidebarTopics();
      } catch (error: any) {
        message.error("토픽 목록을 불러오는데 실패했습니다.");
        console.error("Failed to load topics:", error);
      }
    };

    fetchTopics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // loadSidebarTopics is a stable reference from Zustand store

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

  const handleLogoClick = () => {
    navigate("/chat");
  };

  const handleAdminClick = () => {
    navigate("/admin");
  };

  const handleLogout = async () => {
    try {
      await logout();
      message.success("로그아웃되었습니다.");
      navigate("/login");
    } catch (error) {
      console.error("Logout error:", error);
      message.error("로그아웃 중 오류가 발생했습니다.");
    }
  };

  return (
    <nav
      className={`${styles.sidebar} ${isOpen ? styles.open : styles.collapsed}`}
    >
      {/* Collapsed State (닫힌 상태) */}
      {!isOpen && (
        <>
          <div className={styles.collapsedSidebarHeader}>
            <button
              className={styles.iconBtn}
              onClick={onToggle}
              title="사이드바 열기"
            >
              <RightOutlined />
            </button>
          </div>
          <div className={styles.collapsedContent}>
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
          {/* 사이드바 접기, 로고 */}
          <div className={styles.sidebarHeader}>
            <button
              className={styles.iconBtn}
              onClick={onToggle}
              title="사이드바 닫기"
            >
              <LeftOutlined />
            </button>
            <div>
              <h3 className={styles.title}>HWP 보고서 자동 생성 시스템</h3>
            </div>
          </div>
          <div className={styles.sidebarContent}>
            {/* + 버튼 새로운 주제 */}
            <button
              className={styles.newTopicBtn}
              onClick={onNewTopic}
              title="새로운 주제"
            >
              <div className={styles.plusIcon}>
                <div className={styles.plusCircle}>
                  <PlusOutlined />
                </div>
              </div>
              <span>새로운 주제</span>
            </button>

            {/* 최근 항목 */}
            <div className={styles.recentLabel}>최근 항목</div>

            {/* 토픽 리스트 */}
            <div className={styles.topicList}>
              {sidebarLoading ? (
                <div className={styles.loadingState}>
                  <div className={styles.loadingSpinner} />
                  <span>불러오는 중...</span>
                </div>
              ) : sidebarTopics.length === 0 ? (
                <div className={styles.emptyState}>
                  <MessageOutlined />
                  <p>아직 대화가 없습니다</p>
                  <p className={styles.emptyHint}>새 대화를 시작해보세요</p>
                </div>
              ) : (
                sidebarTopics.map((topic) => (
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

            {/* 모든 대화 버튼 - Sidebar에 로드된 토픽보다 더 많은 토픽이 있을 때 표시 */}
            {sidebarTopics.length >=
              UI_CONFIG.PAGINATION.SIDEBAR_TOPICS_PER_PAGE && (
              <button
                className={styles.moreBtn}
                onClick={() => navigate("/topics")}
              >
                <MoreOutlined />
                <span>모든 대화</span>
              </button>
            )}
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
