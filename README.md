# Petition Management System

A modern web-based platform for managing petitions, designed for institutions and organizations. Supports users, departments, and administrators with secure authentication, real-time notifications, analytics, and AI-powered features.

---

## Features

### For Users
- Register and login with OTP verification
- Submit petitions with detailed information
- AI-powered petition improvement suggestions
- Track petition status and view updates
- Receive email notifications for status changes and rejections
- View rejection reasons

### For Departments
- Secure login with OTP
- Dashboard with petition stats and quick actions
- View, filter, and manage assigned petitions
- Bulk status update for multiple petitions
- Provide mandatory rejection reasons
- Deadline countdown and overdue alerts
- Real-time notifications and daily/weekly reports

### For Administrators
- Admin dashboard with analytics and stats
- Manage departments and staff
- Oversee all petitions and user data
- Send reminders and generate reports
- Advanced analytics and performance tracking

---

## Technology Stack
- **Backend:** Python Flask
- **Database:** MongoDB
- **Frontend:** HTML, CSS, JavaScript
- **AI:** Google Gemini (for petition improvement)
- **Email:** SMTP (Outlook)

---

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/mini_project.git
   cd mini_project/project
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Edit `config.py` with your MongoDB URI, SMTP credentials, and Gemini API key
   - (Optional) Create a `.env` file for sensitive data
4. **Run the server:**
   ```sh
   python app.py
   ```
5. **Access the app:**
   - Open `http://127.0.0.1:5000` in your browser

---

## Folder Structure
```
project/
    app.py
    config.py
    models.py
    email_utils.py
    email_templates.py
    requirements.txt
    static/
    templates/
    ...
```

---

## Security
- Sensitive files (e.g., `config.py`, `.env`) are excluded via `.gitignore`
- OTP authentication for users and departments
- Role-based access control
- Secure email notifications

---

## License
This project is for educational purposes.

---

## Author
- Developed by [Your Name]
- [Your Email]
