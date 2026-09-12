🏨 StayComfy - Cloud-Based Hotel Management System (AWS)

An end-to-end hotel booking and management web application deployed on Amazon Web Services (AWS) using scalable production infrastructure.

---

📐 Architecture Overview
1. Amazon EC2: Hosts the Django application, Gunicorn WSGI server, and Nginx reverse proxy.
2. Amazon RDS: Fully managed relational database storing user profiles, room availability, and booking records.
3. AWS SNS (Simple Notification Service): Handles automated welcome emails and background notifications.
4. AWS IAM: Enforces least-privilege access roles, allowing the EC2 server to securely trigger AWS services without hardcoded credentials.
5. Linux Cron Daemon: Automates daily background tasks to process check-ins.

---

💻 Tech Stack
- Cloud: AWS (EC2, RDS, SNS, IAM, VPC)
- Backend: Python / Django
- Web Server: Nginx + Gunicorn
- OS/Environment: Linux 

🧠 Key Learnings
- Provisioning and configuring Linux EC2 instances, Security Groups, and reverse proxies (Nginx).
- Integrating backend application code with the AWS SDK (Boto3) to interact with AWS SNS.
- Designing IAM roles to avoid storing hardcoded AWS access keys inside the codebase.
- Deploying background automated tasks using Linux cron jobs.
