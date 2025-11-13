import { setupWorker } from 'msw/browser'
import { handlers, getMockedEndpoints } from './handlers'

export const worker = setupWorker(...handlers)

/**
 * 개발 환경에서 Mock API 목록을 콘솔에 출력
 * 사용법: 브라우저 콘솔에서 `window.listMockAPIs()` 실행
 */
if (import.meta.env.MODE === 'development') {
  // @ts-ignore
  window.listMockAPIs = () => {
    console.group('🔵 MSW Mock APIs')
    getMockedEndpoints().forEach(endpoint => {
      console.log(`  ${endpoint}`)
    })
    console.groupEnd()
    console.log('⚪ 기타 모든 API는 실제 Backend로 전달됩니다.')
  }
  
  // @ts-ignore
  window.mswWorker = worker
}
