from app.database import AsyncSessionLocal, Employee
from sqlalchemy import update

async def handle_account_activated(event):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Employee).where(Employee.auth_id == event.payload['auth_id']).values(status="ACTIVE")
        );
        await session.commit();

async def handle_activation_expired(event):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Employee).where(Employee.auth_id == event.payload['auth_id']).values(status="EXPIRED")
        );
        await session.commit();

EVENT_HANDLER_MAP = {
    "EmployeeAccountActivated": handle_account_activated,
    "EmployeeActivationExpired": handle_activation_expired,
};

async def route_event(event):
    handler = EVENT_HANDLER_MAP.get(event.event_type);
    if handler:
        await handler(event);
    else:
        print(f"Ignoring event: {event.event_type}");
