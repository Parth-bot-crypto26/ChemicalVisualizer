# Chemical Equipment Parameter Visualizer (Hybrid App)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![React](https://img.shields.io/badge/react-18.2-61DAFB)
![Django](https://img.shields.io/badge/django-4.0%2B-092E20)
![PyQt5](https://img.shields.io/badge/PyQt5-Desktop-41CD52)

## 📌 Project Overview
The **Chemical Equipment Parameter Visualizer** is a robust, hybrid full-stack application designed for the analysis and visualization of chemical equipment data. It features a unique architecture where a **single Django REST API** serves two distinct frontends:
1.  A modern **Web Dashboard** (React.js)
2.  A native **Desktop Application** (PyQt5)

Both platforms support secure authentication, real-time data analytics, interactive charting, and PDF report generation, ensuring a seamless user experience across devices.

---

## 🚀 Key Features
* **Hybrid Architecture:** Unified backend powering both Web and Desktop clients.
* **Secure Authentication:** Token-based authentication system (Django REST Knox/AuthToken).
* **Data Analytics:** Automatic calculation of KPIs (Avg Temperature, Pressure, Flowrate).
* **Interactive Visualizations:**
    * **Web:** Chart.js implementation for dynamic bar charts.
    * **Desktop:** Matplotlib integration for native plotting.
* **History Management:** Tracks user-specific upload history.
* **Report Generation:** Server-side PDF generation with embedded analytics and charts.
* **Cross-Platform Sync:** Uploads from the web are instantly accessible on the desktop (and vice-versa).

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Django + DRF | RESTful API, Auth, Data Processing |
| **Database** | SQLite | Data persistence & User Management |
| **Web Frontend** | React.js + Bootstrap | Responsive Web Dashboard |
| **Desktop Frontend** | PyQt5 | Native Desktop Client (Windows/Linux/Mac) |
| **Visualization** | Chart.js / Matplotlib | Data rendering |
| **Reporting** | ReportLab | PDF Report Generation |

---

## ⚙️ Setup & Installation Guide

Follow these steps to set up the project locally.

### 1️⃣ Backend Setup (Django)
The backend is the heart of the application. It must be running for the frontends to work.

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create Superuser (Admin) for Login
python manage.py createsuperuser
# (Follow prompts to set username/password)

# Run Server
python manage.py runserver

### 2️⃣ Web Frontend Setup (React)
Open a new terminal for the web client.

```bash
# Navigate to web directory
cd frontend-web

# Install Node modules
npm install

# Start the React App
npm start


### 3️⃣ Desktop Frontend Setup (PyQt5)
Open a new terminal for the desktop client.

# Navigate to desktop directory
cd frontend-desktop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install PyQt5 requests matplotlib

# Run the Application
python main.py

### 🧪 How to Test the Application

Ensure the Backend is Running on port 8000.

Log in to either the Web or Desktop app using the superuser credentials you created.

Upload Data: Use the provided sample_equipment_data.csv file.

View Analytics: Check the Dashboard for charts and KPIs.

Generate Report: Click the "PDF" button in the history list to download the analysis report.
