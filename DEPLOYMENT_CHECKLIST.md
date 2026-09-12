# AWS Deployment Checklist for Staycomfy

## Pre-Deployment Checklist

### AWS Account Setup
- [ ] AWS account is active and billing is configured
- [ ] AWS CLI is installed and configured locally
- [ ] Default region is set (recommended: ap-south-1)
- [ ] IAM user with appropriate permissions is created
- [ ] Access keys are generated and stored securely

### Project Configuration
- [ ] `.env` file is updated with production values
- [ ] `USE_DYNAMODB=true` is set in `.env` for production
- [ ] AWS credentials are added to `.env` file
- [ ] `SECRET_KEY` is set to a strong random value
- [ ] `DEBUG=False` is set in `.env`
- [ ] Database models are updated for DynamoDB compatibility
- [ ] All dependencies are updated in `requirements.txt`

### Code Preparation
- [ ] All database migrations are run locally
- [ ] Static files are collected locally
- [ ] Code is tested thoroughly
- [ ] No hardcoded credentials in code
- [ ] Environment variables are used for all sensitive data

---

## AWS Infrastructure Setup

### IAM Configuration
- [ ] IAM user `staycomfy-backend` is created
- [ ] Custom IAM policy is attached with DynamoDB, S3, and CloudWatch permissions
- [ ] Access keys are generated and saved securely
- [ ] IAM credentials are added to `.env` file

### DynamoDB Setup
- [ ] DynamoDB tables are created:
  - [ ] `staycomfy-hotels`
  - [ ] `staycomfy-rooms` with GSI `hotel-id-index`
  - [ ] `staycomfy-users`
  - [ ] `staycomfy-bookings` with GSI `user-email-index`
- [ ] Tables are in "Active" status
- [ ] Auto scaling is configured (optional but recommended)
- [ ] Point-in-time recovery is enabled
- [ ] On-demand backup is created

### S3 Setup
- [ ] S3 bucket `staycomfy-static` is created
- [ ] Bucket name is globally unique
- [ ] Static website hosting is enabled
- [ ] Bucket policy allows public read access
- [ ] CORS configuration is set up
- [ ] Versioning is enabled (optional but recommended)

### EC2 Setup
- [ ] EC2 instance is launched with appropriate instance type
- [ ] Key pair is created and downloaded
- [ ] Security group `staycomfy-ec2-sg` is created
- [ ] Security group rules are configured:
  - [ ] SSH (port 22) from your IP
  - [ ] HTTP (port 80) from anywhere
  - [ ] HTTPS (port 443) from anywhere
  - [ ] Custom TCP (port 8000) from anywhere
- [ ] Security group is attached to EC2 instance
- [ ] Elastic IP is allocated and associated (optional)

### CloudWatch Setup
- [ ] CloudWatch log groups are created:
  - [ ] `/aws/ec2/staycomfy/application`
  - [ ] `/aws/ec2/staycomfy/error`
  - [ ] `/aws/ec2/staycomfy/nginx`
- [ ] Log retention policy is set (recommended: 30 days)
- [ ] CloudWatch alarms are configured:
  - [ ] CPU utilization > 80%
  - [ ] Memory utilization > 85%
  - [ ] Disk utilization > 80%
  - [ ] Application error rate
- [ ] SNS topic is created for alarm notifications (optional)
- [ ] CloudWatch agent is installed on EC2

---

## Deployment Process

### 1. Deploy to EC2
- [ ] Update `deploy_ec2.sh` with your EC2 IP and key pair path
- [ ] Make script executable: `chmod +x deploy_ec2.sh`
- [ ] Run deployment script: `./deploy_ec2.sh`
- [ ] Verify SSH connection works
- [ ] Verify application starts successfully
- [ ] Check systemd service status: `sudo systemctl status staycomfy`

### 2. Deploy Static Files to S3
- [ ] Update `deploy_s3.sh` with your bucket name and region
- [ ] Make script executable: `chmod +x deploy_s3.sh`
- [ ] Run deployment script: `./deploy_s3.sh`
- [ ] Verify files are uploaded to S3
- [ ] Test S3 website endpoint

### 3. Test Application
- [ ] Access application via EC2 public IP: http://your-ec2-ip:8000
- [ ] Test user registration and login
- [ ] Test hotel browsing and search
- [ ] Test booking creation
- [ ] Test admin panel access
- [ ] Verify static files load correctly from S3

### 4. Monitoring Setup
- [ ] Run CloudWatch setup script: `./setup_cloudwatch.sh`
- [ ] Verify log groups are created
- [ ] Verify alarms are created
- [ ] Test alarm notifications (if SNS is configured)

---

## Post-Deployment Checklist

### Security
- [ ] Security group rules are reviewed and tightened
- [ ] IAM credentials are not hardcoded in any files
- [ ] Only necessary ports are open in security groups
- [ ] VPC endpoints are configured for DynamoDB and S3 (optional)
- [ ] SSL/TLS certificates are configured
- [ ] Application is accessible via HTTPS only

### Performance
- [ ] Application response time is acceptable
- [ ] Database query performance is monitored
- [ ] Static files are served efficiently from S3
- [ ] CloudWatch metrics show healthy system
- [ ] Auto scaling is tested (if configured)

### Backup and Recovery
- [ ] DynamoDB point-in-time recovery is enabled
- [ ] Regular DynamoDB backups are scheduled
- [ ] EC2 AMI backup is created
- [ ] S3 versioning is enabled
- [ ] Backup restoration process is documented

### Documentation
- [ ] Deployment process is documented
- [ ] Troubleshooting guide is created
- [ ] Contact information for support is available
- [ ] Runbook for common operations is created

---

## Maintenance Tasks

### Daily
- [ ] Check CloudWatch alarms
- [ ] Review application logs
- [ ] Monitor system metrics

### Weekly
- [ ] Review AWS costs
- [ ] Check for security updates
- [ ] Test backup restoration

### Monthly
- [ ] Rotate IAM credentials
- [ ] Review and update IAM policies
- [ ] Performance tuning based on metrics
- [ ] Security audit

---

## Troubleshooting

### Application Won't Start
- [ ] Check systemd service status
- [ ] Review application logs in `/var/log/staycomfy/`
- [ ] Verify environment variables are set correctly
- [ ] Check database connectivity
- [ ] Verify all dependencies are installed

### Database Connection Issues
- [ ] Verify DynamoDB tables exist and are active
- [ ] Check IAM permissions for DynamoDB access
- [ ] Verify AWS credentials in `.env` file
- [ ] Check network connectivity to DynamoDB
- [ ] Review DynamoDB error logs

### Static Files Not Loading
- [ ] Verify S3 bucket policy allows public read
- [ ] Check CORS configuration
- [ ] Verify files are uploaded to correct bucket
- [ ] Check S3 bucket region matches configuration
- [ ] Test S3 website endpoint directly

### High CPU/Memory Usage
- [ ] Review CloudWatch metrics
- [ ] Check for memory leaks in application
- [ ] Optimize database queries
- [ ] Consider scaling up EC2 instance
- [ ] Review application logs for errors

### Security Group Issues
- [ ] Verify security group rules are correct
- [ ] Check if your IP is added to SSH access
- [ ] Verify security group is attached to EC2
- [ ] Test connectivity from different sources

---

## Rollback Plan

### If Deployment Fails
1. Stop the deployment script
2. Review error logs
3. Fix the issue
4. Restart deployment from failed step

### If Application Issues Occur
1. Check CloudWatch logs
2. Review recent changes
3. Rollback to previous version if needed
4. Test thoroughly before re-deploying

### Emergency Rollback
1. SSH into EC2 instance
2. Stop the application: `sudo systemctl stop staycomfy`
3. Revert to previous code version
4. Restart application: `sudo systemctl start staycomfy`
5. Verify application is working

---

## Cost Optimization

### Regular Reviews
- [ ] Review AWS Billing Dashboard
- [ ] Analyze cost by service
- [ ] Identify unused resources
- [ ] Optimize instance types based on usage

### Cost Saving Measures
- [ ] Use Reserved Instances for EC2
- [ ] Enable S3 lifecycle policies
- [ ] Configure DynamoDB auto scaling
- [ ] Use CloudWatch free tier effectively
- [ ] Clean up unused resources

---

## Contact and Support

### AWS Support
- AWS Support Center: https://console.aws.amazon.com/support/home
- Documentation: https://docs.aws.amazon.com/

### Project Resources
- Setup Guide: `AWS_SETUP_GUIDE.md`
- Original Setup Guide: `SETUP_GUIDE.md`
- Deployment Scripts: `deploy_*.sh`

### Emergency Contacts
- System Administrator: [Add contact]
- DevOps Engineer: [Add contact]
- AWS Account Owner: [Add contact]