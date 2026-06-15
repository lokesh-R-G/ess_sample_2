# ESS + Payroll Backend

This folder contains the Python backend for the IDS Pvt Ltd ESS and payroll system.

## Stack

- FastAPI for APIs
- MongoDB Atlas for auth and attendance storage
- zeep for eSSL SOAP integration

## Core responsibilities

- Authenticate users with MongoDB Atlas
- Force password change on first login
- Sync raw attendance logs from eSSL into MongoDB
- Build processed daily attendance summaries from raw logs
- Serve attendance data only from MongoDB

## Environment

Copy `.env.example` to `.env` and fill in the secrets.

## Run

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload --app-dir backend
```

## Default flow

1. Seed users into MongoDB.
2. Log in with `empId` and the shared default password.
3. Change the password on first login.
4. Sync eSSL logs on a schedule or by admin action.
5. Read only processed attendance records from the API.
