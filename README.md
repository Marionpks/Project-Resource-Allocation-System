# Project Resource Allocation System

A clean and simple web application for managing employee allocations to projects.

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

## Setup Instructions

### 1. Activate Virtual Environment

```powershell
.\capstone\Scripts\Activate.ps1
```

### 2. Install Dependencies (if not already installed)

```powershell
pip install -r requirements.txt
```

### 3. Run the Backend Server

```powershell
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 4. Open the Frontend

Open `index.html` in your web browser, or use a simple HTTP server:

```powershell
python -m http.server 8080
```

Then navigate to: `http://localhost:8080/index.html`

## API Endpoints

### Employees
- `POST /create_employee` - Create a new employee
- `GET /read_employees` - Get all employees

### Projects
- `POST /create_project` - Create a new project
- `GET /read_projects` - Get all projects

### Allocations
- `POST /create_allocation` - Create a new allocation
- `GET /read_allocations` - Get all allocations

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

## Future Enhancements

- Delete/Update operations
- Search and filter functionality
- Reporting and analytics dashboard
- Export data to CSV/Excel
- User authentication
- Project completion tracking
