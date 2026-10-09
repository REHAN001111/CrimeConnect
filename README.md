# CrimeConnect — Online Crime Reporting and Complaint Management System

**Academic Information Technology Lab (ITL) Project Prototype**  
Developed with **Python 3, Flask, SQLite, SQLAlchemy, HTML5, CSS3, and JavaScript**.

---

> [!IMPORTANT]
> **Educational Demonstration Disclaimer:**  
> This web application is engineered strictly for educational demonstration and laboratory practical evaluation. It is **NOT** connected to any real police department, emergency dispatch, or official law enforcement agency. In real emergencies, call **911 / 112 / 100** immediately.

---

## 1. Project Overview

**CrimeConnect** is a full-stack web application designed to solve common challenges in public service incident logging. Citizens can register fictional complaints, immediately receive an algorithmically generated tracking reference code (e.g. `CR-20261001-A104E`), and inspect real-time review progress. Administrators have a dedicated, password-protected management console to audit complaints, update lifecycle statuses, record public remarks, and maintain confidential internal notes.

### Core Highlights
- **Role-Based Access Control (RBAC):** Server-enforced separation between citizens and administrative operators.
- **Secure Authentication:** Password hashing using Werkzeug (never plaintext), secure session cookies, and login redirection.
- **Automated Reference Generation:** Unique reference numbers generated upon submission (`CR-YYYYMMDD-XXXXX`).
- **Two-Factor Tracking Authorization:** Case tracking requires both the Reference Number and the registered Complainant Email to prevent unauthorized data exposure.
- **Audit History & Internal Notes:** Immutable status transitions with public citizen remarks, plus confidential internal staff notes hidden from ordinary users.
- **Evidence Management:** File uploads validated by extension and size, stored with randomized UUID identifiers outside public directories.
- **Analytics & Data Export:** Real-time visual charts with Chart.js and one-click CSV export for authorized administrators.
- **Modern Responsive UI:** Navy blue and white design system with responsive layouts and dark/light mode toggle.

---

## 2. Technology Stack

- **Backend:** Python 3 (3.10+ / 3.13 supported) with **Flask 3.x**
- **Database & ORM:** SQLite 3 via **Flask-SQLAlchemy**
- **Authentication & Forms:** **Flask-Login**, **Flask-WTF**, **WTForms**
- **Testing:** **pytest** automated test framework
- **Frontend:** HTML5, CSS3 (Custom Responsive Design System), JavaScript (ES6)
- **Visual Analytics:** **Chart.js**
- **Icons:** **Font Awesome 6**

---

## 3. Pre-configured Demonstration Credentials

The application includes a seeding utility (`seed_data.py`) that populates the database with default accounts and 6 realistic fictional incident reports:

| Account Type | Full Name | Email Address | Password | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | Chief Admin Officer | `admin@crimeconnect.local` | `Admin@123` | `admin` |
| **Citizen (Demo 1)** | Alex Morgan | `citizen@crimeconnect.local` | `Citizen@123` | `user` |
| **Citizen (Demo 2)** | Jane Doe | `jane@crimeconnect.local` | `Citizen@123` | `user` |

> [!TIP]
> The login page includes **Quick Demo Login** buttons (`Admin Demo` and `Citizen Demo`) to fill in credentials with a single click.

---

## 4. Installation and Execution Guide (Windows & VS Code)

Follow these step-by-step instructions in PowerShell or the VS Code integrated terminal:

### Step 1: Verify Python Installation
Ensure Python 3 is installed and added to your system PATH:
```powershell
python --version
```
*(Expected output: Python 3.10 or higher)*

### Step 2: Open Project in VS Code
Open the `crimeconnect` project folder in VS Code:
```powershell
cd crimeconnect
code .
```

### Step 3: Create and Activate Virtual Environment
Create an isolated Python virtual environment named `venv`:
```powershell
python -m venv venv
```
Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once)*

### Step 4: Install Dependencies
Install all required libraries from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize and Seed Database
Run the seeding script to create SQLite database tables, populate demo accounts, and generate realistic sample complaints:
```powershell
python seed_data.py
```

### Step 6: Start the Flask Development Server
Run the application server:
```powershell
python app.py
```
*(The server will start at `http://127.0.0.1:5000/`)*

### Step 7: Open in Browser
Open your preferred web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 5. Running Automated Tests

CrimeConnect comes with a complete **pytest** test suite covering authentication, RBAC, complaint registration, tracking security, and admin actions:

Run tests with verbose output:
```powershell
pytest -v
```
*(All 16 test cases will execute and verify database isolation, validation rules, and authorization boundaries).*

---

## 6. Project Directory Structure

```
crimeconnect/
├── app.py                      # Application factory, error handlers, and runner
├── config.py                   # Development, testing, and production configurations
├── extensions.py               # Flask extensions (SQLAlchemy, LoginManager, CSRFProtect)
├── forms.py                    # WTForms definitions and validation rules
├── models.py                   # Database schema models (User, Complaint, ComplaintHistory, AdminNote)
├── requirements.txt            # Python package dependencies
├── seed_data.py                # Database initialization and sample data generator
├── README.md                   # Installation and user guide
├── PROJECT_REPORT.md           # Comprehensive ITL college documentation
├── VIVA_QUESTIONS.md           # 20 ITL practical viva questions and model answers
├── instance/                   # Runtime SQLite database and isolated file uploads
│   ├── crimeconnect.db         # SQLite database file
│   └── uploads/                # Protected evidence storage directory
├── routes/                     # Blueprint modular controllers
│   ├── __init__.py
│   ├── auth.py                 # Registration, login, logout, and profile
│   ├── main.py                 # Landing page, about, and FAQ
│   ├── complaints.py           # Filing, dashboard, tracking, and downloads
│   └── admin.py                # Admin dashboard, status transitions, internal notes, CSV export
├── static/                     # Frontend static assets
│   ├── css/
│   │   └── style.css           # Modern navy/white responsive design system & dark mode
│   └── js/
│       ├── main.js             # Theme toggle, demo quick-fill, copy reference, form UX
│       └── admin_charts.js     # Chart.js visual statistics integration
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shared base layout, navbars, and disclaimer banners
│   ├── index.html              # Public landing page with metrics and guides
│   ├── about.html              # Academic context and architectural documentation
│   ├── faq.html                # Frequently asked questions
│   ├── login.html              # Login portal with quick demo buttons
│   ├── register.html           # Citizen registration form
│   ├── profile.html            # User account summary
│   ├── report_complaint.html   # Complaint filing form with validation
│   ├── complaint_success.html  # Post-submission confirmation with copyable tracking ID
│   ├── track_complaint.html    # Two-factor status verification portal
│   ├── user_dashboard.html     # Citizen incident table and search filters
│   ├── complaint_details.html  # Citizen case file view with status timeline
│   ├── admin_dashboard.html    # Staff control center with Chart.js analytics
│   ├── admin_complaint_detail.html # Case triage, status transition, and confidential notes
│   └── errors/                 # Friendly error pages (400, 403, 404, 500)
└── tests/                      # Automated test suite
    ├── conftest.py             # Test fixtures and in-memory test DB
    ├── test_auth.py            # Authentication & RBAC tests
    ├── test_complaints.py      # Complaint filing & tracking authorization tests
    └── test_admin.py           # Admin control, status update, and CSV export tests
```

---

## 7. Troubleshooting Common Issues

1. **PowerShell Script Execution Error (`running scripts is disabled`):**
   - Solution: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell, then retry activating `venv`.
2. **Port 5000 Already in Use:**
   - Solution: In `app.py`, change `port=5000` to `port=5050` or another free port, and visit `http://127.0.0.1:5050/`.
3. **Missing Module Error:**
   - Solution: Ensure virtual environment is activated (`(venv)` appears before your prompt) and run `pip install -r requirements.txt`.
4. **Database Reset Needed:**
   - Solution: Run `python seed_data.py` to recreate clean database tables with demonstration records.
