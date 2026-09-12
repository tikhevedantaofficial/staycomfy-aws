#!/bin/bash

# CloudWatch Setup Script for Staycomfy EC2 Instance
# This script sets up CloudWatch monitoring and alarms

set -e

# Configuration
AWS_REGION="ap-south-1"
LOG_GROUP_PREFIX="/aws/ec2/staycomfy"
ALARM_SNS_TOPIC=""  # Optional: Add your SNS topic ARN for notifications

echo "🚀 Setting up CloudWatch monitoring for Staycomfy..."

# Create CloudWatch log groups
echo "📁 Creating CloudWatch log groups..."
aws logs create-log-group --log-group-name "${LOG_GROUP_PREFIX}/application" --region $AWS_REGION 2>/dev/null || echo "Log group already exists"
aws logs create-log-group --log-group-name "${LOG_GROUP_PREFIX}/error" --region $AWS_REGION 2>/dev/null || echo "Log group already exists"
aws logs create-log-group --log-group-name "${LOG_GROUP_PREFIX}/nginx" --region $AWS_REGION 2>/dev/null || echo "Log group already exists"

# Set retention policy to 30 days
echo "⏰ Setting log retention to 30 days..."
aws logs put-retention-policy --log-group-name "${LOG_GROUP_PREFIX}/application" --retention-in-days 30 --region $AWS_REGION
aws logs put-retention-policy --log-group-name "${LOG_GROUP_PREFIX}/error" --retention-in-days 30 --region $AWS_REGION
aws logs put-retention-policy --log-group-name "${LOG_GROUP_PREFIX}/nginx" --retention-in-days 30 --region $AWS_REGION

# Create CloudWatch Alarms
echo "🚨 Creating CloudWatch alarms..."

# CPU Utilization Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "staycomfy-cpu-high" \
    --alarm-description "Alert when CPU utilization exceeds 80% for 5 minutes" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --evaluation-periods 5 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=$(ec2-metadata -i | cut -d " " -f 2) \
    --region $AWS_REGION \
    --alarm-actions $ALARM_SNS_TOPIC 2>/dev/null || echo "CPU alarm creation failed (may need instance ID)"

# Memory Utilization Alarm (requires CloudWatch agent)
aws cloudwatch put-metric-alarm \
    --alarm-name "staycomfy-memory-high" \
    --alarm-description "Alert when memory utilization exceeds 85% for 5 minutes" \
    --metric-name mem_used_percent \
    --namespace Staycomfy \
    --statistic Average \
    --period 300 \
    --evaluation-periods 5 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --region $AWS_REGION \
    --alarm-actions $ALARM_SNS_TOPIC 2>/dev/null || echo "Memory alarm creation failed"

# Disk Space Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "staycomfy-disk-high" \
    --alarm-description "Alert when disk utilization exceeds 80% for 5 minutes" \
    --metric-name disk_used_percent \
    --namespace Staycomfy \
    --statistic Average \
    --period 300 \
    --evaluation-periods 5 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --region $AWS_REGION \
    --alarm-actions $ALARM_SNS_TOPIC 2>/dev/null || echo "Disk alarm creation failed"

# Application Error Rate Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "staycomfy-errors-high" \
    --alarm-description "Alert when application error rate is high" \
    --metric-name ErrorCount \
    --namespace Staycomfy \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 3 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --region $AWS_REGION \
    --alarm-actions $ALARM_SNS_TOPIC 2>/dev/null || echo "Error rate alarm creation failed"

echo "✅ CloudWatch setup completed successfully!"
echo "📊 You can view your metrics in the CloudWatch console: https://console.aws.amazon.com/cloudwatch/"
echo "🚨 Alarms will trigger notifications if configured with an SNS topic"