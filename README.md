# Eskala Operations - Equity Management Platform

A comprehensive web-based equity management system designed for microfinance operations in Honduras. Built as part of the University of Maryland BUDT748 Industry Capstone project.

--NOTE:- This was our capstone group project comprising of 5 members, with each member having different valuable contributions.

**Live Site:** https://budt748s04t03.rhsmith.umd.edu

## Project Overview

Eskala Operations is a Flask-based platform that enables microfinance organizations to track and manage equity investments, conversions, dividends, and partner relationships. The system provides bilingual support (English/Spanish) and features role-based access controls for staff and banking partner users.

## Key Features

### Data Entry Forms
The platform includes five specialized forms for comprehensive equity data management:

**Primarily for Banking Partners:**
- **Dividend Entry Form** - Used to submit proof of dividend payments to Eskala staff
- **Request for Equity Conversion** - Used to convert dividend payments into additional equity for Eskala, or to request additional capital from Eskala in exchange for an increased equity stake in the partner bank

**Primarily for Eskala Staff:**
- **Investments vs Loans** - Used to track current investments or loans made by Eskala and assess the financial health and profitability of those loans
- **Micro Equity Matching** - Used to collect data on potential banking partners that have not yet demonstrated profitability, helping determine their eligibility for investment by Eskala
- **Micro Equity Profit** - Used to collect data on potential banking partners that have demonstrated profitability, supporting investment eligibility assessments for Eskala

### CRUD Data Tables
Each form has a corresponding data table with full CRUD (Create, Read, Update, Delete) functionality:
- View all submitted entries with sorting and filtering
- Edit existing records with audit trail tracking
- Delete records with confirmation
- Download data as CSV for external analysis
- Attachment viewing for uploaded documents
- **Investments vs Loans**, **Micro Equity Matching**, and **Micro Equity Profit** include additional bulk upload capability for importing multiple records at once

### Administrative Tools

- **Formula Manager** - Configure and manage calculation formulas for auto-calculated fields across all forms. Supports dynamic formula editing with real-time validation and version history.

- **Exchange Rate Manager** - Manage USD/HNL exchange rates with historical tracking. Update current rates, view rate history with timestamps, and track who made changes.

- **User Administration** - Complete user management system including:
  - Add new staff and banking partner users
  - Email invitation system with password setup
  - Approve or reject pending user registrations
  - Activate/deactivate user accounts
  - Role-based access control (Staff vs Banking Partner)
  - Filter users by status, role, and account state

### Reports Dashboard
Interactive analytics dashboard featuring:
- Total pipeline overview with proposal state breakdown
- Proposal state visualization (Accepted, Rejected, Executed, Presented, To Pitch)
- Geographic distribution by state
- Business category/influence zone analysis
- Monthly disbursement projections
- Toggle between Matching Equity and Profit-Sharing data sources
- **PDF Export** - Download complete dashboard as PDF report

### Authentication System
- Secure login for staff and banking partners
- Email verification for new accounts
- Admin approval workflow for new registrations
- Password reset via email
- Session management with remember-me functionality

### Additional Features
- **Bilingual Support** - Full English/Spanish language toggle throughout the application
- **Form Autosave** - Automatic draft saving to prevent data loss
- **Audit Logging** - Complete audit trail for all data modifications
- **Responsive Design** - Works on desktop and mobile devices

## Technology Stack

### Backend Framework
- **Flask 3.0.3** - Python web framework for building the application
- **Flask-CORS 4.0.0** - Handles cross-origin resource sharing for API requests
- **flask-mysqldb 2.0.0** - Flask extension for MySQL database connections
- **Gunicorn** - WSGI HTTP server for production deployment

### Database
- **MySQL 8.0+** - Relational database management system
- **SQLAlchemy 2.0.32** - SQL toolkit and Object-Relational Mapping (ORM) library
- **PyMySQL 1.1.1** - Pure Python MySQL client library
- **mysql-connector-python 8.0.33** - Official MySQL driver for Python

### Security & Configuration
- **bcrypt 4.2.0+** - Password hashing and encryption
- **python-dotenv 1.0.1** - Manages environment variables from .env files

### Frontend
- **HTML/CSS/JavaScript** - User interface and client-side functionality
- **Chart.js** - Interactive charts for Reports Dashboard
- **html2canvas / jsPDF** - PDF export functionality


## Team Members & Roles

| Name | Role |
|------|------|
| Lakshmi Nair | Project Management |
| Noah Dolnick | Technical Lead |
| Selina Liu | Software Quality Assurance |
| Giselle Barretto | User Experience Developer |
| **Amogha Aithal** | **Business Systems Analyst** |

### My Contributions (Amogha Aithal)

As Business Systems Analyst on this project, my responsibilities included:

- **Requirements Analysis:** Defined the project scope & objectives through interaction with client, then documented the system requirements, thereby translating business needs into technical specifications.

- **UI/UX Design:** Created Figma prototypes for three data entry forms (Dividend Entry, Equity Conversion Request, Investments vs Loans), three administrative interfaces (main landing page, Eskala staff login and Eskala staff dashboard) and the Formula Manager.

- **Feature Specification:** Defined functional requirements (what the forms should contain/dashboards should display) and high-level system specifications (such as access controls) for multiple data entry forms and reporting dashboards.

- **Workflow Design:**  Helped in designing end-to-end processes for dividend submissions, equity conversions and reporting workflows to improve operational efficiency by migrating from manual spreadsheets to an automated platform.

- **Agile Team Collaboration:** Collaborated within a 5-person team; built cross-functional relationships with various departments; worked in Scrum-style sprints with Agile planning through development, testing, and deployment.

- **Use Case Documentation:** Prepared a comprehensive use-case documentation detailing the complete functioning of the various data-entry forms, interfaces and dashboards using visuals and explanations.  

---
## Repository Structure

```
F2025-504-Eskala-Operations/
├── flaskapp/                    # Frontend assets directory
│   ├── Assets/                  # Image assets (logos)
│   ├── js/                      # Client-side JavaScript
│   └── web/                     # HTML templates
│       └── styles/              # CSS stylesheets
├── uploads/                     # File upload directory
├── admin.py                     # Admin panel & user management API
├── app.py                       # Main Flask application entry point
├── auth.py                      # Authentication & authorization API
├── db.py                        # Database connection utilities
├── equity.py                    # Equity entry & conversion API
├── equity_current.py            # Current equity calculations
├── fx_rates.py                  # Exchange rate management API
├── reports.py                   # Report generation API
├── gunicorn_conf.py             # Gunicorn server configuration
├── wsgi.py                      # WSGI entry point for deployment
├── .env                         # Environment variables template
├── requirements.txt             # Python dependencies
├── Eskala_DB_Local.sql          # Database schema for local development
└── Eskala_DB_Server.sql         # Database schema for production server
```

---

## Local Development Setup

### Prerequisites

#### Required Software
1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/

2. **MySQL 8.0 or higher**
   - Includes MySQL Server and MySQL Workbench
   - Download from: https://dev.mysql.com/downloads/mysql/

3. **Visual Studio Code (VS Code)**
   - Download from: https://code.visualstudio.com/

4. **Git**
   - Download from: https://git-scm.com/downloads/

#### Required Files
- `Eskala_DB_Local.sql` - Database schema (included in the repository after cloning)

### Step 1: Clone the Repository

Create a project folder and clone the repository:

```bash
mkdir Eskala_Project
cd Eskala_Project
git clone https://github.com/UMDMSISCapstone/F2025-504-Eskala-Operations.git
cd F2025-504-Eskala-Operations
```

### Step 2: Create Virtual Environment

**Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python3 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Set Up the Database

1. Open MySQL Workbench and sign in with your credentials
2. Go to **File > Open SQL Script** and select `Eskala_DB_Local.sql`
3. Run the script by clicking the lightning bolt icon

### Step 4: Configure Environment Variables

Create/edit the `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_root_password
DB_NAME=user_management

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DEBUG=True
PORT=5000
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` value.

### Step 5: Run the Application

```bash
python app.py
```

Open your browser and navigate to: **http://localhost:5000**

---

## Production Server Deployment

### Prerequisites
- UMD GlobalProtect VPN connection
- Server credentials

### Step 1: Set Up the Database

1. Navigate to: https://budt748.rhsmith.umd.edu/phpmyadmin/
2. Sign in with server credentials
3. Click **Databases** and create a new database (name must start with `budt748s04t03_`)
4. Select the new database and click **Import**
5. Choose `Eskala_DB_Server.sql` and click **Import**

### Step 2: Update Environment Variables

Update your `.env` file with production settings:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=budt748s04t03
DB_PASSWORD=IM]Qry5139631
DB_NAME=budt748s04t03_Eskala_Smith

FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
DEBUG=False
PORT=5000

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=eskala.equity@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=eskala.equity@gmail.com
BASE_URL=https://budt748s04t03.rhsmith.umd.edu
```

### Step 3: Upload Files to Server

Connect to GlobalProtect VPN, then:

```bash
# Connect via SFTP
sftp budt748s04t03@budt748s04t03.rhsmith.umd.edu
# Enter password when prompted

# Upload Python files
cd flaskapp
put *.py
put requirements.txt
put .env

# Upload frontend assets
put -r js
put -r web
put -r Assets

# Exit SFTP
exit
```

### Step 4: Restart the Server

```bash
ssh budt748s04t03@budt748s04t03.rhsmith.umd.edu
sudo fixpermissions
restartwebserver
```

The site will be available at: **https://budt748s04t03.rhsmith.umd.edu**

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `restartwebserver` | Restart the Flask application |
| `sudo fixpermissions` | Fix file permissions after upload |
| `checkerrors` | View live error log (Ctrl+C to exit) |

---

## Contact

**Amogha Aithal**  
MS Information Systems, University of Maryland  
Email: amogha95@umd.edu  
LinkedIn: https://www.linkedin.com/in/amogha-aithal-539449317

---

## Project Context & Disclaimer

This project was completed as part of the University of Maryland MSIS Capstone program and delivered to the client.

The materials in this repository are shared strictly for educational and portfolio demonstration purposes.  
All proprietary rights to the deployed application belong to the client organization.


---

*Last Updated: December 2025*
