from database import base ,engine

from sqlalchemy import Column , String , Integer ,ForeignKey

class EmployeeDB(base):
    __tablename__="employeedb"
    employee_id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    employee_name=Column(String)
    skilled_language=Column(String)
    available_hrs=Column(Integer)

class ProjectDB(base):
    __tablename__="projectdb"
    project_id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    project_name=Column(String)
    project_duration=Column(Integer)
    project_skill_required=Column(String)

class AllocationDB(base):
    __tablename__="allocationdb"
    allocation_id=Column(Integer, primary_key=True , index=True , autoincrement=True)
    project_id=Column(Integer,ForeignKey(ProjectDB.project_id))
    employee_id=Column(Integer,ForeignKey(EmployeeDB.employee_id))
    allocation_hours=Column(Integer,default=0)
