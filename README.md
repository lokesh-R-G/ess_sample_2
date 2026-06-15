# 🚀 Employee Self Service (ESS) & Payroll Management System

A full-stack **Enterprise HRMS solution** designed to manage employee attendance, leave, and payroll operations with real-time integration to biometric systems.

---

## 📌 Overview

The **ESS & Payroll System** enables organizations to automate HR operations by integrating biometric attendance systems with a centralized web platform. It eliminates manual processes and provides real-time access to employee data.

---

## 🏗️ Tech Stack

### 🔹 Frontend

* React + TypeScript
* Vite
* Tailwind CSS
* Framer Motion
* ApexCharts

### 🔹 Backend

* FastAPI (Python)
* MongoDB Atlas
* Motor (Async MongoDB)
* JWT Authentication

### 🔹 Integration

* eSSL Biometric System (SOAP API via Zeep)

---

## ⚙️ Features

### 👤 Authentication

* JWT-based login system
* Role-Based Access Control (Admin / Employee)
* First login password reset

---

### 📊 Dashboard

* Attendance statistics (Present / Absent)
* Graphical insights
* Real-time API-driven data

---

### 📅 Attendance Management

* Calendar-based attendance tracking
* Daily IN / OUT records
* Auto-calculated attendance status:

  * Present
  * Absent

---

### 🛠️ Admin Module

* Create and manage users
* Trigger attendance sync
* View system-wide statistics

---

### 🔄 eSSL Integration

* Fetch biometric logs from eSSL system
* Store raw logs in `attendance_logs`
* Process into daily summaries in `attendance`

---

### ⏱️ Background Sync System

* First login → fetch last 90 days attendance
* Scheduled sync every 6 hours
* Incremental sync using `lastSyncAt`

---

## 🗂️ Project Structure

```
ess_sample_2/
│
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── scheduler/         # Background jobs
│   │   ├── db/                # MongoDB configuration
│   │   └── main.py            # FastAPI entrypoint
│   │
│   ├── scripts/               # Utility scripts
│   └── requirements.txt
│
├── src/
│   ├── components/            # UI components
│   ├── pages/                 # Application pages
│   ├── services/              # API services
│   ├── context/               # Auth & Theme
│   └── App.tsx                # Routing
│
└── README.md
```

---

## 🔐 Environment Setup

Create `.env` inside backend:

```
MONGO_URI=your_mongodb_uri
JWT_SECRET=your_secret_key

ESSL_URL=your_essl_wsdl_url
ESSL_USERNAME=your_username
ESSL_PASSWORD=your_password

FRONTEND_ORIGINS=http://localhost:5173
```

---

## ▶️ Running the Project

### 1️⃣ Backend

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

### 2️⃣ Frontend

```
cd ess_sample_2
npm install
npm run dev
```

---

## 🔗 API Endpoints

| Endpoint       | Method | Description        |
| -------------- | ------ | ------------------ |
| /auth/login    | POST   | User login         |
| /auth/me       | GET    | Get current user   |
| /dashboard/me  | GET    | Dashboard data     |
| /attendance/me | GET    | Attendance records |
| /admin/summary | GET    | Admin overview     |
| /sync/my-data  | POST   | Trigger user sync  |

---

## 🔄 Attendance Workflow

```
eSSL → Backend Sync → MongoDB → Frontend UI
```

1. Fetch logs from eSSL
2. Store raw data (`attendance_logs`)
3. Process into daily attendance
4. Display in UI

---

## 🧪 Current Status

### ✅ Completed

* Authentication system
* Attendance integration
* Admin module
* Frontend-backend integration
* Background sync system

### 🔄 In Progress

* Leave management workflow
* Payroll calculation module

### ⏳ Pending

* Payslip generation
* Notifications (Email/SMS)
* Advanced analytics

---

## ⚠️ Known Limitations

* eSSL integration requires valid credentials
* Payroll module not fully implemented
* Some admin pages are placeholders

---

## 🚀 Future Enhancements

* Full payroll engine
* Multi-branch support
* Real-time notifications
* AI-based attendance insights

---

## 👨‍💻 Author

**Lokesh Ramesh**

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
