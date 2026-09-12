#!/bin/bash

# Complete Deployment Script for Staycomfy AWS Infrastructure
# This script orchestrates the complete deployment process

set -e

echo "🚀 Starting complete AWS deployment for Staycomfy..."
echo "📋 This will deploy:"
echo "   - Backend to EC2"
echo "   - Static files to S3"
echo "   - Set up CloudWatch monitoring"
echo ""

# Check if required scripts exist
if [ ! -f "deploy_ec2.sh" ]; then
    echo "❌ deploy_ec2.sh not found"
    exit 1
fi

if [ ! -f "deploy_s3.sh" ]; then
    echo "❌ deploy_s3.sh not found"
    exit 1
fi

# Make scripts executable
chmod +x deploy_ec2.sh deploy_s3.sh setup_cloudwatch.sh

# Deploy to EC2
echo "📦 Step 1: Deploying backend to EC2..."
./deploy_ec2.sh

# Deploy to S3
echo "📁 Step 2: Deploying static files to S3..."
./deploy_s3.sh

# Setup CloudWatch (optional - uncomment if needed)
# echo "📊 Step 3: Setting up CloudWatch monitoring..."
# ./setup_cloudwatch.sh

echo "✅ Complete deployment finished successfully!"
echo ""
echo "🌐 Your application is now live:"
echo "   - Backend: http://your-ec2-ip:8000"
echo "   - Static files: http://staycomfy-static.s3-website-ap-south-1.amazonaws.com"
echo ""
echo "📋 Next steps:"
echo "   1. Update your DNS to point to the EC2 instance"
echo "   2. Configure SSL/TLS certificates"
echo "   3. Set up load balancer for production"
echo "   4. Configure backup and disaster recovery"