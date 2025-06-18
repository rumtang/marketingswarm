import React from 'react';
import { Card, Typography, List, Timeline, Tag, Divider, Space, Button } from 'antd';
import { 
  FileTextOutlined, 
  CheckCircleOutlined, 
  WarningOutlined,
  ClockCircleOutlined,
  TeamOutlined,
  CalendarOutlined,
  PrinterOutlined 
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

const BriefingDocument = ({ briefing, onPrint }) => {
  if (!briefing) return null;

  return (
    <Card 
      title={
        <Space>
          <FileTextOutlined />
          <span>Strategic Marketing Brief</span>
        </Space>
      }
      extra={
        <Button 
          icon={<PrinterOutlined />} 
          onClick={onPrint}
          type="primary"
        >
          Export PDF
        </Button>
      }
      style={{ maxWidth: 800, margin: '20px auto' }}
      className="briefing-document"
    >
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Title level={3}>{briefing.title}</Title>
        <Space split={<Divider type="vertical" />}>
          <Text type="secondary">
            <CalendarOutlined /> {briefing.date}
          </Text>
          <Text type="secondary">
            <TeamOutlined /> {briefing.prepared_by}
          </Text>
        </Space>
      </div>

      <Divider />

      {/* Executive Summary */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>Executive Summary</Title>
        <Card type="inner" style={{ backgroundColor: '#f0f5ff' }}>
          <Paragraph>{briefing.executive_summary}</Paragraph>
        </Card>
      </div>

      {/* Situation Analysis */}
      {briefing.situation_analysis && briefing.situation_analysis.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <Title level={4}>Situation Analysis</Title>
          <List
            dataSource={briefing.situation_analysis}
            renderItem={(item, index) => (
              <List.Item>
                <Text>• {item}</Text>
              </List.Item>
            )}
          />
        </div>
      )}

      {/* Strategic Recommendations */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>Strategic Recommendations</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          {briefing.strategic_recommendations.map((rec, index) => (
            <Card 
              key={index} 
              size="small"
              title={
                <Space>
                  <Tag color="blue">{rec.category}</Tag>
                  <Text strong>Owner: {rec.owner}</Text>
                </Space>
              }
            >
              <Text>{rec.recommendation}</Text>
            </Card>
          ))}
        </Space>
      </div>

      {/* Implementation Timeline */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>Implementation Timeline</Title>
        <Timeline>
          {briefing.implementation_timeline.map((phase, index) => (
            <Timeline.Item 
              key={index}
              dot={<ClockCircleOutlined style={{ fontSize: '16px' }} />}
              color={index === 0 ? 'red' : index === 1 ? 'orange' : 'green'}
            >
              <Text strong>{phase.phase}</Text>
              <List
                size="small"
                dataSource={phase.actions}
                renderItem={action => (
                  <List.Item style={{ padding: '4px 0' }}>
                    <Text type="secondary">→ {action}</Text>
                  </List.Item>
                )}
              />
            </Timeline.Item>
          ))}
        </Timeline>
      </div>

      {/* Success Metrics */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>Success Metrics</Title>
        <Space wrap>
          {briefing.success_metrics.map((metric, index) => (
            <Tag 
              key={index} 
              icon={<CheckCircleOutlined />} 
              color="success"
              style={{ margin: '4px', padding: '4px 12px' }}
            >
              {metric}
            </Tag>
          ))}
        </Space>
      </div>

      {/* Risk Mitigation */}
      {briefing.risk_mitigation && briefing.risk_mitigation.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <Title level={4}>
            <WarningOutlined /> Risk Considerations
          </Title>
          <List
            dataSource={briefing.risk_mitigation}
            renderItem={risk => (
              <List.Item>
                <Text type="warning">⚠ {risk}</Text>
              </List.Item>
            )}
          />
        </div>
      )}

      {/* Next Steps */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>Next Steps</Title>
        <List
          dataSource={briefing.next_steps}
          renderItem={(step, index) => (
            <List.Item>
              <Space>
                <Tag>{index + 1}</Tag>
                <Text>{step}</Text>
              </Space>
            </List.Item>
          )}
        />
      </div>

      {/* Approval */}
      <Divider />
      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Text type="secondary">Approval needed from: </Text>
        <Text strong>{briefing.approval_needed_from}</Text>
      </div>
    </Card>
  );
};

export default BriefingDocument;