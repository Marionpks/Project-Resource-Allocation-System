from database import engine, base, sessionlocal
from models import EmployeeDB, ProjectDB, AllocationDB
from sqlalchemy.orm import Session 
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func

app = FastAPI(title="Project Resource Allocation System")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base.metadata.create_all(bind=engine)

def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()

class EmployeeBase(BaseModel):
    employee_name: str = Field(..., min_length=1, max_length=100)
    skilled_language: str = Field(..., min_length=1, max_length=100)
    available_hrs: int = Field(..., ge=0, description="Available hours must be non-negative")

    class Config:
        from_attributes = True

class EmployeeCreate(EmployeeBase):
    pass 

class EmployeeResponse(EmployeeBase):
    employee_id: int 


class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    project_duration: int = Field(..., gt=0, description="Duration must be positive")
    project_skill_required: str = Field(..., min_length=1, max_length=100)

    class Config:
        from_attributes = True

class ProjectCreate(ProjectBase):
    pass 

class ProjectResponse(ProjectBase):
    project_id: int 


class AllocationBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    project_id: int = Field(..., gt=0)
    allocation_hours: int = Field(..., ge=1, le=100, description="Allocation hours must be between 1 and 100")

    class Config:
        from_attributes = True

class AllocationCreate(AllocationBase):
    pass 

class AllocationResponse(AllocationBase):
    allocation_id: int 


class AllocationDetailResponse(BaseModel):
    allocation_id: int
    employee_id: int
    employee_name: str
    employee_skills: str
    project_id: int
    project_name: str
    project_skills_required: str
    allocation_hours: int
    total_employee_hours: int
    remaining_hours: int

    class Config:
        from_attributes = True


@app.get('/')
def root():
    return f"Welcome to project resource allocation system"


@app.post('/create_employee', response_model=EmployeeResponse, status_code=201)
def create_employee(item: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        # Check for duplicate employee name
        existing = db.query(EmployeeDB).filter(
            EmployeeDB.employee_name == item.employee_name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Employee with name '{item.employee_name}' already exists"
            )
        
        db_item = EmployeeDB(
            employee_name=item.employee_name,
            skilled_language=item.skilled_language,
            available_hrs=item.available_hrs
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

@app.get('/read_employees', response_model=list[EmployeeResponse])
def read_employees(db: Session = Depends(get_db)):
    try:
        return db.query(EmployeeDB).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employees: {str(e)}")



@app.post('/create_project', response_model=ProjectResponse, status_code=201)
def create_project(item: ProjectCreate, db: Session = Depends(get_db)):
    try:
        # Check for duplicate project name
        existing = db.query(ProjectDB).filter(
            ProjectDB.project_name == item.project_name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Project with name '{item.project_name}' already exists"
            )
        
        db_item = ProjectDB(
            project_name=item.project_name,
            project_duration=item.project_duration,
            project_skill_required=item.project_skill_required
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@app.get('/read_projects', response_model=list[ProjectResponse])
def read_projects(db: Session = Depends(get_db)):
    try:
        return db.query(ProjectDB).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")


@app.post('/create_allocation', response_model=AllocationResponse, status_code=201)
def create_allocation(item: AllocationCreate, db: Session = Depends(get_db)):
    try:
        # Verify employee exists
        employee = db.query(EmployeeDB).filter(
            EmployeeDB.employee_id == item.employee_id
        ).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Verify project exists
        project = db.query(ProjectDB).filter(
            ProjectDB.project_id == item.project_id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check skill match
        if not (employee.skilled_language.lower() in project.project_skill_required.lower() or 
                project.project_skill_required.lower() in employee.skilled_language.lower()):
            raise HTTPException(
                status_code=400,
                detail=f"Skill mismatch: Employee has '{employee.skilled_language}' but project requires '{project.project_skill_required}'"
            )

        # Check for duplicate allocation
        existing = db.query(AllocationDB).filter(
            AllocationDB.employee_id == item.employee_id,
            AllocationDB.project_id == item.project_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Employee is already allocated to this project with {existing.allocation_hours} hours"
            )

        # Check total allocation doesn't exceed 100 hours
        total_allocated = db.query(AllocationDB).filter(
            AllocationDB.employee_id == item.employee_id
        ).with_entities(func.sum(AllocationDB.allocation_hours)).scalar() or 0

        if total_allocated + item.allocation_hours > 100:
            raise HTTPException(
                status_code=400,
                detail=f"Employee allocation exceeds 100 hours. Currently allocated: {total_allocated} hours"
            )

        # Check if employee has enough available hours
        if total_allocated + item.allocation_hours > employee.available_hrs:
            raise HTTPException(
                status_code=400,
                detail=f"Employee only has {employee.available_hrs} hours available. Already allocated: {total_allocated} hours"
            )

        # Check if project has enough duration for this allocation
        project_total_allocated = db.query(AllocationDB).filter(
            AllocationDB.project_id == item.project_id
        ).with_entities(func.sum(AllocationDB.allocation_hours)).scalar() or 0

        if project_total_allocated + item.allocation_hours > project.project_duration:
            raise HTTPException(
                status_code=400,
                detail=f"Project '{project.project_name}' only has {project.project_duration} hours. Already allocated: {project_total_allocated} hours to other employees"
            )

        # Create allocation
        db_item = AllocationDB(
            project_id=item.project_id,
            employee_id=item.employee_id,
            allocation_hours=item.allocation_hours
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create allocation: {str(e)}")


@app.get('/read_allocations', response_model=list[AllocationResponse])
def read_allocations(db: Session = Depends(get_db)):
    try:
        return db.query(AllocationDB).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve allocations: {str(e)}")


@app.get('/read_allocations_detailed', response_model=list[AllocationDetailResponse])
def read_allocations_detailed(db: Session = Depends(get_db)):
    try:
        allocations = db.query(
            AllocationDB.allocation_id,
            AllocationDB.employee_id,
            EmployeeDB.employee_name,
            EmployeeDB.skilled_language.label('employee_skills'),
            AllocationDB.project_id,
            ProjectDB.project_name,
            ProjectDB.project_skill_required.label('project_skills_required'),
            AllocationDB.allocation_hours
        ).join(
            EmployeeDB, AllocationDB.employee_id == EmployeeDB.employee_id
        ).join(
            ProjectDB, AllocationDB.project_id == ProjectDB.project_id
        ).all()

        result = []
        for alloc in allocations:
            # Calculate total hours for this employee
            total_hours = db.query(AllocationDB).filter(
                AllocationDB.employee_id == alloc.employee_id
            ).with_entities(func.sum(AllocationDB.allocation_hours)).scalar() or 0

            result.append({
                'allocation_id': alloc.allocation_id,
                'employee_id': alloc.employee_id,
                'employee_name': alloc.employee_name,
                'employee_skills': alloc.employee_skills,
                'project_id': alloc.project_id,
                'project_name': alloc.project_name,
                'project_skills_required': alloc.project_skills_required,
                'allocation_hours': alloc.allocation_hours,
                'total_employee_hours': total_hours,
                'remaining_hours': 100 - total_hours
            })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve detailed allocations: {str(e)}")


# Update endpoints
@app.put('/update_employee/{employee_id}', response_model=EmployeeResponse)
def update_employee(employee_id: int, item: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if new name conflicts with another employee
        if item.employee_name != employee.employee_name:
            existing = db.query(EmployeeDB).filter(
                EmployeeDB.employee_name == item.employee_name,
                EmployeeDB.employee_id != employee_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Employee with name '{item.employee_name}' already exists")
        
        employee.employee_name = item.employee_name
        employee.skilled_language = item.skilled_language
        employee.available_hrs = item.available_hrs
        
        db.commit()
        db.refresh(employee)
        return employee
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {str(e)}")


@app.put('/update_project/{project_id}', response_model=ProjectResponse)
def update_project(project_id: int, item: ProjectCreate, db: Session = Depends(get_db)):
    try:
        project = db.query(ProjectDB).filter(ProjectDB.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if new name conflicts with another project
        if item.project_name != project.project_name:
            existing = db.query(ProjectDB).filter(
                ProjectDB.project_name == item.project_name,
                ProjectDB.project_id != project_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Project with name '{item.project_name}' already exists")
        
        project.project_name = item.project_name
        project.project_duration = item.project_duration
        project.project_skill_required = item.project_skill_required
        
        db.commit()
        db.refresh(project)
        return project
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@app.put('/update_allocation/{allocation_id}', response_model=AllocationResponse)
def update_allocation(allocation_id: int, item: AllocationCreate, db: Session = Depends(get_db)):
    try:
        allocation = db.query(AllocationDB).filter(AllocationDB.allocation_id == allocation_id).first()
        if not allocation:
            raise HTTPException(status_code=404, detail="Allocation not found")
        
        # Verify employee exists
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == item.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Verify project exists
        project = db.query(ProjectDB).filter(ProjectDB.project_id == item.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check skill match
        if not (employee.skilled_language.lower() in project.project_skill_required.lower() or 
                project.project_skill_required.lower() in employee.skilled_language.lower()):
            raise HTTPException(
                status_code=400,
                detail=f"Skill mismatch: Employee has '{employee.skilled_language}' but project requires '{project.project_skill_required}'"
            )
        
        # Check for duplicate if employee or project changed
        if allocation.employee_id != item.employee_id or allocation.project_id != item.project_id:
            existing = db.query(AllocationDB).filter(
                AllocationDB.employee_id == item.employee_id,
                AllocationDB.project_id == item.project_id,
                AllocationDB.allocation_id != allocation_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="This employee is already allocated to this project")
        
        # Calculate total hours excluding current allocation
        total_allocated = db.query(AllocationDB).filter(
            AllocationDB.employee_id == item.employee_id,
            AllocationDB.allocation_id != allocation_id
        ).with_entities(func.sum(AllocationDB.allocation_hours)).scalar() or 0
        
        if total_allocated + item.allocation_hours > 100:
            raise HTTPException(
                status_code=400,
                detail=f"Employee allocation exceeds 100 hours. Currently allocated: {total_allocated} hours"
            )
        
        # Check if employee has enough available hours
        if total_allocated + item.allocation_hours > employee.available_hrs:
            raise HTTPException(
                status_code=400,
                detail=f"Employee only has {employee.available_hrs} hours available. Already allocated: {total_allocated} hours"
            )
        
        # Check if project has enough duration for this allocation (excluding current allocation)
        project_total_allocated = db.query(AllocationDB).filter(
            AllocationDB.project_id == item.project_id,
            AllocationDB.allocation_id != allocation_id
        ).with_entities(func.sum(AllocationDB.allocation_hours)).scalar() or 0

        if project_total_allocated + item.allocation_hours > project.project_duration:
            raise HTTPException(
                status_code=400,
                detail=f"Project '{project.project_name}' only has {project.project_duration} hours. Already allocated: {project_total_allocated} hours to other employees"
            )
        
        allocation.employee_id = item.employee_id
        allocation.project_id = item.project_id
        allocation.allocation_hours = item.allocation_hours
        
        db.commit()
        db.refresh(allocation)
        return allocation
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update allocation: {str(e)}")


# Delete endpoints
@app.delete('/delete_employee/{employee_id}')
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if employee has allocations
        allocations = db.query(AllocationDB).filter(AllocationDB.employee_id == employee_id).count()
        if allocations > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete employee. They have {allocations} allocation(s). Delete allocations first."
            )
        
        db.delete(employee)
        db.commit()
        return {"message": f"Employee '{employee.employee_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {str(e)}")


@app.delete('/delete_project/{project_id}')
def delete_project(project_id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(ProjectDB).filter(ProjectDB.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if project has allocations
        allocations = db.query(AllocationDB).filter(AllocationDB.project_id == project_id).count()
        if allocations > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete project. It has {allocations} allocation(s). Delete allocations first."
            )
        
        db.delete(project)
        db.commit()
        return {"message": f"Project '{project.project_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@app.delete('/delete_allocation/{allocation_id}')
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    try:
        allocation = db.query(AllocationDB).filter(AllocationDB.allocation_id == allocation_id).first()
        if not allocation:
            raise HTTPException(status_code=404, detail="Allocation not found")
        
        db.delete(allocation)
        db.commit()
        return {"message": "Allocation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete allocation: {str(e)}")