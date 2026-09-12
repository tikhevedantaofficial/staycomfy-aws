# Staycomfy — Complete Setup Guide

## Table of Contents
1. [VS Code Setup & Running Locally](#1-vs-code-setup--running-locally)
2. [Connecting AWS Aurora RDS](#2-connecting-aws-aurora-rds)
3. [Deploying to IIS (Internet Information Services)](#3-deploying-to-iis)

---

## 1. VS Code Setup & Running Locally

### Prerequisites
- **Python 3.12+** — Download from [python.org](https://www.python.org/downloads/)
  - ⚠️ **Check "Add Python to PATH"** during installation
- **MySQL 8.0+** — Download from [dev.mysql.com/downloads](https://dev.mysql.com/downloads/installer/)
  - Remember the root password you set during installation

### Step 1: Open the Project in VS Code

1. Open **VS Code**
2. Go to **File → Open Folder**
3. Navigate to and select the `staycomfy` folder
4. Click **Select Folder**

### Step 2: Install Recommended Extensions

When prompted, install these extensions (or search for them manually):

| Extension | Purpose |
|-----------|---------|
| **Python** (Microsoft) | Python language support, debugging |
| **Django** (Baptiste Darthenay) | Django template syntax highlighting |
| **MySQL** (Jun Han) | Optional — database management from VS Code |

### Step 3: Create Virtual Environment

Open the terminal in VS Code (**Terminal → New Terminal**):

```bash
python -m venv .venv
```

### Step 4: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

You should see `(.venv)` appear at the start of your terminal prompt.

> **VS Code Tip:** If VS Code doesn't auto-detect the interpreter, press `Ctrl+Shift+P` → type "Python: Select Interpreter" → choose the `.venv` one.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Django 4.2.x
- mysqlclient (MySQL driver)
- python-dotenv (environment variables)
- Pillow (image handling)

### Step 6: Create the MySQL Database

Open **MySQL Command Line Client** (or MySQL Workbench) and run:

```sql
CREATE DATABASE staycomfy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 7: Configure Database Connection

Edit the `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=django-insecure-local-dev-change-me-in-production

DB_ENGINE=django.db.backends.mysql
DB_NAME=staycomfy
DB_USER=root
DB_PASSWORD=your_mysql_root_password
DB_HOST=localhost
DB_PORT=3306
```

Replace `your_mysql_root_password` with the password you set during MySQL installation.

### Step 8: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 9: Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to enter email, password, etc. This user can access the Django admin panel.

### Step 10: Load Sample Data

```bash
python manage.py seed_data
```

This creates 8 hotels with 24 rooms, each with unique photos.

### Step 11: Run the Development Server

```bash
python manage.py runserver
```

Open your browser to **http://127.0.0.1:8000/**

### Step 12: Run Tests (Optional)

```bash
python manage.py test
```

### Useful VS Code Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+`` ` | Toggle Terminal |
| `Ctrl+Shift+`` ` | New Terminal |
| `F5` | Start Debugging |
| `Ctrl+P` | Quick Open File |

### VS Code Debug Configuration (Optional)

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django Server",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver"],
            "django": true,
            "justMyCode": true
        }
    ]
}
```

Press **F5** to start with breakpoints enabled.

---

## 2. Connecting AWS Aurora RDS

### Overview

Staycomfy can connect to AWS Aurora MySQL or AWS RDS MySQL by changing only the `.env` file. No code changes needed.

### Step 1: Create an Aurora MySQL Cluster in AWS

1. Log in to the **AWS Console** → [console.aws.amazon.com](https://console.aws.amazon.com)
2. Go to **RDS** → **Create database**
3. Choose:
   - **Engine type:** Amazon Aurora
   - **Edition:** Aurora (MySQL Compatible)
   - **Version:** Latest stable (e.g., 8.0.mysql_aurora.3.x)
4. **Settings:**
   - **DB cluster identifier:** `staycomfy-db`
   - **Master username:** `staycomfy_admin`
   - **Master password:** (set a strong password — save it!)
5. **Instance class:** Choose based on needs (e.g., `db.t3.medium` for dev/testing)
6. **Connectivity:**
   - **VPC:** Default is fine
   - **Public access:** Yes (if connecting from outside AWS)
   - **Security group:** Create a new one allowing inbound TCP port **3306** from your IP
7. **Additional configuration:**
   - **Initial database name:** `staycomfy`
8. Click **Create database**

### Step 2: Get Your Aurora Endpoint

1. Once the database is **Available** (takes ~15 minutes)
2. Go to **RDS → Databases → staycomfy-db**
3. Under **Connectivity & security**, find the **Endpoint**
4. It looks like: `staycomfy-db.cluster-xxxxxxxxxxxx.us-east-1.rds.amazonaws.com`
5. **Copy this endpoint** — this is your `DB_HOST`

> ⚠️ **Important:** The AWS Console URL (e.g., `us-east-1.console.aws.amazon.com/rds/...`) is NOT the database endpoint. Use the endpoint from the database details page.

### Step 3: Configure Security Group

1. In the RDS database details, click the **Security group** link
2. Under **Inbound rules**, ensure there's a rule:
   - **Type:** MySQL/Aurora
   - **Protocol:** TCP
   - **Port:** 3306
   - **Source:** Your IP address (e.g., `203.0.113.50/32`) or `0.0.0.0/0` (anywhere — less secure)
3. If not, click **Edit inbound rules → Add rule** and save

### Step 4: Update Your `.env` File

Replace your local database settings:

```env
DEBUG=False
SECRET_KEY=change-to-a-long-random-string

DB_ENGINE=django.db.backends.mysql
DB_NAME=staycomfy
DB_USER=staycomfy_admin
DB_PASSWORD=your_aurora_password
DB_HOST=staycomfy-db.cluster-xxxxxxxxxxxx.us-east-1.rds.amazonaws.com
DB_PORT=3306
```

### Step 5: Run Migrations Against Aurora

```bash
python manage.py migrate
```

### Step 6: Load Sample Data

```bash
python manage.py seed_data
python manage.py createsuperuser
```

### Step 7: Test the Connection

```bash
python manage.py dbshell
```

If connected, you'll see the MySQL prompt:
```
mysql>
```

Run a quick test:
```sql
SELECT COUNT(*) FROM hotels_hotel;
```

Type `exit` to leave.

### Step 8: Switch Back to Local MySQL

Simply change `.env` back to your local settings:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_local_password
```

Then restart the server. That's it — no code changes needed.

### Troubleshooting Aurora Connection

| Problem | Solution |
|---------|----------|
| Connection refused | Check Security Group inbound rules for port 3306 |
| Timeout | Ensure "Publicly accessible" is set to Yes on the cluster |
| Access denied | Verify username/password in `.env` match the Aurora master credentials |
| Can't find endpoint | RDS → Databases → click cluster → Connectivity & security → Endpoint |

---

## 3. Deploying to IIS

### Overview

We'll use the **HttpPlatformHandler** module to run Django on IIS. This is the modern recommended approach (replaces the older wfastcgi method).

### Step 1: Enable IIS and Required Features

Open **PowerShell as Administrator**:

```powershell
# Enable IIS
dism /online /enable-feature /featurename:IIS-WebServerRole /all

# Enable CGI (required for HttpPlatformHandler)
dism /online /enable-feature /featurename:IIS-CGI /all

# Enable Static Content
dism /online /enable-feature /featurename:IIS-StaticContent /all

# Enable Default Document
dism /online /enable-feature /featurename:IIS-DefaultDocument /all
```

Or use **Server Manager** → Add Roles and Features → Web Server (IIS) → check:
- Common HTTP Features: Static Content, Default Document
- Application Development: CGI

### Step 2: Install HttpPlatformHandler

1. Download from Microsoft: [HttpPlatformHandler v1.2](https://www.microsoft.com/en-us/download/details.aspx?id=49053)
2. Choose the **x64** installer
3. Run the installer
4. Restart IIS:
   ```powershell
   iisreset
   ```

### Step 3: Install Python on the Server

Install Python on the server machine (same as your dev machine):
- Download Python 3.12+ from [python.org](https://www.python.org/downloads/)
- Check **"Add Python to PATH"**
- Verify:
  ```cmd
  python --version
  ```

### Step 4: Copy the Project to the Server

Copy the entire `staycomfy` folder to your server, for example:

```
C:\inetpub\staycomfy\
```

### Step 5: Set Up the Virtual Environment on the Server

Open **Command Prompt as Administrator**:

```cmd
cd C:\inetpub\staycomfy
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 6: Configure for Production

Edit `.env`:

```env
DEBUG=False
SECRET_KEY=generate-a-long-random-secret-key-here

DB_ENGINE=django.db.backends.mysql
DB_NAME=staycomfy
DB_USER=staycomfy_admin
DB_PASSWORD=your_db_password
DB_HOST=your_database_host
DB_PORT=3306
```

Generate a secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 7: Collect Static Files

Django needs all static files (CSS, JS) gathered in one folder for IIS to serve them:

```cmd
python manage.py collectstatic
```

This creates a `staticfiles/` folder with all CSS, JS, and images.

### Step 8: Run Migrations

```cmd
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
```

### Step 9: Set File Permissions

IIS needs read/write access to certain folders. Right-click the `staycomfy` folder → **Properties → Security → Edit → Add**:

| User/Group | Permissions |
|------------|-------------|
| `IIS_IUSRS` | Read & Execute |
| `IIS_IUSRS` | Write (on `media/` and `staticfiles/` folders) |

Or via PowerShell:
```powershell
icacls C:\inetpub\staycomfy /grant "IIS_IUSRS:(OI)(CI)RX" /T
icacls C:\inetpub\staycomfy\media /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls C:\inetpub\staycomfy\staticfiles /grant "IIS_IUSRS:(OI)(CI)F" /T
```

### Step 10: Create the `web.config` File

Create `C:\inetpub\staycomfy\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="httpPlatformHandler"
                 path="*"
                 verb="*"
                 modules="httpPlatformHandler"
                 resourceType="Unspecified" />
        </handlers>
        <httpPlatform processPath="C:\inetpub\staycomfy\.venv\Scripts\python.exe"
                      arguments="manage.py runserver --noreload 0.0.0.0:%HTTP_PLATFORM_PORT%"
                      stdoutLogEnabled="true"
                      stdoutLogFile="C:\inetpub\staycomfy\logs\django"
                      startupTimeLimit="60"
                      processesPerApplication="16">
            <environmentVariables>
                <environmentVariable name="DJANGO_SETTINGS_MODULE" value="config.settings" />
            </environmentVariables>
        </httpPlatform>

        <!-- Serve static files directly through IIS (much faster) -->
        <staticContent>
            <mimeMap fileExtension=".woff" mimeType="font/woff" />
            <mimeMap fileExtension=".woff2" mimeType="font/woff2" />
        </staticContent>
    </system.webServer>

    <!-- Static files: CSS, JS, images -->
    <location path="staticfiles">
        <system.webServer>
            <handlers>
                <clear />
            </handlers>
        </system.webServer>
    </location>

    <location path="media">
        <system.webServer>
            <handlers>
                <clear />
            </handlers>
        </system.webServer>
    </location>
</configuration>
```

### Step 11: Create the Logs Folder

```cmd
mkdir C:\inetpub\staycomfy\logs
```

### Step 12: Create the IIS Site

**Option A: Using IIS Manager (GUI)**

1. Open **IIS Manager** (`inetmgr`)
2. Right-click **Sites** → **Add Website**
3. Fill in:
   - **Site name:** `Staycomfy`
   - **Physical path:** `C:\inetpub\staycomfy`
   - **Binding:** HTTP, port `80` (or `8080` if 80 is taken)
   - **Host name:** Leave blank for local access, or enter your domain
4. Click **OK**

**Option B: Using PowerShell**

```powershell
# Create the website
New-WebSite -Name "Staycomfy" -PhysicalPath "C:\inetpub\staycomfy" -Port 80

# Set the application pool to No Managed Code (Python handles everything)
Set-ItemProperty IIS:\AppPools\Staycomfy -Name managedRuntimeVersion ""
```

### Step 13: Configure Application Pool

1. In **IIS Manager** → **Application Pools**
2. Find **Staycomfy** (or the default pool)
3. Right-click → **Advanced Settings**
4. Set **.NET CLR version** to **No Managed Code**
5. Set **Identity** to `LocalSystem` (or a specific user with DB access)

### Step 14: Start the Site

In IIS Manager:
- Select the **Staycomfy** site
- Click **Start** in the right panel

Or via PowerShell:
```powershell
Start-Website -Name "Staycomfy"
```

### Step 15: Test

Open your browser:
- **Local:** http://localhost/
- **From other machines:** http://your-server-ip/

### Step 16: Configure Windows Firewall

Allow inbound HTTP traffic:

```powershell
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

### Troubleshooting IIS

| Problem | Solution |
|---------|----------|
| 502.3 Bad Gateway | Check `logs/django-stdout.log` for errors. Verify Python path in `web.config` |
| Static files not loading | Run `python manage.py collectstatic`. Check IIS static content handler |
| Database connection error | Verify `.env` settings. Test with `python manage.py dbshell` |
| Permission denied on media uploads | Grant `IIS_IUSRS` write access to `media/` folder |
| Site won't start | Check Application Pool is set to "No Managed Code" |
| Port already in use | Change the port in IIS site bindings, or stop the conflicting service |

### Checking IIS Logs

```powershell
# Django application logs
type C:\inetpub\staycomfy\logs\django*.log

# IIS request logs
type C:\inetpub\logs\LogFiles\W3SVC*\*.log
```

### Production Checklist

- [ ] `DEBUG=False` in `.env`
- [ ] Strong random `SECRET_KEY` in `.env`
- [ ] Database credentials are not default/weak
- [ ] `python manage.py collectstatic` has been run
- [ ] `media/` folder has write permissions for IIS
- [ ] Windows Firewall allows port 80
- [ ] Application Pool is set to "No Managed Code"
- [ ] Test from a different machine on the same network

---

## Quick Reference

### Common Commands

```bash
# Run locally
python manage.py runserver

# Run tests
python manage.py test

# Create admin user
python manage.py createsuperuser

# Load sample data
python manage.py seed_data

# Collect static files for production
python manage.py collectstatic

# Open database shell
python manage.py dbshell

# Check database connection
python manage.py inspectdb
```

### File Structure

```
staycomfy/
├── .env                    ← Database & secret config
├── .venv/                  ← Virtual environment
├── manage.py               ← Django management
├── requirements.txt        ← Python dependencies
├── web.config              ← IIS configuration (for deployment)
├── config/                 ← Django settings
├── accounts/               ← User auth
├── hotels/                 ← Hotel & room models
├── bookings/               ← Booking system
├── templates/              ← HTML templates
├── static/                 ← CSS, JS (source)
├── staticfiles/            ← CSS, JS (collected for production)
├── media/                  ← Uploaded images
└── logs/                   ← IIS/Django logs
```
