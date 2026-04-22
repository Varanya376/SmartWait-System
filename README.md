Synq System 🍽️

AI-powered Restaurant Queue & Recommendation Platform

Overview

Synq is a full-stack web application designed to improve restaurant queue management by combining real-time wait-time prediction, smart recommendations, and interactive user features.

The system enables users to:

- View restaurants and their estimated wait times
- Join queues remotely
- Receive intelligent recommendations
- Interact with a dynamic frontend interface

The backend uses machine learning models to predict wait times based on historical and real-time data.

🛠️ Tech Stack

Frontend: React.js
          JavaScript,CSS

Backend: Django
         Django REST Framework

Database: SQLite

Machine Learning: Scikit-learn
                  Pre-trained .pkl models


Project Structure

SmartWait-System/

frontend/ → React application
smartwait_backend/ → Django backend
     - api/ → Core logic, models, views
     - model.pkl → ML model
     - wait_time_model.pkl → Wait-time prediction model
     - db.sqlite3 → Database

Prerequisites: Make sure the following are installed:

Python (3.9 or higher)
Node.js (LTS version recommended)
npm (comes with Node.js)
Git

Installation & Setup Guide (Windows): Follow these steps exactly in order.

STEP 1: Clone the Repository
git clone https://github.com/Varanya376/SmartWait-System.git
cd SmartWait-System

STEP 2: Backend Setup (Django)

Open Command Prompt / Terminal

1. Navigate to backend folder - cd smartwait_backend
2. Create virtual environment - python -m venv venv
3. Activate virtual environment

Windows:

venv\Scripts\activate

Mac/Linux (if needed): source venv/bin/activate

4. Install dependencies: pip install -r requirements.txt
5. Apply database migrations: python manage.py migrate
6. (Optional) Create admin user: python manage.py createsuperuser
7. Run backend server: python manage.py runserver

Backend will run at:
http://127.0.0.1:8000/

STEP 3: Frontend Setup (React)

Open a new terminal window (keep backend running)

1. Navigate to frontend: cd frontend
2. Install dependencies: npm install
3. Start frontend server: npm start

Frontend will run at:
http://localhost:3000/

Running the Full Application:-
Start backend server
Start frontend server
Open browser → http://localhost:3000/

The frontend will automatically connect to the backend API.

Machine Learning Models: The backend includes pre-trained models:-

model.pkl
wait_time_model.pkl

These are used to:

Predict restaurant wait times
Improve recommendation accuracy

No additional training is required to run the system.

API Endpoints (Examples)
/api/restaurants/ → Fetch restaurant list
/api/predict/ → Get wait-time prediction
/api/join-queue/ → Join queue


Admin Dashboard: Access Django admin panel:-

http://127.0.0.1:8000/admin/

Use the credentials created with: python manage.py createsuperuser

Important Notes:-

Always start backend before frontend
Ensure virtual environment is activated before running backend
Do NOT delete .pkl model files (required for predictions)


This system is intended to run locally.

Demo Usage Flow:-
Open frontend (localhost:3000)
Browse restaurant listings
View predicted wait times
Join a queue
Observe real-time updates

Key Features:-
Real-time wait-time prediction
Machine learning-based recommendations
Queue management system
User authentication
Admin dashboard

Conclusion: SmartWait demonstrates the integration of:-

Full-stack web development
Machine learning models
Real-time data handling

The system is designed for local execution and showcases a scalable architecture for intelligent queue management.

notes:
add npm install to start frontend first step

pip install daphne
pip install channels
python manage.py migrate