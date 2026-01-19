import sys
sys.path.append('../backend')

from fastapi.testclient import TestClient
from main import app
from database import base, engine
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    base.metadata.create_all(bind=engine)
    yield
    base.metadata.drop_all(bind=engine)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()

def test_create_employee():
    employee_data = {
        "employee_name": "John Doe",
        "skilled_language": "Python",
        "available_hrs": 40
    }
    response = client.post("/create_employee", json=employee_data)
    assert response.status_code == 201
    data = response.json()
    assert data["employee_name"] == "John Doe"
    assert data["skilled_language"] == "Python"
    assert "employee_id" in data

def test_create_duplicate_employee():
    employee_data = {
        "employee_name": "Jane Smith",
        "skilled_language": "Java",
        "available_hrs": 35
    }
    client.post("/create_employee", json=employee_data)
    response = client.post("/create_employee", json=employee_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_read_employees():
    employee_data = {
        "employee_name": "Alice",
        "skilled_language": "JavaScript",
        "available_hrs": 30
    }
    client.post("/create_employee", json=employee_data)
    response = client.get("/read_employees")
    assert response.status_code == 200
    employees = response.json()
    assert len(employees) == 1
    assert employees[0]["employee_name"] == "Alice"

def test_create_project():
    project_data = {
        "project_name": "Web App",
        "project_duration": 100,
        "project_skill_required": "Python"
    }
    response = client.post("/create_project", json=project_data)
    assert response.status_code == 201
    data = response.json()
    assert data["project_name"] == "Web App"
    assert "project_id" in data

def test_read_projects():
    project_data = {
        "project_name": "Mobile App",
        "project_duration": 80,
        "project_skill_required": "React"
    }
    client.post("/create_project", json=project_data)
    response = client.get("/read_projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1

def test_create_allocation():
    employee_data = {
        "employee_name": "Bob",
        "skilled_language": "Python",
        "available_hrs": 50
    }
    emp_response = client.post("/create_employee", json=employee_data)
    emp_id = emp_response.json()["employee_id"]
    
    project_data = {
        "project_name": "API Development",
        "project_duration": 60,
        "project_skill_required": "Python"
    }
    proj_response = client.post("/create_project", json=project_data)
    proj_id = proj_response.json()["project_id"]
    
    allocation_data = {
        "employee_id": emp_id,
        "project_id": proj_id,
        "allocation_hours": 30
    }
    response = client.post("/create_allocation", json=allocation_data)
    assert response.status_code == 201
    data = response.json()
    assert data["allocation_hours"] == 30

def test_skill_mismatch():
    employee_data = {
        "employee_name": "Charlie",
        "skilled_language": "Java",
        "available_hrs": 40
    }
    emp_response = client.post("/create_employee", json=employee_data)
    emp_id = emp_response.json()["employee_id"]
    
    project_data = {
        "project_name": "Python Project",
        "project_duration": 50,
        "project_skill_required": "Python"
    }
    proj_response = client.post("/create_project", json=project_data)
    proj_id = proj_response.json()["project_id"]
    
    allocation_data = {
        "employee_id": emp_id,
        "project_id": proj_id,
        "allocation_hours": 20
    }
    response = client.post("/create_allocation", json=allocation_data)
    assert response.status_code == 400
    assert "Skill mismatch" in response.json()["detail"]

def test_update_employee():
    employee_data = {
        "employee_name": "David",
        "skilled_language": "C++",
        "available_hrs": 45
    }
    response = client.post("/create_employee", json=employee_data)
    emp_id = response.json()["employee_id"]
    
    updated_data = {
        "employee_name": "David Updated",
        "skilled_language": "C++",
        "available_hrs": 50
    }
    update_response = client.put(f"/update_employee/{emp_id}", json=updated_data)
    assert update_response.status_code == 200
    assert update_response.json()["employee_name"] == "David Updated"
    assert update_response.json()["available_hrs"] == 50

def test_delete_employee():
    employee_data = {
        "employee_name": "Eve",
        "skilled_language": "Ruby",
        "available_hrs": 35
    }
    response = client.post("/create_employee", json=employee_data)
    emp_id = response.json()["employee_id"]
    
    delete_response = client.delete(f"/delete_employee/{emp_id}")
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"]
    
    get_response = client.get("/read_employees")
    assert len(get_response.json()) == 0

def test_delete_project():
    project_data = {
        "project_name": "Test Project",
        "project_duration": 40,
        "project_skill_required": "Go"
    }
    response = client.post("/create_project", json=project_data)
    proj_id = response.json()["project_id"]
    
    delete_response = client.delete(f"/delete_project/{proj_id}")
    assert delete_response.status_code == 200
    
    get_response = client.get("/read_projects")
    assert len(get_response.json()) == 0

def test_allocation_exceeds_100_hours():
    employee_data = {
        "employee_name": "Frank",
        "skilled_language": "Python",
        "available_hrs": 100
    }
    emp_response = client.post("/create_employee", json=employee_data)
    emp_id = emp_response.json()["employee_id"]
    
    project1_data = {
        "project_name": "Project A",
        "project_duration": 200,
        "project_skill_required": "Python"
    }
    proj1_response = client.post("/create_project", json=project1_data)
    proj1_id = proj1_response.json()["project_id"]
    
    project2_data = {
        "project_name": "Project B",
        "project_duration": 200,
        "project_skill_required": "Python"
    }
    proj2_response = client.post("/create_project", json=project2_data)
    proj2_id = proj2_response.json()["project_id"]
    
    allocation1_data = {
        "employee_id": emp_id,
        "project_id": proj1_id,
        "allocation_hours": 60
    }
    client.post("/create_allocation", json=allocation1_data)
    
    allocation2_data = {
        "employee_id": emp_id,
        "project_id": proj2_id,
        "allocation_hours": 50
    }
    response = client.post("/create_allocation", json=allocation2_data)
    assert response.status_code == 400
    assert "exceeds 100 hours" in response.json()["detail"]
