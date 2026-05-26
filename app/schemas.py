from app.roles import EmployeeRole
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict

class KafkaEvent(BaseModel):
    event_type: str
    payload: Dict[str, Any]

class EmployeeCreate(BaseModel):
    auth_id: str
    role: EmployeeRole
    manager_id: Optional[int] = None

class EmployeeResponse(BaseModel):
    id: int
    auth_id: str
    role: EmployeeRole
    status: str
    manager_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class EmployeeHierarchyResponse(EmployeeResponse):
    subordinates: List['EmployeeHierarchyResponse'] = []
