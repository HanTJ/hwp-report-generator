import React, {useState, useEffect} from 'react'
import {Modal, Input, message} from 'antd'
import {useTopicStore} from '../../stores/useTopicStore'
import type {Topic} from '../../types/topic'
import styles from './TopicEditModal.module.css'

interface TopicEditModalProps {
    topic: Topic | null
    isOpen: boolean
    onClose: () => void
    onSuccess?: () => void
}

const TopicEditModal: React.FC<TopicEditModalProps> = ({topic, isOpen, onClose, onSuccess}) => {
    const [editTitle, setEditTitle] = useState('')
    const [isSaving, setIsSaving] = useState(false)
    const {updateTopicById} = useTopicStore()

    // topic이 변경될 때마다 editTitle 업데이트
    useEffect(() => {
        if (topic) {
            setEditTitle(topic.generated_title || topic.input_prompt)
        }
    }, [topic])

    const handleSave = async () => {
        if (!topic) return

        const trimmedTitle = editTitle.trim()
        if (!trimmedTitle) {
            message.error('제목을 입력해주세요.')
            return
        }

        if (trimmedTitle === (topic.generated_title || topic.input_prompt)) {
            message.info('변경사항이 없습니다.')
            onClose()
            return
        }

        setIsSaving(true)
        try {
            await updateTopicById(topic.id, {
                generated_title: trimmedTitle
            })

            message.success('제목이 수정되었습니다.')
            onClose()
            onSuccess?.()
        } catch (error: any) {
            console.error('TopicEditModal > failed >', error)
            message.error(error.message || '제목 수정에 실패했습니다.')
        } finally {
            setIsSaving(false)
        }
    }

    const handleCancel = () => {
        onClose()
    }

    return (
        <Modal
            title="제목 수정"
            open={isOpen}
            onOk={handleSave}
            onCancel={handleCancel}
            okText="저장"
            cancelText="취소"
            confirmLoading={isSaving}
            centered
            className={styles.modal}>
            <div className={styles.content}>
                <Input
                    id="edit-title"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    placeholder="제목을 입력하세요."
                    maxLength={200}
                    showCount
                    onPressEnter={handleSave}
                    autoFocus
                    className={styles.input}
                />
            </div>
        </Modal>
    )
}

export default TopicEditModal
