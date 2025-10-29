import React from 'react';
import { CloseOutlined, DownloadOutlined } from '@ant-design/icons';
import styles from './ReportPreview.module.css';

interface ReportPreviewProps {
  report: {
    filename: string;
    content: string;
    reportId: number;
  };
  onClose: () => void;
  onDownload: () => void;
}

const ReportPreview: React.FC<ReportPreviewProps> = ({
  report,
  onClose,
  onDownload,
}) => {
  return (
    <div className={styles.reportPreviewSidebar}>
      <div className={styles.previewHeader}>
        <div className={styles.previewTitle}>
          <span>보고서 미리보기</span>
        </div>
        <div className={styles.previewActions}>
          <button
            className={`${styles.previewActionBtn} ${styles.download}`}
            onClick={onDownload}
            title="다운로드"
          >
            <DownloadOutlined />
          </button>
          <button
            className={`${styles.previewActionBtn} ${styles.close}`}
            onClick={onClose}
            title="닫기"
          >
            <CloseOutlined />
          </button>
        </div>
      </div>

      <div className={styles.previewContent}>
        <div className={styles.previewFilename}>{report.filename}</div>
        <div className={styles.previewText}>
          {report.content.split('\n').map((line, index) => (
            <React.Fragment key={index}>
              {line}
              {index < report.content.split('\n').length - 1 && <br />}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className={styles.previewFooter}>
        <button className={styles.previewDownloadBtn} onClick={onDownload}>
          <DownloadOutlined />
          <span>다운로드</span>
        </button>
      </div>
    </div>
  );
};

export default ReportPreview;
