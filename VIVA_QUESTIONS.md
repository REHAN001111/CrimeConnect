# 20 COMMON VIVA VOCE QUESTIONS & ANSWERS
## Project: CrimeConnect — Online Crime Reporting System
**Target Audience:** College ITL / Software Engineering Viva & Practical Exam

---

### Q1: What is the main objective of CrimeConnect?
**Answer:**  
CrimeConnect is a web-based educational portal designed to allow citizens to file simulated incident complaints, receive an automated unique tracking reference number, and track case progress in real time. It provides a secure, role-separated administrative console for staff to audit cases, update workflow stages, share public remarks, and maintain confidential internal notes.

---

### Q2: Why did you choose Flask over Django for this project?
**Answer:**  
Flask is a lightweight, modular micro-framework that provides granular control over components without imposing monolithic defaults. It allows students to explicitly implement and understand every layer—routing, database ORM, authentication, and security defenses—making it ideal for an Information Technology Lab practical.

---

### Q3: How are user passwords secured in your database?
**Answer:**  
Passwords are never stored in plaintext. When a user registers, Werkzeug's `generate_password_hash()` creates a cryptographically salted one-way hash (using scrypt or pbkdf2:sha256). During login, `check_password_hash()` compares the hash with the entered password. Even if the database is exposed, original passwords cannot be reversed.

---

### Q4: How is Role-Based Access Control (RBAC) implemented?
**Answer:**  
Users have a `role` attribute (`'user'` or `'admin'`). We created a custom Python decorator `@admin_required` that wraps admin routes:
```python
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```
Furthermore, the user registration route hardcodes `role='user'`, preventing users from escalating privileges during account creation.

---

### Q5: What is CSRF, and how is the project protected against it?
**Answer:**  
CSRF (Cross-Site Request Forgery) occurs when a malicious website tricks an authenticated user's browser into submitting unauthorized requests. We enabled **Flask-WTF**'s `CSRFProtect`, which generates a cryptographically random, session-tied CSRF token for each user session and embeds it in every HTML form. Requests without a valid token are rejected with HTTP 400.

---

### Q6: How does the system prevent SQL Injection attacks?
**Answer:**  
Instead of concatenating raw user strings into SQL queries, we utilize **SQLAlchemy ORM**. SQLAlchemy automatically utilizes parameterized queries and prepared statements, ensuring that user inputs are treated strictly as data literals rather than executable SQL commands.

---

### Q7: How does the application generate unique complaint reference numbers?
**Answer:**  
The `Complaint.generate_reference_number()` static method combines the current UTC date with a 5-character cryptographic random uppercase hex token (e.g. `CR-20261009-8A4F2`). It also checks the database in a loop to guarantee that collisions never occur before assigning the identifier.

---

### Q8: How does the tracking feature protect complainant privacy?
**Answer:**  
The tracking portal requires a two-factor verification: the **Complaint Reference Number** AND the **Complainant's Registered Email Address**. This ensures that an unauthorized individual cannot view sensitive grievance details merely by guessing or knowing a reference number.

---

### Q9: How are uploaded evidence files handled securely?
**Answer:**  
1. File extensions are whitelisted (`.png`, `.jpg`, `.jpeg`, `.pdf`, `.txt`, `.docx`).
2. Maximum upload size is enforced (5 MB).
3. Files are renamed using randomized UUID strings (`uuid.uuid4().hex`) to prevent path traversal attacks (`../`).
4. Files are stored in a private `instance/uploads` directory outside the public `static/` directory and can only be downloaded via an authenticated route that verifies case ownership or admin status.

---

### Q10: What are the lifecycle statuses of a complaint in CrimeConnect?
**Answer:**  
The complaint lifecycle transitions through five standardized states:
1. **Submitted:** Filed by citizen and awaiting triage.
2. **Under Review:** Assigned to an investigator for examination.
3. **Additional Information Requested:** Complainant asked for clarifications or evidence.
4. **Resolved:** Action completed and grievance addressed.
5. **Closed:** Case archived and finalized.

---

### Q11: What is the difference between Public Remarks and Internal Administrative Notes?
**Answer:**  
- **Public Remarks** (`ComplaintHistory.public_remarks`): Updates written by the administrator intended for the citizen to explain why a status changed. Visible on the citizen's tracking timeline.
- **Internal Administrative Notes** (`AdminNote.note`): Confidential investigation logs written by staff (e.g. IP traces, officer assignments). Accessible strictly to administrators; ordinary users cannot view them.

---

### Q12: What is the Application Factory Pattern in Flask?
**Answer:**  
In `app.py`, the `create_app(config_class)` function instantiates and configures the Flask application object, initializes extensions (`db`, `login_manager`, `csrf`), and registers Blueprints. This pattern enables easy configuration switching (such as testing with an in-memory database) and prevents global state coupling.

---

### Q13: What is a Flask Blueprint?
**Answer:**  
A Blueprint is a way to organize related routes and handlers into independent modules. In CrimeConnect, we organized routes into four blueprints:
- `auth_bp`: User registration, login, logout, profile.
- `main_bp`: Landing page, about, FAQ.
- `complaints_bp`: Reporting, citizen dashboard, status tracking.
- `admin_bp`: Administrator control console, case review, CSV export.

---

### Q14: Explain the database relationship between Users and Complaints.
**Answer:**  
It is a **One-to-Many** relationship. One `User` can file multiple `Complaints`. In the `Complaint` model, `user_id` is a Foreign Key referencing `users.id`. In SQLAlchemy, this is mapped via `db.relationship('Complaint', backref='complainant', lazy=True)`.

---

### Q15: What HTTP status codes are used in your application and what do they mean?
**Answer:**  
- **200 OK:** Successful request (page rendered or data returned).
- **302 Found / Redirect:** Redirect after form submission or login.
- **400 Bad Request:** Form validation failure or expired CSRF token.
- **403 Forbidden:** Unauthorized access attempt (e.g., citizen accessing `/admin`).
- **404 Not Found:** Resource or complaint ID does not exist.
- **500 Internal Server Error:** Unhandled server exception (triggers automatic DB rollback).

---

### Q16: How is data exported to CSV for administrators?
**Answer:**  
The `/admin/export-csv` route queries matching complaints, writes rows using Python's built-in `csv.writer` into an in-memory `io.StringIO` buffer, and returns a Flask `Response` with `mimetype='text/csv'` and header `Content-Disposition: attachment; filename=crimeconnect_complaints_export.csv`.

---

### Q17: How did you implement visual analytics in the Admin Dashboard?
**Answer:**  
We created a JSON endpoint `/admin/api/stats` that computes category and status distributions. The frontend uses **Chart.js** via `admin_charts.js` to fetch this data asynchronously and render an interactive doughnut chart (by category) and a bar chart (by status).

---

### Q18: What is the purpose of `seed_data.py`?
**Answer:**  
`seed_data.py` is an initialization and demonstration utility. It drops and creates database tables, seeds a pre-configured administrator account (`admin@crimeconnect.local`), two citizen accounts, and creates 6 realistic fictional complaints with audit histories and internal notes so the project can be demonstrated immediately.

---

### Q19: How did you test your application?
**Answer:**  
We wrote an automated test suite in `tests/` using **pytest**. Using Flask's test client and an in-memory SQLite database (`sqlite:///:memory:`), we tested:
- User registration, login, logout, and duplicate email rejection.
- Complaint submission and unique reference number assignment.
- Authorization isolation (users cannot access other users' files).
- Two-factor tracking verification.
- Admin role restriction (unauthorized citizens receive 403).
- Status updates and CSV export.
All 16 test cases execute cleanly with zero failures.

---

### Q20: What are three immediate future enhancements you would add to CrimeConnect?
**Answer:**  
1. **Automated Email/SMS Alerts:** Sending notifications via SMTP or SMS whenever an administrator updates a case status.
2. **Interactive GIS Map:** Visualizing crime incident density across a geographic map using Leaflet.js.
3. **Citizen Two-Way Messaging:** Allowing complainants to upload additional evidence in response to an "Additional Information Requested" status.
