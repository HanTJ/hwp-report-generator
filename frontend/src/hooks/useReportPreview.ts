import {useState} from 'react'
import {message as antdMessage} from 'antd'
import {artifactApi} from '../services/artifactApi'

interface ReportData {
    filename: string
    content: string
    messageId: number
    reportId: number
}

interface DownloadedFile {
    id: number
    filename: string
    downloadUrl: string
    size: string
    timestamp: Date
}

/**
 * useReportPreview 커스텀 훅
 *
 * 보고서 미리보기 및 다운로드 상태 관리
 *
 * @returns 보고서 미리보기 관련 상태 및 핸들러
 */
export const useReportPreview = () => {
    const [selectedReport, setSelectedReport] = useState<ReportData | null>(null)
    const [downloadedFiles, setDownloadedFiles] = useState<DownloadedFile[]>([])

    /**
     * 보고서 클릭 - 미리보기 열기
     */
    const handleReportClick = (reportData: ReportData) => {
        setSelectedReport(reportData)
    }

    /**
     * 보고서 미리보기 닫기
     */
    const handleClosePreview = () => {
        setSelectedReport(null)
    }

    /**
     * 보고서 다운로드 핸들러
     */
    const handleDownload = async (reportData: ReportData) => {
        try {
            antdMessage.loading({
                content: 'HWPX 파일 다운로드 중...',
                key: 'download',
                duration: 0
            })

            const hwpxFilename = reportData.filename.replace('.md', '.hwpx')
            await artifactApi.downloadMessageHwpx(reportData.messageId, hwpxFilename)

            antdMessage.destroy('download')

            const downloadedFile: DownloadedFile = {
                id: reportData.messageId,
                filename: hwpxFilename,
                downloadUrl: `#`,
                size: '알 수 없음',
                timestamp: new Date()
            }

            setDownloadedFiles((prev) => [...prev, downloadedFile])
            antdMessage.success('HWPX 파일이 다운로드되었습니다.')
        } catch (error: any) {
            console.error('Download failed:', error)
            antdMessage.error('HWPX 파일 다운로드에 실패했습니다.')
        }
    }

    return {
        selectedReport,
        setSelectedReport,
        downloadedFiles,
        handleReportClick,
        handleClosePreview,
        handleDownload
    }
}
