import React from 'react';
import { FileTextOutlined, DownloadOutlined } from '@ant-design/icons';
import styles from './DownloadedFiles.module.css';

interface DownloadedFile {
  id: number;
  filename: string;
  downloadUrl: string;
  size: string;
  timestamp: Date;
}

interface DownloadedFilesProps {
  files: DownloadedFile[];
}

const DownloadedFiles: React.FC<DownloadedFilesProps> = ({ files }) => {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}시간 전`;

    const days = Math.floor(hours / 24);
    return `${days}일 전`;
  };

  return (
    <div className={styles.downloadedFilesContainer}>
      <div className={styles.downloadedFilesHeader}>
        <DownloadOutlined />
        <span>다운로드한 파일</span>
        <span className={styles.fileCount}>{files.length}</span>
      </div>
      <div className={styles.downloadedFilesList}>
        {files.map((file) => (
          <div key={file.id} className={styles.downloadedFileItem}>
            <div className={styles.fileIcon}>
              <FileTextOutlined />
            </div>
            <div className={styles.fileDetails}>
              <div className={styles.fileName}>{file.filename}</div>
              <div className={styles.fileMeta}>
                <span>{file.size}</span>
                <span className={styles.separator}>•</span>
                <span>{formatTime(file.timestamp)}</span>
              </div>
            </div>
            <a
              href={file.downloadUrl}
              className={styles.fileDownloadLink}
              download={file.filename}
              title="다시 다운로드"
            >
              <DownloadOutlined />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DownloadedFiles;
