import React from 'react'
import {Modal} from 'antd'
import {ExclamationCircleOutlined} from '@ant-design/icons'
import styles from './DeleteChatMessageModal.module.css'

interface DeleteChatMessageModalProps {
    open: boolean
    onConfirm: () => void
    onCancel: () => void
    loading?: boolean
}

const DeleteChatMessageModal: React.FC<DeleteChatMessageModalProps> = ({open, onConfirm, onCancel, loading = false}) => {
    return (
        <Modal
            title={
                <div className={styles.modalTitle}>
                    <ExclamationCircleOutlined className={styles.titleIcon} />
                    <span>메시지 삭제</span>
                </div>
            }
            open={open}
            onOk={onConfirm}
            onCancel={onCancel}
            centered
            okText="삭제"
            cancelText="취소"
            okButtonProps={{
                danger: true,
                loading: loading
            }}
            cancelButtonProps={{
                disabled: loading
            }}
            closable={!loading}
            maskClosable={!loading}>
            <div className={styles.modalContent}>
                <p className={styles.warningText}>이 메시지를 삭제하시겠습니까?</p>
                <p className={styles.infoText}>연관된 보고서 파일도 함께 삭제됩니다. 이 작업은 되돌릴 수 없습니다.</p>
            </div>
        </Modal>
    )
}

export default DeleteChatMessageModal
