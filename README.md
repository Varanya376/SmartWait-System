# 🍽️ Synq System

Synq is a full-stack web application designed to improve restaurant queue management using real-time updates and machine learning-based predictions.

The system consists of:

- A Django backend  
- A React frontend  

This guide provides step-by-step instructions to set up and run the project locally.

---

## Project Structure

```
SmartWait-System/

├── smartwait_backend/        # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── api/                 # Core logic (models, views, ML, queue system)
│   ├── model.pkl
│   ├── wait_time_model.pkl
│
├── frontend/                # React frontend
```

---

## System Requirements

### Backend
- Python 3.9 or higher  
- pip  
- Virtual environment (venv)  

### Frontend
- Node.js (LTS recommended)  
- npm  

### General
- Git  
- Modern web browser (Chrome recommended)  

---

## Installation and Setup

### 1. Clone the Repository

```
git clone https://github.com/Varanya376/SmartWait-System.git
cd SmartWait-System
```

---

### 2. Create Virtual Environment (OUTSIDE project folder)

**Windows**
```
python -m venv venv
```

**macOS/Linux**
```
python3 -m venv venv
```

---

### 3. Activate Virtual Environment

**Windows**
```
venv\Scripts\activate
```

**macOS/Linux**
```
source venv/bin/activate
```

---

### 4. Install Backend Dependencies

```
cd smartwait_backend
pip install -r requirements.txt
pip install daphne channels python-dotenv
```

---

## 🔐 Environment Variables

Create a `.env` file inside:

```
smartwait_backend/
```

Add:

```

EMAIL_USER=varanya.376@gmail.com
EMAIL_PASS=ifhgbwrpswwxpxxl
```

⚠️ Notes:
- Use a Gmail **App Password**, not your real password  
- If email is not configured, OTP will be printed in the terminal  

---

## 🗄️ Database Setup

```
python manage.py migrate
```

(Optional)
```
python manage.py createsuperuser
```

---

## ▶️ Running the Application

### Start Backend

```
python manage.py runserver
```

Backend runs at:
```
http://127.0.0.1:8000/
```

---

### Start Frontend

Open a new terminal:

```
cd frontend
npm install
npm start
```

Frontend runs at:
```
http://localhost:3000/
```

---

## Configuration

- Default database: SQLite3  
- Pre-trained ML models included  
- No additional setup required  

---

## Features

- Real-time queue updates (WebSockets)  
- AI-based wait-time prediction  
- Smart restaurant recommendations  
- Queue join/leave system  
- Notification system (OTP + alerts)  
- Admin dashboard  

---

## Usage Notes

- Activate virtual environment before running backend  
- Run backend and frontend in separate terminals  
- Ensure ports are available:  
  - 8000 → Backend  
  - 3000 → Frontend  

---

## Demo Flow

1. Open frontend (localhost:3000)  
2. Browse restaurants  
3. View wait-time predictions  
4. Join queue  
5. Observe real-time updates  

---

## Troubleshooting

### Backend not starting
- Ensure virtual environment is activated  

---

### No restaurants showing
```
python manage.py migrate
```

(Data is auto-seeded automatically)

---

### OTP / Email not working
- Check `.env` file exists  
- Install dotenv:

```
pip install python-dotenv
```

- If email not configured → OTP appears in terminal  

---

### Frontend issues

```
rm -rf node_modules
npm install
```

---

### Port conflicts
- Change port or stop other services  

---

## Final Note

Synq demonstrates:

- Full-stack web development  
- Machine learning integration  
- Real-time systems using WebSockets  

The system is designed to run locally and is fully self-contained for demonstration and evaluation.