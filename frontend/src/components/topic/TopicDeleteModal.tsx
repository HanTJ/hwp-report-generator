import React from 'react'
import {Modal, message} from 'antd'
import {ExclamationCircleOutlined} from '@ant-design/icons'
import {useTopicStore} from '../../stores/useTopicStore'
import type {Topic} from '../../types/topic'
import styles from './TopicDeleteModal.module.css'

interface TopicDeleteModalProps {
    topic: Topic | null
    isOpen: boolean
    onClose: () => void
    onSuccess?: () => void
}

const TopicDeleteModal: React.FC<TopicDeleteModalProps> = ({topic, isOpen, onClose, onSuccess}) => {
    const {deleteTopicById} = useTopicStore()

    const handleDelete = async () => {
        if (!topic) return

        try {
            await deleteTopicById(topic.id)
            message.success('토픽이 삭제되었습니다.')
            onClose()
            onSuccess?.()
        } catch (error: any) {
            console.error('TopicDeleteModal > failed >', error)
            message.error(error.message || '토픽 삭제에 실패했습니다.')
        }
    }

    if (!topic) return null

    return (
        <Modal
            title={
                <div className={styles.title}>
                    <ExclamationCircleOutlined className={styles.warningIcon} />
                    <span>토픽 삭제</span>
                </div>
            }
            open={isOpen}
            onOk={handleDelete}
            onCancel={onClose}
            okText="삭제"
            cancelText="취소"
            okType="danger"
            centered
            className={styles.modal}>
            <div className={styles.content}>
                <p className={styles.message}>정말로 이 토픽을 삭제하시겠습니까?</p>
                <div className={styles.topicInfo}>
                    <strong>{topic.generated_title || topic.input_prompt}</strong>
                </div>
                <div className={styles.warning}>
                    <p>⚠️ 이 작업은 되돌릴 수 없습니다.</p>
                    <p>관련된 모든 메시지와 파일이 영구적으로 삭제됩니다.</p>
                </div>
            </div>
        </Modal>
    )
}

export default TopicDeleteModal
