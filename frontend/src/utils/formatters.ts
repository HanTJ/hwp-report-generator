/**
 * 바이트 크기를 사람이 읽기 쉬운 형식으로 변환합니다.
 *
 * @param bytes - 변환할 바이트 크기 (음수가 아닌 정수)
 * @returns 포맷된 파일 크기 문자열 (소수점 둘째 자리까지)
 *
 * @example
 * formatFileSize(0)          // '0 Bytes'
 * formatFileSize(1024)       // '1 KB'
 * formatFileSize(1536)       // '1.5 KB'
 * formatFileSize(1048576)    // '1 MB'
 * formatFileSize(5242880)    // '5 MB'
 * formatFileSize(1073741824) // '1 GB'
 */
export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Unix 타임스탬프를 한국어 형식의 날짜/시간 문자열로 변환합니다.
 *
 * @param timestamp - Unix 타임스탬프 (초 단위)
 * @returns 한국어 로케일 형식의 날짜/시간 문자열 (YYYY. MM. DD. HH:MM)
 *
 * @example
 * formatDate(1609459200)      // '2021. 01. 01. 오전 09:00' (KST 기준)
 * formatDate(1735689600)      // '2025. 01. 01. 오전 12:00' (KST 기준)
 * formatDate(1704067200)      // '2024. 01. 01. 오전 09:00' (KST 기준)
 *
 * @remarks
 * - 입력은 Unix 타임스탬프 (초 단위)이며, 밀리초로 변환하여 Date 객체 생성
 * - 출력 형식은 한국 표준시(KST) 기준
 * - 시간은 24시간 형식이 아닌 오전/오후 형식으로 표시됨
 */
export const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp * 1000)
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}
