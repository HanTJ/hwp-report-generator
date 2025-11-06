import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import App from './App'

import './styles/variables.css' // CSS 변수 정의 (색상, 간격 등)
import './styles/global.css' // 전역 스타일
import './styles/common.css' // 공통 스타일
import 'antd/dist/reset.css' // Ant Design 기본 스타일 초기화

/**
 * main.tsx
 *
 * ⭐ 리액트 앱의 시작점 (진입점)
 *
 * 역할:
 * 1. HTML의 #root 요소를 찾아서
 * 2. 그 안에 리액트 앱(<App />)을 렌더링
 *
 * StrictMode: 개발 모드에서 잠재적 문제를 경고해주는 도구
 */

// HTML의 id="root" 요소에 리액트 앱을 렌더링
createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <App />
    </StrictMode>
)
