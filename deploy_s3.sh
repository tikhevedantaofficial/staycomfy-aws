#!/bin/bash

# S3 Deployment Script for Staycomfy Static Files
# This script collects static files and uploads them to S3

set -e

# Configuration
S3_BUCKET="staycomfy-static"
AWS_REGION="ap-south-1"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting S3 deployment for Staycomfy..."

# Activate virtual environment if it exists
if [ -d "$PROJECT_DIR/.venv" ]; then
    echo "📦 Activating virtual environment..."
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "   Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Upload to S3
echo "☁️  Uploading files to S3 bucket: $S3_BUCKET..."
aws s3 sync staticfiles/ s3://$S3_BUCKET/ --region $AWS_REGION --delete --cache-control "public, max-age=31536000"

echo "✅ Deployment completed successfully!"
echo "🌐 Your static files are now available at: http://$S3_BUCKET.s3-website-$AWS_REGION.amazonaws.com"