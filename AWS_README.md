# AWS Infrastructure Setup for Staycomfy

This directory contains all the necessary files and documentation to deploy the Staycomfy hotel booking website to AWS infrastructure.

## 📋 Overview

The AWS infrastructure consists of:
- **DynamoDB**: NoSQL database for hotels, rooms, bookings, and users
- **IAM**: Secure identity management for backend access
- **EC2**: Backend Django application server
- **Security Groups**: Network security for EC2
- **S3**: Static website hosting for frontend
- **CloudWatch**: Monitoring and logging for EC2

## 🚀 Quick Start

### 1. Prerequisites
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Project codebase ready for deployment

### 2. Setup Steps
1. **Read the comprehensive guide**: `AWS_SETUP_GUIDE.md`
2. **Configure IAM**: Use `aws-iam-policy.json` as reference
3. **Create DynamoDB tables**: Use `dynamodb-schema.json` as reference
4. **Setup S3 bucket**: Use `s3-bucket-policy.json` and `s3-cors-config.xml`
5. **Deploy to EC2**: Run `deploy_ec2.sh`
6. **Deploy static files**: Run `deploy_s3.sh`
7. **Setup monitoring**: Run `setup_cloudwatch.sh`

### 3. Complete Deployment
For a complete deployment, run:
```bash
./deploy_all.sh
```

## 📁 Configuration Files

### AWS Configuration
- `aws-iam-policy.json` - IAM policy for backend access
- `dynamodb-schema.json` - DynamoDB table definitions
- `s3-bucket-policy.json` - S3 bucket policy for static website
- `s3-cors-config.xml` - CORS configuration for S3
- `security-groups-config.json` - Security group rules
- `cloudwatch-agent-config.json` - CloudWatch agent configuration

### Deployment Scripts
- `deploy_ec2.sh` - Deploy backend to EC2 instance
- `deploy_s3.sh` - Deploy static files to S3
- `setup_cloudwatch.sh` - Setup CloudWatch monitoring
- `deploy_all.sh` - Complete deployment orchestration

### Application Configuration
- `config/dynamodb_utils.py` - DynamoDB utility functions
- `hotels/dynamodb_models.py` - DynamoDB models for hotels
- `bookings/dynamodb_models.py` - DynamoDB models for bookings
- `accounts/dynamodb_models.py` - DynamoDB models for users
- `staycomfy.service` - Systemd service configuration

### Documentation
- `AWS_SETUP_GUIDE.md` - Comprehensive AWS setup guide
- `DEPLOYMENT_CHECKLIST.md` - Deployment checklist and troubleshooting
- `AWS_README.md` - This file

## 🔧 Configuration Updates

### Environment Variables
Update your `.env` file with AWS configuration:

```env
USE_DYNAMODB=true
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-south-1
```

### Dependencies
Updated `requirements.txt` to include:
- `boto3>=1.28.0` - AWS SDK for Python
- `gunicorn>=21.0.0` - Production WSGI server
- `watchtower>=3.0.0` - CloudWatch logging

### Django Settings
Updated `config/settings.py` to support DynamoDB configuration via environment variables.

## 📊 Architecture

```
┌─────────────┐
│   S3 Bucket │  (Static Website)
│  (Frontend) │
└──────┬──────┘
       │
       │ HTTP/HTTPS
       │
┌──────▼──────┐
│   EC2 Instance │  (Backend)
│  (Django + Gunicorn) │
└──────┬──────┘
       │
       │ boto3
       │
┌──────▼──────┐
│  DynamoDB   │  (Database)
│  (Tables)   │
└─────────────┘

┌─────────────┐
│ CloudWatch │  (Monitoring)
│  (Logs + Alarms) │
└─────────────┘
```

## 🔒 Security

- IAM user with least privilege access
- Security groups with minimal required ports
- Environment variables for sensitive data
- No hardcoded credentials in code
- SSL/TLS recommended for production

## 💰 Cost Estimate

Based on typical usage:
- **EC2 (t3.medium)**: ~$25/month
- **DynamoDB**: ~$15-50/month (depending on usage)
- **S3**: ~$1-5/month (depending on storage)
- **CloudWatch**: ~$5-10/month (depending on metrics)
- **Data Transfer**: ~$10-20/month
- **Total Estimate**: ~$56-110/month

## 🚨 Monitoring

CloudWatch alarms are configured for:
- CPU utilization > 80%
- Memory utilization > 85%
- Disk utilization > 80%
- Application error rate

Logs are collected for:
- Application logs
- Error logs
- Nginx logs (if configured)

## 🛠️ Maintenance

### Daily
- Check CloudWatch alarms
- Review application logs
- Monitor system metrics

### Weekly
- Review AWS costs
- Check for security updates
- Test backup restoration

### Monthly
- Rotate IAM credentials
- Review and update IAM policies
- Performance tuning based on metrics

## 📞 Support

For issues or questions:
1. Check `AWS_SETUP_GUIDE.md` for detailed instructions
2. Review `DEPLOYMENT_CHECKLIST.md` for troubleshooting
3. Consult AWS documentation: https://docs.aws.amazon.com/

## 🔄 Rollback

If deployment fails or issues occur:
1. Check logs in `/var/log/staycomfy/`
2. Review CloudWatch metrics
3. Use previous EC2 AMI if needed
4. Restore DynamoDB from backup if required

## 📝 Notes

- This setup assumes the ap-south-1 (Mumbai) region. Update as needed.
- DynamoDB is used instead of MySQL for this AWS deployment.
- The application can be switched back to MySQL by changing `USE_DYNAMODB=false` in `.env`.
- Static files are served from S3 for better performance and cost optimization.
- Consider using a load balancer for production deployments.

## ✅ Pre-Deployment Checklist

Before deploying, ensure:
- [ ] AWS account is active and billing is configured
- [ ] IAM user with appropriate permissions is created
- [ ] DynamoDB tables are created and active
- [ ] S3 bucket is created and configured
- [ ] EC2 instance is launched and configured
- [ ] Security groups are properly configured
- [ ] `.env` file is updated with production values
- [ ] All deployment scripts are executable
- [ ] Application is tested locally

---

Generated for Staycomfy Hotel Booking Website
Date: 2026-08-14