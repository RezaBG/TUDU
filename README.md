# TUDU Application

## Setup Instructions

### Step 1: Clone the Repository


```bash
git clone https://github.com/your-username/TUDU.git
cd TUDU
```

### Step 2: Set Up the Virtual Environment


Create and activate the virtual environment (if not already set up):


```bash
python3 -m venv .venv
source .venv/bin/activate  # For Linux/Mac
# or
.venv\Scripts\activate  # For Windows
```

### Step 3: Install Dependencies


Install the required packages from `requirements.txt`:


```bash
pip install -r requirements.txt
```

Note: Make sure to use the virtual environment before installing dependencies to avoid conflicts with system packages.

### Step 4: Configure Environment Variables


Make sure to set up the PostgreSQL database URL in your environment variables:


```bash
export DATABASE_URL="postgresql+psycopg2://dev:dev@localhost/tudu"
```

### Step 5: Run Database Migrations

To set up the database table and apply any schema changes, run the Alembic migrations:

1. Ensure Alembic is installed:

```bash
pip install alembic
```

2. Run the database migirations:

```bash
alembic upgrade head
```

### Step 6: Start the Application


Run the FastAPI application using Uvicorn:


```bash
uvicorn src.main:app --reload
```

### Step 7: Access the Application


Go to your browser and visit:


```
http://127.0.0.1:8000
```
