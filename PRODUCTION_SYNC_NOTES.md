# Production Synchronization Notes

## Changes Made to Match AWS EC2 Production Server

### ✅ Files Modified

#### 1. `config/__init__.py`
**Added PyMySQL configuration:**
```python
import pymysql
pymysql.install_as_MySQLdb()
```
This configures PyMySQL as the default MySQL connector, which is more compatible than mysqlclient.

#### 2. `config/settings.py`
**Added WhiteNoise middleware:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added this line
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]
```
WhiteNoise serves static files efficiently in production and must be placed immediately after SecurityMiddleware.

**Added AWS SNS configuration:**
```python
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN', '')
```

**Removed DynamoDB configuration:**
- Removed boto3 and django-dynamodb-backend imports
- Removed DynamoDB database configuration logic
- Simplified to use MySQL RDS only

#### 3. `requirements.txt`
**Updated dependencies:**
```
Django>=4.2,<5.0
python-dotenv>=1.0
Pillow>=10.0
gunicorn>=21.0.0
pymysql                    # Added
whitenoise                 # Added
boto3>=1.28.0              # Added for SNS email service
```
Removed AWS-specific DynamoDB packages, kept boto3 for SNS email service.

#### 4. `.env`
**Set USE_DYNAMODB to false:**
```env
USE_DYNAMODB=false
```
This ensures the application connects to MySQL RDS instead of DynamoDB.

**Added AWS SNS configuration:**
```env
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ap-south-1
SNS_TOPIC_ARN=your_sns_topic_arn
```

#### 5. `.env.example`
**Updated to reflect production configuration:**
```env
DEBUG=true
SECRET_KEY=change-to-a-long-random-string

# Database Configuration - MySQL RDS
DB_ENGINE=django.db.backends.mysql
DB_NAME=staycomfy
DB_USER=admin
DB_PASSWORD=your_db_password
DB_HOST=your_rds_endpoint
DB_PORT=3306

# AWS Configuration for SNS Email Service
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ap-south-1
SNS_TOPIC_ARN=your_sns_topic_arn
```

### 🎉 New Feature: Welcome Email Service

#### Files Created
1. `bookings/email_service.py` - SNS email service implementation
2. `bookings/management/commands/send_welcome_emails.py` - Django management command
3. `templates/bookings/welcome_email.html` - HTML email template
4. `templates/bookings/welcome_email.txt` - Plain text email template
5. `bookings/migrations/0002_booking_welcome_email_sent.py` - Database migration

#### Files Modified
1. `bookings/models.py` - Added `welcome_email_sent` field
2. `accounts/models.py` - Removed DynamoDB dependencies
3. `hotels/models.py` - Removed DynamoDB dependencies
4. `aws-iam-policy.json` - Added SNS permissions

#### Feature Overview
- **Automatic welcome emails** sent to guests on check-in day
- **Beautiful HTML templates** with professional design
- **AWS SNS integration** for reliable email delivery
- **Tracking system** to prevent duplicate emails
- **Flexible scheduling** via cron or task scheduler

### 📦 Dependencies Installed
Successfully installed the new packages:
- `pymysql-1.2.0`
- `whitenoise-6.12.0`
- `boto3>=1.28.0` (for SNS email service)

### 🗄️ Database Configuration
The application is now configured to use MySQL RDS:
- **Engine**: django.db.backends.mysql (via PyMySQL)
- **Host**: staycomfy-db.c7008ucgarie.ap-south-1.rds.amazonaws.com
- **Database**: staycomfy
- **User**: admin

### 🚀 Next Steps

#### 1. Test the Application
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

#### 2. Verify Database Connection
```bash
# Test database connection
python manage.py dbshell
```

#### 3. Setup Welcome Email Feature
```bash
# Send test email
python manage.py send_welcome_emails --test-email your.email@example.com

# Dry run to see what would be sent
python manage.py send_welcome_emails --dry-run

# Manual execution
python manage.py send_welcome_emails
```

#### 4. Collect Static Files (for production)
```bash
python manage.py collectstatic
```

### 🔧 Key Benefits of These Changes

1. **PyMySQL vs mysqlclient**: PyMySQL is a pure Python MySQL client that's easier to install and maintain, while providing the same functionality.

2. **WhiteNoise**: 
   - Serves static files efficiently without needing a separate web server
   - Compresses static files automatically
   - Supports HTTP caching headers
   - Essential for serving static files in production

3. **Welcome Email Service**:
   - Automated guest communication
   - Professional email templates
   - AWS SNS reliability
   - Tracking and error handling

4. **Simplified Configuration**: 
   - Removed DynamoDB complexity
   - Focused on MySQL RDS for production
   - Cleaner, more maintainable codebase

### 📝 Notes

- The DynamoDB-related files (`dynamodb_models.py`, `dynamodb_utils.py`, `dynamodb-schema.json`) are still present but not actively used
- These can be removed if you're certain you won't need DynamoDB in the future
- The AWS deployment scripts and documentation remain available for reference
- Welcome email feature requires AWS SNS setup (see WELCOME_EMAIL_SETUP.md)

### ⚠️ Important

- Ensure your MySQL RDS instance is accessible from your local environment
- Verify the database credentials in `.env` are correct
- The production server uses the same configuration, ensuring consistency between environments
- For welcome emails, set up AWS SNS topic and update `.env` with SNS_TOPIC_ARN