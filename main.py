import asyncio
from typing import List
from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db, Employee
from app.consumer import KafkaEventConsumer
from app.producer import kafka_producer
from app.roles import EmployeeRole
from app.schemas import EmployeeCreate, EmployeeHierarchyResponse, EmployeeResponse

consumer = KafkaEventConsumer();

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all);
    
    await kafka_producer.start();
    consumer_task = asyncio.create_task(consumer.start());
    
    yield;
    
    consumer_task.cancel();
    await kafka_producer.stop();

app = FastAPI(lifespan=lifespan);

@app.get("/health")
async def health():
    return {"status": "ok"};

@app.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate, 
    x_user_role: str = Header(None), 
    db: AsyncSession = Depends(get_db)
):
    if x_user_role not in [EmployeeRole.ADMIN.value, EmployeeRole.DIRECTOR.value, EmployeeRole.CHIEF.value]:
        raise HTTPException(status_code=403, detail="No permissions to create an employee");

    new_employee = Employee(
        auth_id=employee_data.auth_id,
        role=employee_data.role,
        manager_id=employee_data.manager_id
    );
    db.add(new_employee);
    await db.commit();
    await db.refresh(new_employee);

    await kafka_producer.send_event(
        event_type="EmployeeProfileCreated",
        payload={"employee_id": new_employee.id, "auth_id": new_employee.auth_id, "role": new_employee.role}
    );

    return new_employee;

@app.get("/employees/{employee_id}/hierarchy", response_model=EmployeeHierarchyResponse)
async def get_employee_hierarchy(
    employee_id: int, 
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Employee)
        .where(Employee.id == employee_id)
        .options(selectinload(Employee.subordinates))
    );
    result = await db.execute(stmt);
    employee = result.scalar_one_or_none();

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found");

    return employee;

@app.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Employee);
    result = await db.execute(stmt);
    employees = result.scalars().all();
    
    return employees;

@app.patch("/employees/{employee_id}/transfer-director", response_model=EmployeeResponse)
async def transfer_director_role(
    employee_id: int,
    x_user_role: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if x_user_role != EmployeeRole.ADMIN.value:
        raise HTTPException(
            status_code=403, 
            detail="Only admin can transfer directors"
        );

    stmt_old_director = select(Employee).where(Employee.role == "Dyrektor");
    result_old = await db.execute(stmt_old_director);
    old_directors = result_old.scalars().all();
    
    for old_dir in old_directors:
        old_dir.role = EmployeeRole.EMPLOYEE.value;

    stmt_new_director = select(Employee).where(Employee.id == employee_id);
    result_new = await db.execute(stmt_new_director);
    new_director = result_new.scalar_one_or_none();

    if not new_director:
        raise HTTPException(
            status_code=404, 
            detail="Employee not found"
        );

    new_director.role = EmployeeRole.DIRECTOR.value;
    
    await db.commit();
    await db.refresh(new_director);

    return new_director;

@app.patch("/employees/{employee_id}/deactivate", response_model=EmployeeResponse)
async def deactivate_employee(
    employee_id: int,
    x_user_role: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if x_user_role != EmployeeRole.ADMIN.value:
        raise HTTPException(
            status_code=403, 
            detail="Only admin can deactive employee accounts"
        );

    stmt = select(Employee).where(Employee.id == employee_id);
    result = await db.execute(stmt);
    employee = result.scalar_one_or_none();

    if not employee:
        raise HTTPException(
            status_code=404, 
            detail="Employee not found"
        );

    employee.status = "DEACTIVATED";
    
    await db.commit();
    await db.refresh(employee);

    return employee;
