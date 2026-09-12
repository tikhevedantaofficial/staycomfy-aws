#!/bin/bash

# EC2 Deployment Script for Staycomfy Backend
# This script deploys the Django application to an EC2 instance

set -e

# Configuration
EC2_USER="ec2-user"
EC2_HOST="your-ec2-public-ip"  # Replace with your EC2 public IP
KEY_PATH="your-key-pair.pem"    # Replace with your key pair path
PROJECT_DIR="/opt/staycomfy"
AWS_REGION="ap-south-1"

echo "🚀 Starting EC2 deployment for Staycomfy..."

# Check if key file exists
if [ ! -f "$KEY_PATH" ]; then
    echo "❌ Key pair file not found: $KEY_PATH"
    echo "   Please update the KEY_PATH variable in this script."
    exit 1
fi

# Check if key file has correct permissions
if [ $(stat -c %a "$KEY_PATH") != "600" ]; then
    echo "🔒 Setting correct permissions on key file..."
    chmod 600 "$KEY_PATH"
fi

# Test SSH connection
echo "🔌 Testing SSH connection to EC2..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no -o ConnectTimeout=10 $EC2_USER@$EC2_HOST "echo '✅ SSH connection successful'" || {
    echo "❌ Cannot connect to EC2 instance. Please check:"
    echo "   - EC2 instance is running"
    echo "   - Security group allows SSH (port 22) from your IP"
    echo "   - Key pair is correct"
    exit 1
}

# Create project directory on EC2
echo "📁 Creating project directory on EC2..."
ssh -i "$KEY_PATH" $EC2_USER@$EC2_HOST "sudo mkdir -p $PROJECT_DIR && sudo chown $EC2_USER:$EC2_USER $PROJECT_DIR"

# Copy project files to EC2
echo "📦 Copying project files to EC2..."
rsync -avz -e "ssh -i $KEY_PATH -o StrictHostKeyChecking=no" \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'media' \
    --exclude 'staticfiles' \
    --exclude '*.log' \
    ./ $EC2_USER@$EC2_HOST:$PROJECT_DIR/

# Install dependencies and setup application on EC2
echo "⚙️  Setting up application on EC2..."
ssh -i "$KEY_PATH" $EC2_USER@$EC2_HOST << 'ENDSSH'
    cd /opt/staycomfy
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p logs media staticfiles
    
    # Collect static files
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Run migrations
    echo "🗄️  Running database migrations..."
    python manage.py migrate
    
    # Setup systemd service
    echo "🔧 Setting up systemd service..."
    sudo cp staycomfy.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable staycomfy
    
    # Restart application
    echo "🔄 Restarting application..."
    sudo systemctl restart staycomfy
    
    # Check status
    sudo systemctl status staycomfy --no-pager
ENDSSH

echo "✅ EC2 deployment completed successfully!"
echo "🌐 Your application should be available at: http://$EC2_HOST:8000"
echo "📋 Check application logs: ssh -i $KEY_PATH $EC2_USER@$EC2_HOST 'tail -f /var/log/staycomfy/application.log'"