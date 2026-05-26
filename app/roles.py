from enum import Enum

class EmployeeRole(str, Enum):
    EMPLOYEE = "Pracownik"
    ASSISTANT = "Podlesniczy"
    FORESTER = "Lesniczy"
    CHIEF = "Nadlesniczy"
    DIRECTOR = "Dyrektor"
    ADMIN = "Administrator"
