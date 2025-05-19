# Privy Task - Full Stack Application

This is a full-stack application built with FastAPI (Python) backend and React (TypeScript) frontend. The application includes user authentication, database integration with PostgreSQL, and a modern UI built with React and TailwindCSS.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Node.js 20 or higher
- Docker and Docker Compose
- Git
- A modern web browser

## Project Structure

```
.
├── client/             # React frontend application
├── server/             # FastAPI backend application
└── README.md          # This file
```

## Backend Setup

### 1. Environment Setup

First, set up your environment variables:

```bash
cd server
cp .env.example .env
```

Edit the `.env` file with your desired configuration. The file contains the following variables:

```env
POSTGRES_USER=privy_user
POSTGRES_PASSWORD=privy_password
POSTGRES_DB=privy_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Start the Database

The project uses PostgreSQL as the database. You can start it using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- pgAdmin on port 5050 (optional, for database management)

Default credentials:
- Database:
  - User: privy_user
  - Password: privy_password
  - Database: privy_db
- pgAdmin:
  - Email: admin@admin.com
  - Password: admin

### 3. Set Up Python Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Start the Backend Server

```bash
# Start the FastAPI server
python3 run.py
```

The API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Dependencies

```bash
cd client
npm install
```

### 2. Environment Setup

First, set up your environment variables:

```bash
cp .env.example .env
```

Edit the `.env` file with your desired configuration. The file contains the following variables:

### 3. Start the Development Server

```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173`

## Development

- Backend API documentation is available at `http://localhost:8000/docs`
- Frontend development server includes hot-reloading
- Database can be managed through pgAdmin at `http://localhost:5050`

## Building for Production

### Backend

```bash
# In the server directory
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# In the client directory
npm run build
```

The built files will be in the `client/dist` directory.

## Technologies Used

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic for database migrations
- JWT for authentication

### Frontend
- React 18
- TypeScript
- Vite
- React Query
- React Router
- TailwindCSS
- React Hook Form
- Zod for validation

## License

This project is created as a job assignment and is not licensed for public use. 