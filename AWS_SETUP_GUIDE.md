# AWS Infrastructure Setup Guide for Staycomfy

## Overview
This guide walks through setting up the complete AWS infrastructure for the Staycomfy hotel booking website, migrating from MySQL to DynamoDB.

## Architecture
- **DynamoDB**: NoSQL database for hotels, rooms, bookings, and users
- **IAM**: Secure identity management for backend access
- **EC2**: Backend Django application server
- **Security Groups**: Network security for EC2
- **S3**: Static website hosting for frontend
- **CloudWatch**: Monitoring and logging for EC2

---

## 1. IAM User Setup

### 1.1 Create IAM User for Backend
1. Log in to AWS Console → **IAM** → **Users** → **Create user**
2. User name: `staycomfy-backend`
3. Select **Attach policies directly**
4. Create and attach the following custom policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DescribeTable"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/staycomfy-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:*:*:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::staycomfy-static",
                "arn:aws:s3:::staycomfy-static/*"
            ]
        }
    ]
}
```

### 1.2 Create Access Keys
1. Select the user → **Security credentials** → **Create access key**
2. Choose **Application running on an AWS compute service**
3. Save the **Access key ID** and **Secret access key** - you won't see them again!

---

## 2. DynamoDB Setup

### 2.1 Create Tables

#### Hotels Table
1. Go to **DynamoDB** → **Create table**
2. Table name: `staycomfy-hotels`
3. Partition key: `id` (String)
4. Sort key: None
5. Settings: Use default settings
6. Click **Create table**

#### Rooms Table
1. Table name: `staycomfy-rooms`
2. Partition key: `id` (String)
3. Sort key: `hotel_id` (String)
4. Create table

#### Users Table
1. Table name: `staycomfy-users`
2. Partition key: `email` (String)
3. Sort key: None
4. Create table

#### Bookings Table
1. Table name: `staycomfy-bookings`
2. Partition key: `id` (String)
3. Sort key: `user_email` (String)
4. Create table

### 2.2 Configure Global Secondary Indexes (GSIs)

#### Rooms GSI (for hotel queries)
1. Go to `staycomfy-rooms` table → **Indexes** → **Create index**
2. Index name: `hotel-id-index`
3. Partition key: `hotel_id` (String)
4. Create index

#### Bookings GSI (for user queries)
1. Go to `staycomfy-bookings` table → **Indexes** → **Create index**
2. Index name: `user-email-index`
3. Partition key: `user_email` (String)
4. Create index

### 2.3 Enable Auto Scaling (Optional but Recommended)
1. For each table → **Capacity** → **Auto scaling**
2. Set minimum and maximum capacity units
3. Set target utilization (e.g., 70%)

---

## 3. Backend Configuration for DynamoDB

### 3.1 Update Requirements
Add to `requirements.txt`:
```
boto3>=1.28.0
django-dynamodb-backend>=0.5.0
```

### 3.2 Update Django Settings
Modify `config/settings.py`:

```python
# DynamoDB configuration
import boto3
from django_dynamodb_backend import backend

# Update DATABASES for DynamoDB
DATABASES = {
    'default': {
        'ENGINE': 'django_dynamodb_backend',
        'NAME': 'staycomfy',
        'USER': os.getenv('AWS_ACCESS_KEY_ID'),
        'PASSWORD': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'HOST': os.getenv('AWS_REGION', 'ap-south-1'),
        'OPTIONS': {
            'table_prefix': 'staycomfy-',
        }
    }
}

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
```

### 3.3 Update .env File
```env
DEBUG=False
SECRET_KEY=your-production-secret-key

# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-south-1

# DynamoDB (optional, using defaults from settings)
DB_NAME=staycomfy
```

### 3.4 Update Models for DynamoDB
Modify models to use DynamoDB-compatible fields. Here's an example for `hotels/models.py`:

```python
from django.db import models
from django_dynamodb_backend.fields import DynamoDBCharField, DynamoDBTextField

class Hotel(models.Model):
    id = DynamoDBCharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotels'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.city}"

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return ''
```

---

## 4. S3 Setup for Static Website

### 4.1 Create S3 Bucket
1. Go to **S3** → **Create bucket**
2. Bucket name: `staycomfy-static` (must be globally unique)
3. Region: Choose your region (e.g., ap-south-1)
4. Block Public Access settings: 
   - Uncheck **Block all public access**
   - Acknowledge the warning
5. Create bucket

### 4.2 Enable Static Website Hosting
1. Select the bucket → **Properties** → **Static website hosting**
2. Click **Edit** → **Enable**
3. Index document: `index.html`
4. Error document: `error.html`
5. Save changes

### 4.3 Configure Bucket Policy
1. Go to **Permissions** → **Bucket policy**
2. Add this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::staycomfy-static/*"
        }
    ]
}
```

### 4.4 Configure CORS (Optional)
If you need API calls from the frontend:
1. Go to **Permissions** → **CORS configuration**
2. Add:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeRange>
        <AllowedHeader>Authorization</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

### 4.5 Upload Static Files
```bash
# Collect static files locally first
python manage.py collectstatic

# Upload to S3 using AWS CLI
aws s3 sync staticfiles/ s3://staycomfy-static/ --region ap-south-1
```

---

## 5. EC2 Setup

### 5.1 Launch EC2 Instance
1. Go to **EC2** → **Launch Instance**
2. Name: `staycomfy-backend`
3. AMI: Amazon Linux 2023 or Ubuntu 22.04 LTS
4. Instance type: `t3.medium` (or based on your needs)
5. Key pair: Create or select an existing key pair
6. Network settings:
   - VPC: Default
   - Subnet: Any subnet
   - Auto-assign public IP: Enable
   - Security group: Create new (see section 6)
7. Configure storage: 20 GB GP3
8. Launch instance

### 5.2 Connect to EC2 Instance
```bash
# Using SSH
ssh -i your-key-pair.pem ec2-user@your-ec2-public-ip

# Or using AWS Systems Manager Session Manager (if configured)
```

### 5.3 Install Dependencies on EC2
```bash
# Update system
sudo yum update -y  # For Amazon Linux
# sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install Python 3.12
sudo yum install python3.12 python3.12-pip -y

# Install virtualenv
sudo pip3.12 install virtualenv

# Create project directory
sudo mkdir /opt/staycomfy
sudo chown ec2-user:ec2-user /opt/staycomfy
cd /opt/staycomfy

# Create virtual environment
virtualenv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5.4 Deploy Application Code
```bash
# Upload your code to EC2
scp -i your-key-pair.pem -r /path/to/staycomfy ec2-user@your-ec2-ip:/opt/

# Or use git
cd /opt/staycomfy
git clone your-repo-url .
```

### 5.5 Configure Environment Variables
```bash
# Create .env file
nano /opt/staycomfy/.env
```

Add your production environment variables.

### 5.6 Run Migrations and Start Server
```bash
cd /opt/staycomfy
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load seed data
python manage.py seed_data

# Test server
python manage.py runserver 0.0.0.0:8000
```

### 5.7 Set Up Systemd Service
Create `/etc/systemd/system/staycomfy.service`:

```ini
[Unit]
Description=Staycomfy Django Application
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/opt/staycomfy
Environment="PATH=/opt/staycomfy/venv/bin"
EnvironmentFile=/opt/staycomfy/.env
ExecStart=/opt/staycomfy/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable staycomfy
sudo systemctl start staycomfy
sudo systemctl status staycomfy
```

---

## 6. Security Groups Configuration

### 6.1 Create Security Group for EC2
1. Go to **EC2** → **Security Groups** → **Create security group**
2. Name: `staycomfy-ec2-sg`
3. Description: Security group for Staycomfy backend

### 6.2 Inbound Rules
Add the following inbound rules:

| Type | Protocol | Port Range | Source | Description |
|------|----------|-----------|--------|-------------|
| SSH | TCP | 22 | Your IP/32 | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP access |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS access |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Django dev server (optional) |

### 6.3 Outbound Rules
Keep the default outbound rule (allow all traffic).

### 6.4 Attach Security Group to EC2
1. Go to your EC2 instance → **Security** → **Security groups**
2. Click **Edit security groups**
3. Add the `staycomfy-ec2-sg` security group
4. Save

---

## 7. CloudWatch Monitoring

### 7.1 Enable CloudWatch Monitoring for EC2
1. Go to your EC2 instance → **Actions** → **Monitor and troubleshoot** → **Manage detailed monitoring**
2. This enables 1-minute granularity metrics (additional cost)

### 7.2 Create CloudWatch Alarms

#### CPU Utilization Alarm
1. Go to **CloudWatch** → **Alarms** → **Create alarm**
2. Select metric: **EC2** → **Per-Instance Metrics** → **CPUUtilization**
3. Conditions:
   - Threshold type: Static
   - Whenever CPU utilization is: > 80%
   - For: 5 consecutive periods
   - Period: 1 minute
4. Notification: Send to SNS topic or email

#### Memory Utilization Alarm
You'll need to install the CloudWatch agent on EC2 first:

```bash
# Download and install CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Configure the agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Start the agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### 7.3 Create Log Groups
```bash
# Create log group for application logs
aws logs create-log-group --log-group-name /aws/ec2/staycomfy/application --region ap-south-1

# Create log group for nginx logs (if using nginx)
aws logs create-log-group --log-group-name /aws/ec2/staycomfy/nginx --region ap-south-1
```

### 7.4 Configure Application Logging
Update your Django settings to send logs to CloudWatch:

```python
# In config/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/staycomfy/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'cloudwatch': {
            'level': 'INFO',
            'class': 'watchtower.CloudWatchLogHandler',
            'log_group_name': '/aws/ec2/staycomfy/application',
            'stream_name': 'django-stream',
        },
    },
    'root': {
        'handlers': ['file', 'cloudwatch'],
        'level': 'INFO',
    },
}
```

Add to requirements.txt:
```
watchtower>=3.0.0
```

---

## 8. Domain and SSL Setup (Optional)

### 8.1 Purchase Domain
1. Go to **Route 53** → **Registered domains** → **Register domain**
2. Search for your domain (e.g., staycomfy.com)
3. Complete the purchase process

### 8.2 Create Hosted Zone
1. Go to **Route 53** → **Hosted zones** → **Create hosted zone**
2. Domain name: your domain
3. Create record set:
   - Type: A record
   - Value: Your EC2 public IP
   - TTL: 300

### 8.3 Setup SSL Certificate
1. Go to **ACM** (AWS Certificate Manager) → **Request a certificate**
2. Domain name: your domain
3. Validation method: DNS validation
4. Add the CNAME records to Route 53
5. Wait for validation

### 8.4 Set Up Load Balancer (Optional for production)
For production, consider using an Application Load Balancer:
1. Create ALB in EC2 console
2. Configure target group with your EC2 instance
3. Attach SSL certificate to the listener
4. Update Route 53 to point to ALB

---

## 9. Deployment Automation

### 9.1 Create Deployment Script
Create `deploy.sh`:

```bash
#!/bin/bash

# Configuration
EC2_USER="ec2-user"
EC2_HOST="your-ec2-ip"
KEY_PATH="your-key-pair.pem"
PROJECT_DIR="/opt/staycomfy"

# Deploy to EC2
echo "Deploying to EC2..."

# Copy files
scp -i $KEY_PATH -r . $EC2_USER@$EC2_HOST:$PROJECT_DIR

# SSH into EC2 and run deployment commands
ssh -i $KEY_PATH $EC2_USER@$EC2_HOST << 'ENDSSH'
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run migrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Restart service
    sudo systemctl restart staycomfy
ENDSSH

echo "Deployment completed!"
```

### 9.2 Set Up CI/CD Pipeline (Optional)
Consider using AWS CodePipeline or GitHub Actions for automated deployments.

---

## 10. Cost Optimization

### 10.1 Use Reserved Instances
- Consider purchasing Reserved Instances for your EC2 if running 24/7
- Save up to 75% compared to On-Demand pricing

### 10.2 Enable DynamoDB Auto Scaling
- Prevents over-provisioning during low traffic
- Automatically scales during high traffic

### 10.3 Use S3 Lifecycle Policies
- Move old static files to Glacier for long-term storage
- Set up automatic deletion of temporary files

### 10.4 Monitor CloudWatch Metrics
- Set up billing alerts
- Review cost explorer regularly

---

## 11. Backup and Disaster Recovery

### 11.1 DynamoDB Backups
1. Enable **Point-in-time recovery (PITR)** for each table
2. Create on-demand backups before major changes
3. Set up automatic backup schedules

### 11.2 EC2 Backups
1. Create AMIs of your EC2 instance regularly
2. Use AWS Backup for automated backup policies
3. Document the restoration process

### 11.3 S3 Versioning
Enable versioning on your S3 bucket:
```bash
aws s3api put-bucket-versioning --bucket staycomfy-static --versioning-configuration Status=Enabled
```

---

## 12. Security Best Practices

### 12.1 Use IAM Roles Instead of Access Keys
For EC2 instances, use IAM roles instead of hardcoded credentials:
1. Create IAM role with DynamoDB and S3 permissions
2. Attach the role to your EC2 instance
3. Remove AWS credentials from .env file

### 12.2 Enable VPC Endpoints
- Use VPC endpoints for DynamoDB and S3 to keep traffic within AWS network
- Reduces internet gateway costs and improves security

### 12.3 Enable Encryption
- Enable encryption at rest for DynamoDB tables
- Use SSL/TLS for all communications
- Encrypt S3 buckets using server-side encryption

### 12.4 Regular Security Audits
- Use AWS Trusted Advisor for security recommendations
- Enable AWS Config for compliance monitoring
- Regularly rotate IAM credentials

---

## Troubleshooting

### Common Issues

#### DynamoDB Connection Issues
- Verify IAM permissions
- Check AWS region configuration
- Ensure tables exist and are active

#### EC2 Connection Issues
- Verify security group rules
- Check key pair permissions
- Ensure instance is running

#### S3 Static Website Issues
- Verify bucket policy permissions
- Check CORS configuration
- Ensure files are uploaded to correct bucket

#### CloudWatch Not Receiving Logs
- Verify IAM permissions for CloudWatch
- Check log group configuration
- Ensure CloudWatch agent is running

---

## Maintenance Tasks

### Daily
- Monitor CloudWatch alarms
- Check application logs

### Weekly
- Review AWS costs
- Check for security updates
- Test backup restoration

### Monthly
- Rotate IAM credentials
- Review and update IAM policies
- Performance tuning based on metrics

---

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)

---

## Cost Estimate (Monthly)

Based on typical usage:
- **EC2 (t3.medium)**: ~$25/month
- **DynamoDB**: ~$15-50/month (depending on usage)
- **S3**: ~$1-5/month (depending on storage)
- **CloudWatch**: ~$5-10/month (depending on metrics)
- **Data Transfer**: ~$10-20/month
- **Total Estimate**: ~$56-110/month

Actual costs will vary based on your specific usage patterns.