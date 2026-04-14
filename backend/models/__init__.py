"""
__init__.py for models package — imports all models so Base.metadata knows about them.
"""
from models.user import User
from models.hcm import Employee, Attendance, Payroll, Performance
from models.finance import Expense, Revenue
from models.procurement import Vendor, PurchaseOrder, InventoryItem
from models.ppm import Project, Task
from models.crm import Customer, Lead, Sale

__all__ = [
    "User",
    "Employee", "Attendance", "Payroll", "Performance",
    "Expense", "Revenue",
    "Vendor", "PurchaseOrder", "InventoryItem",
    "Project", "Task",
    "Customer", "Lead", "Sale",
]
