/**
 * useMessageStore.ts
 *
 * 메시지 관련 UI 상태 관리 (전역)
 */

import {create} from 'zustand'

interface MessageStore {
    // State - 메시지 생성/삭제 상태
    isGeneratingMessage: boolean
    isDeletingMessage: boolean

    // Actions
    setIsGeneratingMessage: (generating: boolean) => void
    setIsDeletingMessage: (deleting: boolean) => void
}

export const useMessageStore = create<MessageStore>((set) => ({
    // 초기 상태
    isGeneratingMessage: false,
    isDeletingMessage: false,

    // Actions
    setIsGeneratingMessage: (generating) => set({isGeneratingMessage: generating}),
    setIsDeletingMessage: (deleting) => set({isDeletingMessage: deleting})
}))
