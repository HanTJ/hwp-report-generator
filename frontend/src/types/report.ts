export interface ReportRequest {
    topic: string
}

export interface ReportResponse {
    success: boolean
    message: string
    file_path?: string
    filename?: string
}

export interface Report {
    filename: string
    size: number
    created: number
}

export interface ReportListResponse {
    reports: Report[]
}
