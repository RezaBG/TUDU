# TUDU Application

## About TUDU

TUDU is a task management application built using FastAPI and SQLAlchemy. It allows users to create, update, and manage tasks efficiently. This application integrates a PostgreSQL database and supports RESTful APIs for seamless task management.

---

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
.venv\\Scripts\\activate  # For Windows
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

Note: SQLite is used for testing. If you prefer to test locally, use the following:

```bash
export TEST_DATABASE_URL="sqlite:///./test.db"
```

### Step 5: Run Database Migrations

To set up the database tables and apply schema changes:

1. Ensure Alembic is installed:

   ```bash
   pip install alembic
   ```

2. Run the migrations:

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

### Step 8: Run Tests

Use `pytest` to run the test suite and verify the functionality:

```bash
pytest
```

### Reset Database

To reset the database for testing or debugging:

```bash
alembic downgrade base
alembic upgrade head
```

---

## Contributing

We welcome contributions to the TUDU application! Please follow these steps:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and test thoroughly.
4. Submit a pull request with a clear description of your changes.
