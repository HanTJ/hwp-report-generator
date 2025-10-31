import React, { useState } from 'react';
import { Form, Input, Button, Card, Table, message, Space } from 'antd';
import { DownloadOutlined, ReloadOutlined, FileTextOutlined, PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

const { TextArea } = Input;
import type { ColumnsType } from 'antd/es/table';
import MainLayout from '../components/layout/MainLayout';
import { useReports } from '../hooks/useReports';
import type { Report } from '../types/report';
import { formatFileSize, formatDate } from '../utils/formatters';
import { API_BASE_URL } from '../constants/';
import styles from './MainBakPage.module.css';

const MainBakPage: React.FC = () => {
  const [form] = Form.useForm();
  const { reports, isLoading, refetch, generateReport, isGenerating } = useReports();
  const [generatedFilename, setGeneratedFilename] = useState<string | null>(null);

  const onFinish = async (values: { topic: string; requiredContent: string; referenceUrls?: string[] }) => {
    try {
      // 백엔드 API는 topic만 받으므로, topic에 필수 내용과 참조 웹사이트를 합쳐서 전송
      let combinedTopic = values.topic;

      if (values.requiredContent) {
        combinedTopic += `\n\n[필수 포함 내용]\n${values.requiredContent}`;
      }

      if (values.referenceUrls && values.referenceUrls.length > 0) {
        const validUrls = values.referenceUrls.filter(url => url && url.trim());
        if (validUrls.length > 0) {
          combinedTopic += `\n\n[참조 웹사이트]\n${validUrls.map((url, index) => `${index + 1}. ${url}`).join('\n')}`;
        }
      }

      const response = await generateReport({ topic: combinedTopic });
      message.success(response.message);
      setGeneratedFilename(response.filename || null);
      form.resetFields();
      refetch();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '보고서 생성에 실패했습니다.');
    }
  };

  const handleDownload = (filename: string) => {
    window.open(`${API_BASE_URL}/api/download/${filename}`, '_blank');
  };

  const columns: ColumnsType<Report> = [
    {
      title: '파일명',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string) => (
        <Space>
          <FileTextOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: '파일 크기',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '생성 시간',
      dataIndex: 'created',
      key: 'created',
      render: (created: number) => formatDate(created),
    },
    {
      title: '다운로드',
      key: 'action',
      render: (_, record) => (
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={() => handleDownload(record.filename)}
        >
          다운로드
        </Button>
      ),
    },
  ];

  return (
    <MainLayout>
      <Space direction="vertical" size="large" className={styles.container}>
        <Card title="보고서 생성" bordered={false}>
          <Form
            form={form}
            name="reportForm"
            onFinish={onFinish}
            layout="vertical"
          >
            <Form.Item
              label="보고서 주제"
              name="topic"
              rules={[
                { required: true, message: '보고서 주제를 입력해주세요!' },
                { min: 3, message: '최소 3자 이상 입력해주세요!' }
              ]}
            >
              <Input
                placeholder="예: 2025년 디지털 뱅킹 서비스 현황 분석"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="필수 내용"
              name="requiredContent"
              tooltip="보고서에 반드시 포함되어야 할 내용을 입력하세요 (선택사항)"
            >
              <TextArea
                rows={4}
                placeholder="예:
- 2024년 대비 성장률 분석
- 주요 경쟁사 비교 (A사, B사)
- 향후 3년간 예상 시장 규모"
                maxLength={1000}
                showCount
              />
            </Form.Item>

            <Form.Item
              label="참조 웹사이트"
              tooltip="보고서 생성 시 참조할 웹사이트 주소를 입력하세요 (선택사항)"
            >
              <Form.List name="referenceUrls">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <div key={key} className={styles.urlInputContainer}>
                        <Form.Item
                          {...restField}
                          name={name}
                          rules={[
                            {
                              type: 'url',
                              message: '올바른 URL 형식이 아닙니다 (http:// 또는 https://로 시작해야 합니다)',
                            },
                          ]}
                          className={styles.urlInputWrapper}
                        >
                          <Input
                            placeholder="예: https://www.example.com"
                          />
                        </Form.Item>
                        <MinusCircleOutlined
                          onClick={() => remove(name)}
                          className={styles.removeIcon}
                        />
                      </div>
                    ))}
                    <Form.Item className={styles.addUrlButton}>
                      <Button
                        type="dashed"
                        onClick={() => add()}
                        block
                        icon={<PlusOutlined />}
                      >
                        웹사이트 추가
                      </Button>
                    </Form.Item>
                  </>
                )}
              </Form.List>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={isGenerating}
                size="large"
                block
              >
                {isGenerating ? '생성 중...' : '보고서 생성'}
              </Button>
            </Form.Item>
          </Form>

          {generatedFilename && (
            <div className={styles.successMessage}>
              <p className={styles.successText}>
                ✓ 보고서가 생성되었습니다: <strong>{generatedFilename}</strong>
              </p>
            </div>
          )}
        </Card>

        <Card
          title="생성된 보고서 목록"
          bordered={false}
          extra={
            <Button
              icon={<ReloadOutlined />}
              onClick={() => refetch()}
              loading={isLoading}
            >
              새로고침
            </Button>
          }
        >
          <Table
            columns={columns}
            dataSource={reports}
            rowKey="filename"
            loading={isLoading}
            pagination={{
              pageSize: 10,
              showSizeChanger: false,
              showTotal: (total) => `총 ${total}개`,
            }}
          />
        </Card>
      </Space>
    </MainLayout>
  );
};

export default MainBakPage;
