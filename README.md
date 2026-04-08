# 🌐 User Login & Registration Portal

A full-stack web application built with **Python Flask** and **SQLite**, 
designed for AWS EC2 deployment as part of AWS SAA-C03 certification learning.

## ✨ Features
- 🔐 Secure login with hashed passwords (Werkzeug)
- 👥 Add new users with role assignment (admin/user)
- 🔄 Reset password functionality
- 📊 Dashboard with all users table
- 🚪 Session management with Flask-Login

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Database | SQLite (local) → AWS RDS (production) |
| Frontend | HTML5 + CSS3 (AWS dark theme) |
| Auth | Flask-Login + Werkzeug password hashing |
| Hosting | AWS EC2 (Amazon Linux 2) |

## 🚀 Run Locally
```bash
# Clone the repo
git clone https://github.com/abhineshreddyalmawar/user-login-registration-portal.git
cd user-login-registration-portal

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install flask flask-login werkzeug

# Run the app
python app.py
```

Visit `http://127.0.0.1:5000`

## 🔑 Default Login
| Username | Password |
|----------|----------|
| admin | admin123 |

## ☁️ AWS Deployment
This app is configured for deployment on **AWS EC2** as part of the 
AWS Certified Solutions Architect (SAA-C03) learning path.