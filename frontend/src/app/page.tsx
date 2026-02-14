'use client';

import { useState } from 'react';
import { Layout, Menu, Card, Typography, Row, Col, Button, Input, Form, message, Modal } from 'antd';
import {
  ProjectOutlined,
  TeamOutlined,
  ApiOutlined,
  PlayCircleOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import axios from 'axios';

const { Header, Content, Sider } = Layout;
const { Title, Paragraph, Text } = Typography;

export default function Home() {
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [apiConfig, setApiConfig] = useState({
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4',
  });

  const handleCreateProject = async () => {
    if (!projectName) {
      message.warning('请输入项目名称');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/project/', {
        name: projectName,
        description: projectDesc,
        total_days: 30,
      });
      message.success(`项目创建成功: ${response.data.id}`);
    } catch (error) {
      message.error('创建项目失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = () => {
    if (!apiConfig.apiKey) {
      message.warning('请输入 API Key');
      return;
    }
    
    localStorage.setItem('twork_api_config', JSON.stringify(apiConfig));
    message.success('模型配置已保存');
    setConfigModalVisible(false);
  };

  const handleOpenConfig = () => {
    const savedConfig = localStorage.getItem('twork_api_config');
    if (savedConfig) {
      setApiConfig(JSON.parse(savedConfig));
    }
    setConfigModalVisible(true);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="light">
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <Title level={4}>TWork</Title>
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['1']}
          items={[
            { key: '1', icon: <ProjectOutlined />, label: '项目管理' },
            { key: '2', icon: <TeamOutlined />, label: 'Agent管理' },
            { key: '3', icon: <ApiOutlined />, label: '知识图谱' },
            { key: '4', icon: <PlayCircleOutlined />, label: '模拟运行' },
            { key: '5', icon: <SettingOutlined />, label: '模型配置', onClick: handleOpenConfig },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={4} style={{ margin: '16px 0' }}>
            项目管理多Agent模拟系统
          </Title>
          <Button icon={<SettingOutlined />} onClick={handleOpenConfig}>
            模型配置
          </Button>
        </Header>
        <Content style={{ margin: '24px', background: '#fff', padding: '24px', borderRadius: '8px' }}>
          <Row gutter={[24, 24]}>
            <Col span={24}>
              <Card title="创建新项目" bordered={false}>
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Text strong>项目名称</Text>
                    <Input
                      placeholder="请输入项目名称"
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                      style={{ marginTop: 8 }}
                    />
                  </Col>
                  <Col span={12}>
                    <Text strong>项目描述</Text>
                    <Input
                      placeholder="请输入项目描述"
                      value={projectDesc}
                      onChange={(e) => setProjectDesc(e.target.value)}
                      style={{ marginTop: 8 }}
                    />
                  </Col>
                  <Col span={24}>
                    <Button type="primary" onClick={handleCreateProject} loading={loading}>
                      创建项目
                    </Button>
                  </Col>
                </Row>
              </Card>
            </Col>
            <Col span={24}>
              <Card title="功能介绍" bordered={false}>
                <Row gutter={[16, 16]}>
                  <Col span={8}>
                    <Card hoverable>
                      <Title level={5}>📄 文档解析</Title>
                      <Paragraph>上传需求文档，自动提取任务、角色和依赖关系</Paragraph>
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card hoverable>
                      <Title level={5}>🤖 多Agent模拟</Title>
                      <Paragraph>多个AI Agent协作完成项目任务模拟</Paragraph>
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card hoverable>
                      <Title level={5}>📊 时间估算</Title>
                      <Paragraph>基于PERT三点估算的智能时间预测</Paragraph>
                    </Card>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        </Content>
      </Layout>

      <Modal
        title="模型配置"
        open={configModalVisible}
        onOk={handleSaveConfig}
        onCancel={() => setConfigModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form layout="vertical">
          <Form.Item label="API Key" required>
            <Input.Password
              placeholder="请输入 OpenAI API Key"
              value={apiConfig.apiKey}
              onChange={(e) => setApiConfig({ ...apiConfig, apiKey: e.target.value })}
            />
          </Form.Item>
          <Form.Item label="Base URL">
            <Input
              placeholder="https://api.openai.com/v1"
              value={apiConfig.baseUrl}
              onChange={(e) => setApiConfig({ ...apiConfig, baseUrl: e.target.value })}
            />
          </Form.Item>
          <Form.Item label="模型名称">
            <Input
              placeholder="gpt-4"
              value={apiConfig.model}
              onChange={(e) => setApiConfig({ ...apiConfig, model: e.target.value })}
            />
          </Form.Item>
          <Paragraph type="secondary" style={{ fontSize: '12px' }}>
            配置将保存在浏览器本地存储中，用于调用后端API时传递模型参数。
          </Paragraph>
        </Form>
      </Modal>
    </Layout>
  );
}