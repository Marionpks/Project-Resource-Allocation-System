# Project Resource Allocation System

A clean and simple web application for managing employee allocations to projects.

## Project Structure

```
Project-Resource-Allocation-System/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── database.py      # Database configuration
│   └── models.py        # SQLAlchemy models
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── styles.css       # Styling
│   └── app.js           # JavaScript logic
├── tests/
│   ├── conftest.py      # Pytest configuration
│   └── test_api.py      # API tests
├── proj/                # Virtual environment
├── requirements.txt     # Python dependencies
└── README.md
```

## Features

- **Employee Management**: Add and view employees with their skills and available hours
- **Project Management**: Create and track projects with duration and skill requirements
- **Resource Allocation**: Allocate employees to projects with hour-based tracking
- **Validation**: Prevents over-allocation (max 100 hours per employee)
- **Clean UI**: Modern, responsive interface with tabbed navigation

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Database**: SQLite
- **Testing**: Pytest

## Setup Instructions

### 1. Activate Virtual Environment

```powershell
.\proj\Scripts\Activate.ps1
```

### 2. Install Dependencies (if not already installed)

```powershell
pip install -r requirements.txt
```

### 3. Run the Backend Server

```powershell
cd backend
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 4. Open the Frontend

Open `frontend/index.html` in your web browser, or use a simple HTTP server:

```powershell
cd frontend
python -m http.server 8080
```

Then navigate to: `http://localhost:8080/index.html`

### 5. Run Tests

```powershell
pytest tests/
```

## API Endpoints

### Employees
- `POST /create_employee` - Create a new employee
- `GET /read_employees` - Get all employees
- `PUT /update_employee/{employee_id}` - Update employee
- `DELETE /delete_employee/{employee_id}` - Delete employee

### Projects
- `POST /create_project` - Create a new project
- `GET /read_projects` - Get all projects
- `PUT /update_project/{project_id}` - Update project
- `DELETE /delete_project/{project_id}` - Delete project

### Allocations
- `POST /create_allocation` - Create a new allocation
- `GET /read_allocations` - Get all allocations
- `GET /read_allocations_detailed` - Get detailed allocation info
- `PUT /update_allocation/{allocation_id}` - Update allocation
- `DELETE /delete_allocation/{allocation_id}` - Delete allocation

## Backend Improvements Made

1. **CORS Support**: Added CORS middleware for frontend-backend communication
2. **Input Validation**: Added Pydantic Field validators for data integrity
3. **Error Handling**: Comprehensive try-catch blocks with meaningful error messages
4. **Status Codes**: Proper HTTP status codes (201 for creation, 404 for not found, etc.)
5. **Database Rollback**: Added rollback on errors to maintain database consistency
6. **Better Logic**: Improved allocation checking logic (removed redundant hour check in duplicate detection)
7. **Code Formatting**: Consistent spacing and PEP 8 compliance

## Database Schema

### EmployeeDB
- `employee_id` (Primary Key)
- `employee_name`
- `skilled_language`
- `available_hrs`

### ProjectDB
- `project_id` (Primary Key)
- `project_name`
- `project_duration`
- `project_skill_required`

### AllocationDB
- `allocation_id` (Primary Key)
- `employee_id` (Foreign Key)
- `project_id` (Foreign Key)
- `allocation_hours`

## Usage Notes

- Allocation hours are limited to 1-100 per allocation
- An employee cannot be allocated more than 100 total hours across all projects
- Each employee-project pair can only have one allocation
- All fields are required when creating records
- Skills must match between employee and project for allocation
- Employee/Project cannot be deleted if they have active allocations

## Testing

The test suite includes:
- Basic CRUD operations for employees, projects, and allocations
- Validation tests (duplicate entries, skill mismatch, hour limits)
- Edge cases (exceeding 100 hours, deleting with dependencies)
- All tests use isolated test database

Run tests with: `pytest tests/ -v`


Made by ~Chriss , ~Marion & ~Aswathy.