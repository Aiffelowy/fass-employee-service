from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from app.config import settings
from app.roles import EmployeeRole

engine = create_async_engine(settings.DATABASE_URL, echo=True);
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False);
Base = declarative_base();

class Employee(Base):
    __tablename__ = "employees";

    id = Column(Integer, primary_key=True, index=True);
    auth_id = Column(String, unique=True, index=True, nullable=False);
    role = Column(SQLEnum(EmployeeRole), nullable=False);
    status = Column(String, default="PENDING");
    
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True);
    manager = relationship("Employee", remote_side=[id], backref="subordinates");

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session;
