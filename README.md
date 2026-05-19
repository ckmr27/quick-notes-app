# Quick Notes App

A secure, lightweight, and modern note-taking web application built using **Python**, **Flask**, and **SQLAlchemy**. This application is designed to be self-hosted, easy to deploy, and features robust security protections.

---

## 🚀 Key Features

*   **🔒 Secure Authentication**: User registration and login utilizing `scrypt` password hashing.
*   **🛡️ Security Hardening**:
    *   **Rate Limiting**: Limits login and registration endpoints to a maximum of 5 requests per 15 minutes using `Flask-Limiter` to protect against brute-force attacks.
    *   **Brute-Force Lockout**: Dynamically locks out user accounts for 2 minutes after 5 consecutive failed login attempts.
    *   **Session Timeout**: Automatically logs users out and invalidates sessions after 20 minutes of inactivity.
    *   **Note Ownership Enforcement**: Server-side validation ensuring users can only read, update, or delete notes they own.
*   **✏️ Note CRUD Management**: Create, view, edit, and delete notes dynamically.
*   **📂 Persistent Storage**: SQLite database integration with automated table creation on application startup.
*   **📱 Responsive UI**: A premium user interface with clean layouts, custom styling, and flash notification feedback.

---

## 🛠️ Technology Stack

*   **Backend Framework**: [Flask](https://flask.palletsprojects.com/)
*   **Database ORM**: [SQLAlchemy (Flask-SQLAlchemy)](https://flask-sqlalchemy.palletsprojects.com/)
*   **Authentication Manager**: [Flask-Login](https://flask-login.readthedocs.io/)
*   **Security & Rate Limiting**: [Flask-Limiter](https://flask-limiter.readthedocs.io/)
*   **Database Engine**: SQLite

---

## 📂 Project Architecture

```
quick-notes-app/
├── app/
│   ├── static/             # Static assets (CSS styles, JS, images)
│   │   └── css/
│   │       └── style.css   # Custom CSS styling
│   ├── templates/          # HTML templates (Jinja2)
│   │   ├── base.html       # Base layout
│   │   ├── dashboard.html  # User dashboard
│   │   ├── login.html      # Login page
│   │   ├── register.html   # Registration page
│   │   └── note_form.html  # Create/Edit note form
│   ├── __init__.py         # Application factory & setup
│   ├── auth.py             # Authentication blueprints & logic
│   ├── extensions.py       # Extension initializations (db, login manager, limiter)
│   ├── models.py           # SQLAlchemy Database Models (User, Note)
│   └── notes.py            # Notes blueprint & CRUD endpoints
├── instance/               # Flask instance folder (contains configs/databases)
├── .env                    # Environment variables (Ignored by Git)
├── .env.example            # Environment variables template
├── .gitignore              # Git ignored files & patterns
├── requirements.txt        # Python dependency manifest
├── run.py                  # Project entry point
└── venv/                   # Python virtual environment (Ignored by Git)
```

---

## ⚙️ Setup & Installation Instructions

### Prerequisites
*   Python 3.8 or higher
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/ckmr27/quick-notes-app.git
cd quick-notes-app
```

### 2. Set Up the Virtual Environment
Create and activate a virtual environment to manage dependencies locally:

*   **Windows (PowerShell)**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
*   **Windows (Command Prompt)**:
    ```cmd
    python -m venv venv
    .\venv\Scripts\activate.bat
    ```
*   **Linux / macOS**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to `.env` and configure your settings:
```bash
cp .env.example .env
```
Open `.env` and define:
```env
SECRET_KEY=your_generated_secret_key_here
FLASK_ENV=development
DATABASE_URL=sqlite:///app/notes.db
```
> [!NOTE]
> The database path in `DATABASE_URL` will be automatically resolved by the application to an absolute path relative to your project root.

---

## 🏁 Running the Project

Ensure your virtual environment is active, then execute the startup script:

```bash
python run.py
```

The application will start running at:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🛡️ API & Security Design Decisions

1.  **Dynamic Database URL Resolution**: On startup, the application factory parses `DATABASE_URL` and converts any relative SQLite URI starting with `sqlite:///` into a platform-agnostic absolute path, solving standard directory resolution bugs in Flask-SQLAlchemy 3.x.
2.  **Scrypt Password Hashing**: Hashing algorithm configured via Werkzeug security primitives ensuring robust protection of stored passwords.
3.  **Cross-Site Scripting (XSS) & Input Validation**: Strict validation on client input lengths (Usernames max 150, Passwords max 128, Note Title max 200, Content max 10000) coupled with Jinja2 autoescaping.
