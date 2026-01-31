# V.I.S.T.A. Analytics: Hybrid Chemical Telemetry Platform 
**Virtual Interactive Speech and Text Assistant | Enterprise Asset Monitoring**

**Developed by:** [Aman Shakya](https://github.com/yourusername)  
*3rd Year Computer Science Engineering  | VIT Bhopal University*  


---

## 📖 Project Vision
V.I.S.T.A. is a production-grade, hybrid analytics platform built to bridge the gap between industrial sensor data and decision-making. It provides a unified data pipeline that ingests raw chemical asset telemetry and synchronizes analysis across both Web and Desktop environments.

## 🛠️ System Architecture
The platform utilizes a **Stateless Hybrid Architecture**:
* **Centralized API**: A Django REST Framework backend serving as the "Single Source of Truth."
* **Web Dashboard**: A React.js application optimized for remote monitoring and history tracking.
* **Desktop Pro**: A PyQt5 application designed for high-performance local data ingestion and Matplotlib rendering.

## ✨ Key Features
* **Cross-Platform Data Sync**: Datasets uploaded via the Desktop tool are instantly processed and reflected in the Web Dashboard's history.
* **Advanced Data Processing**: Automated calculation of Mean Temperature, Average Pressure, and Flowrate distributions using Pandas.
* **Interactive Visualizations**: 
    * **Web**: Chart.js for responsive, interactive bar graphs.
    * **Desktop**: Matplotlib integrated into PyQt5 for professional-grade plotting.
* **Secure Reporting**: Server-side PDF generation using ReportLab, providing equipment-specific summaries.

## 🔐 Security & Authentication Deep Dive
This project implements a sophisticated dual-layer security model to handle different client types:
1.  **Session-Based Auth (Web)**: Uses Django's `SessionAuthentication` to persist logins within the browser using secure cookies.
2.  **Basic Auth (Desktop)**: The PyQt5 client utilizes `HTTPBasicAuth` headers to sign every request, ensuring secure data transfer without browser cookies.
3.  **User Isolation**: Database queries are strictly filtered using `request.user` to ensure users only ever see their own uploaded datasets.
4.  **CORS Management**: Configured with `django-cors-headers` to safely allow communication between the different local ports used by React (3000) and Django (8000).

## ⚙️ Detailed Installation & Setup

### 1. Backend (Django REST)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install django djangorestframework django-cors-headers pandas reportlab requests
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser # Create your access credentials
python manage.py runserver

