🚀 Employee Self Service (ESS) & Payroll Management System

A full-stack Enterprise HRMS solution designed to manage employee attendance, leave, and payroll operations with real-time integration to biometric systems.

📌 Overview

The ESS & Payroll System is built for organizations to:

Automate attendance tracking via biometric devices (eSSL)
Provide employees with self-service access
Enable admins to manage workforce operations
Eliminate manual HR processes
🏗️ Tech Stack
🔹 Frontend
React + TypeScript
Vite
Tailwind CSS
Framer Motion
ApexCharts
🔹 Backend
FastAPI (Python)
MongoDB Atlas
Motor (async MongoDB driver)
JWT Authentication
🔹 Integration
eSSL Biometric System (SOAP API via Zeep)
⚙️ Features
👤 Authentication
JWT-based login system
Role-Based Access (Admin / Employee)
First login password reset
📊 Dashboard
Attendance statistics (Present / Absent)
Graphical insights
Real-time data from backend
📅 Attendance Management
Calendar-based attendance view
Daily IN / OUT tracking
Auto-calculated status:
Present
Absent
🛠️ Admin Module
Create and manage users
Trigger attendance sync
View system-wide data
🔄 eSSL Integration
Fetch biometric logs from device/cloud
Store raw logs (attendance_logs)
Process into daily attendance (attendance)
⏱️ Background Sync System
First login → fetch last 90 days data
Scheduled sync every 6 hours
Incremental updates (based on lastSyncAt)
🗂️ Project Structure
ess_sample_2/
│
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── scheduler/         # Background jobs
│   │   ├── db/                # MongoDB config
│   │   └── main.py            # FastAPI entrypoint
│   │
│   ├── scripts/               # Utility scripts
│   └── requirements.txt
│
├── src/
│   ├── components/            # UI components
│   ├── pages/                 # Application pages
│   ├── services/              # API calls
│   ├── context/               # Auth & Theme
│   └── App.tsx                # Routes
│
└── README.md
🔐 Environment Setup
Backend .env
MONGO_URI=your_mongodb_uri
JWT_SECRET=your_secret_key

# eSSL Config
ESSL_URL=your_essl_wsdl_url
ESSL_USERNAME=your_username
ESSL_PASSWORD=your_password

FRONTEND_ORIGINS=http://localhost:5173
▶️ Running the Project
1️⃣ Backend Setup
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
2️⃣ Frontend Setup
cd ess_sample_2
npm install
npm run dev
🔗 API Endpoints
Endpoint	Method	Description
/auth/login	POST	Login
/auth/me	GET	Get current user
/dashboard/me	GET	Dashboard data
/attendance/me	GET	Attendance records
/admin/summary	GET	Admin stats
/sync/my-data	POST	Trigger user sync
🔄 Attendance Workflow
eSSL → Backend Sync → MongoDB → Frontend UI
Fetch raw logs from eSSL
Store in attendance_logs
Process into daily records (attendance)
Display in calendar UI
🧪 Current Status
✅ Completed
Authentication system
Attendance integration
Admin control panel
Frontend-backend integration
Background sync (APScheduler)
🔄 In Progress
Leave management workflow
Payroll calculations
⏳ Pending
Payslip generation
Notifications (Email/SMS)
Advanced analytics
⚠️ Known Limitations
eSSL integration requires valid device credentials
Payroll module not fully implemented
Some admin pages are placeholders
🚀 Future Enhancements
Full payroll engine
Multi-branch support
Real-time notifications
AI-based attendance insights
👨‍💻 Author

Lokesh Ramesh

⭐ If you like this project

Give it a ⭐ on GitHub and feel free to contribute!
