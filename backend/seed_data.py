"""
Seed Data — populates the database with sample data for all modules.
Run:  python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, time, timedelta
import random

from database import engine, SessionLocal, Base
from models import *  # noqa — registers all models with Base
from auth.password import hash_password


def seed():
    """Create tables and populate with sample data."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ── Users ────────────────────────────────────────────────────────
        # ── Users ────────────────────────────────────────────────────────
        demo_users = [
            ("admin", "admin@startup.com", "admin123", "System Admin", "admin"),
            ("manager", "manager@startup.com", "manager123", "Jane Manager", "manager"),
            ("employee", "employee@startup.com", "employee123", "John Worker", "employee"),
        ]
        
        for uname, email, pwd, fname, role in demo_users:
            if not db.query(User).filter(User.username == uname).first():
                new_user = User(
                    username=uname, email=email,
                    hashed_password=hash_password(pwd),
                    full_name=fname, role=role
                )
                db.add(new_user)
                print(f"[OK] Created user: {uname}")
        
        db.commit()

        # ── Employees ────────────────────────────────────────────────────
        if db.query(Employee).count() == 0:
            departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
            positions = {
                "Engineering": ["Software Engineer", "Senior Developer", "Tech Lead", "DevOps Engineer"],
                "Marketing": ["Marketing Manager", "Content Strategist", "SEO Specialist", "Growth Hacker"],
                "Sales": ["Sales Rep", "Account Executive", "Sales Manager", "BDR"],
                "HR": ["HR Manager", "Recruiter", "People Ops", "HR Coordinator"],
                "Finance": ["Accountant", "Financial Analyst", "Controller", "Bookkeeper"],
                "Operations": ["Ops Manager", "Project Coordinator", "Office Manager", "Admin Assistant"],
            }
            first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
                           "Ivy", "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia", "Paul",
                           "Quinn", "Ryan", "Sarah", "Tom", "Uma", "Victor", "Wendy", "Xavier"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                          "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor"]

            employees = []
            for i in range(24):
                dept = departments[i % len(departments)]
                emp = Employee(
                    employee_code=f"EMP{i+1:04d}",
                    first_name=first_names[i],
                    last_name=random.choice(last_names),
                    email=f"{first_names[i].lower()}.{random.choice(last_names).lower()}@startup.com",
                    phone=f"+1-555-{random.randint(1000, 9999)}",
                    department=dept,
                    position=random.choice(positions[dept]),
                    salary=random.uniform(45000, 120000).__round__(2),
                    hire_date=date(2023, 1, 1) + timedelta(days=random.randint(0, 800)),
                    is_active=True,
                )
                employees.append(emp)
            db.add_all(employees)
            db.commit()
            print(f"[OK] {len(employees)} Employees created")

            # ── Attendance ───────────────────────────────────────────────
            attendance = []
            for emp in employees[:15]:
                for day_offset in range(30):
                    d = date(2026, 3, 1) + timedelta(days=day_offset)
                    if d.weekday() >= 5:  # skip weekends
                        continue
                    status = random.choices(
                        ["present", "present", "present", "late", "absent", "leave"],
                        weights=[50, 30, 10, 5, 3, 2],
                    )[0]
                    check_in = time(9, random.randint(0, 30)) if status != "absent" else None
                    check_out = time(17, random.randint(0, 45)) if status != "absent" else None
                    attendance.append(Attendance(
                        employee_id=emp.id, date=d,
                        check_in=check_in, check_out=check_out,
                        status=status,
                    ))
            db.add_all(attendance)
            db.commit()
            print(f"[OK] {len(attendance)} Attendance records created")

            # ── Payroll ──────────────────────────────────────────────────
            payrolls = []
            for emp in employees:
                for month in range(1, 4):  # Jan-Mar 2026
                    deductions = round(emp.salary * 0.08 * random.uniform(0.8, 1.2), 2)
                    bonuses = round(emp.salary * 0.02 * random.uniform(0, 2), 2)
                    net = round(emp.salary - deductions + bonuses, 2)
                    payrolls.append(Payroll(
                        employee_id=emp.id, month=month, year=2026,
                        basic_salary=emp.salary, deductions=deductions,
                        bonuses=bonuses, net_salary=net, paid=True,
                    ))
            db.add_all(payrolls)
            db.commit()
            print(f"[OK] {len(payrolls)} Payroll records created")

            # ── Performance ──────────────────────────────────────────────
            performances = []
            for emp in employees:
                for q in range(1, 5):
                    gm = random.randint(2, 8)
                    gt = random.randint(5, 10)
                    performances.append(Performance(
                        employee_id=emp.id, quarter=q, year=2025,
                        rating=round(random.uniform(2.0, 5.0), 1),
                        goals_met=gm, goals_total=gt,
                        review_notes=f"Q{q} review — {'Excellent' if gm/gt > 0.7 else 'Needs improvement'}",
                        reviewer="manager",
                    ))
            db.add_all(performances)
            db.commit()
            print(f"[OK] {len(performances)} Performance reviews created")

        # ── Finance ──────────────────────────────────────────────────────
        if db.query(Revenue).count() == 0:
            categories = ["payroll", "rent", "marketing", "utilities", "supplies", "other"]
            sources = ["product_sales", "services", "subscriptions", "consulting"]

            revenues = []
            for month in range(1, 13):
                for _ in range(random.randint(3, 8)):
                    revenues.append(Revenue(
                        source=random.choice(sources),
                        amount=round(random.uniform(5000, 50000), 2),
                        date=date(2025, month, random.randint(1, 28)),
                        description=f"Revenue entry for {date(2025, month, 1).strftime('%B')}",
                    ))
            # 2026 data
            for month in range(1, 4):
                for _ in range(random.randint(5, 10)):
                    revenues.append(Revenue(
                        source=random.choice(sources),
                        amount=round(random.uniform(8000, 60000), 2),
                        date=date(2026, month, random.randint(1, 28)),
                        description=f"Revenue entry for {date(2026, month, 1).strftime('%B')} 2026",
                    ))
            db.add_all(revenues)
            db.commit()
            print(f"[OK] {len(revenues)} Revenue records created")

            expenses = []
            for month in range(1, 13):
                for _ in range(random.randint(4, 10)):
                    expenses.append(Expense(
                        category=random.choice(categories),
                        amount=round(random.uniform(500, 15000), 2),
                        date=date(2025, month, random.randint(1, 28)),
                        description=f"Expense for {date(2025, month, 1).strftime('%B')}",
                        approved_by="manager",
                    ))
            for month in range(1, 4):
                for _ in range(random.randint(5, 8)):
                    expenses.append(Expense(
                        category=random.choice(categories),
                        amount=round(random.uniform(1000, 20000), 2),
                        date=date(2026, month, random.randint(1, 28)),
                        description=f"Expense for {date(2026, month, 1).strftime('%B')} 2026",
                        approved_by="manager",
                    ))
            db.add_all(expenses)
            db.commit()
            print(f"[OK] {len(expenses)} Expense records created")

        # ── Procurement ──────────────────────────────────────────────────
        if db.query(Vendor).count() == 0:
            vendors_data = [
                ("TechSupply Co", "tech@supply.com", 4.5),
                ("OfficeMax Pro", "sales@officemax.com", 3.8),
                ("CloudHost Inc", "billing@cloudhost.com", 4.2),
                ("PrintWorld", "orders@printworld.com", 3.5),
                ("Furniture Hub", "info@furniturehub.com", 4.0),
                ("SecureSoft", "sales@securesoft.com", 4.7),
            ]
            vendors = []
            for name, email, rating in vendors_data:
                vendors.append(Vendor(
                    name=name, contact_person=f"{name.split()[0]} Rep",
                    email=email, phone=f"+1-555-{random.randint(1000, 9999)}",
                    address=f"{random.randint(100, 999)} Business Ave",
                    rating=rating,
                ))
            db.add_all(vendors)
            db.commit()

            pos = []
            for i in range(12):
                v = random.choice(vendors)
                status = random.choice(["pending", "approved", "shipped", "delivered"])
                pos.append(PurchaseOrder(
                    po_number=f"PO-2026-{i+1:04d}",
                    vendor_id=v.id,
                    items_description=f"Order #{i+1} items from {v.name}",
                    total_amount=round(random.uniform(500, 25000), 2),
                    status=status,
                    order_date=date(2026, random.randint(1, 3), random.randint(1, 28)),
                    expected_delivery=date(2026, random.randint(3, 6), random.randint(1, 28)),
                ))
            db.add_all(pos)
            db.commit()

            items = [
                ("Laptop", "LAP-001", 15, 1200.00, 5, "electronics"),
                ("Monitor", "MON-001", 20, 350.00, 8, "electronics"),
                ("Keyboard", "KEY-001", 50, 45.00, 15, "peripherals"),
                ("Mouse", "MOU-001", 45, 25.00, 15, "peripherals"),
                ("Desk Chair", "CHR-001", 8, 350.00, 3, "furniture"),
                ("Standing Desk", "DSK-001", 5, 600.00, 2, "furniture"),
                ("Printer Paper", "PAP-001", 100, 8.00, 30, "supplies"),
                ("Ink Cartridge", "INK-001", 12, 35.00, 5, "supplies"),
                ("Webcam", "WEB-001", 18, 80.00, 5, "electronics"),
                ("Headset", "HDS-001", 3, 120.00, 10, "peripherals"),
            ]
            inv_items = []
            for name, sku, qty, price, reorder, cat in items:
                inv_items.append(InventoryItem(
                    name=name, sku=sku, quantity=qty, unit_price=price,
                    reorder_level=reorder, vendor_id=random.choice(vendors).id,
                    category=cat,
                ))
            db.add_all(inv_items)
            db.commit()
            print(f"[OK] {len(vendors)} Vendors, {len(pos)} POs, {len(inv_items)} Inventory items created")

        # ── PPM ──────────────────────────────────────────────────────────
        if db.query(Project).count() == 0:
            projects_data = [
                ("Website Redesign", "Redesign company website with modern UI", "active", "high", 45000, 28000),
                ("Mobile App MVP", "Build mobile app for customers", "active", "critical", 80000, 52000),
                ("CRM Integration", "Integrate Salesforce CRM", "planning", "medium", 30000, 0),
                ("Data Pipeline", "Build real-time analytics pipeline", "active", "high", 60000, 35000),
                ("Security Audit", "Annual security review and fixes", "completed", "critical", 25000, 24000),
                ("HR Portal", "Employee self-service portal", "delayed", "medium", 35000, 38000),
                ("API Platform", "Public API for partners", "planning", "low", 40000, 0),
                ("Cloud Migration", "Migrate infra to AWS", "active", "high", 100000, 65000),
            ]
            projects = []
            for name, desc, status, priority, budget, spent in projects_data:
                projects.append(Project(
                    name=name, description=desc,
                    start_date=date(2025, random.randint(6, 12), 1),
                    end_date=date(2026, random.randint(3, 9), 28),
                    budget=budget, spent=spent,
                    status=status, priority=priority,
                    manager="manager",
                ))
            db.add_all(projects)
            db.commit()

            tasks = []
            task_titles = [
                "Setup project scaffold", "Design wireframes", "Implement authentication",
                "Build API endpoints", "Frontend development", "Database schema design",
                "Write unit tests", "Code review", "Deploy to staging",
                "Performance optimization", "Bug fixes", "Documentation",
                "User testing", "Security review", "Deploy to production",
            ]
            for proj in projects:
                n_tasks = random.randint(4, 8)
                selected = random.sample(task_titles, n_tasks)
                for title in selected:
                    status = random.choice(["todo", "in_progress", "review", "done"])
                    tasks.append(Task(
                        project_id=proj.id, title=title,
                        description=f"{title} for {proj.name}",
                        assignee=random.choice(["Alice", "Bob", "Charlie", "Diana", "Eve"]),
                        status=status,
                        priority=random.choice(["low", "medium", "high"]),
                        due_date=date(2026, random.randint(3, 8), random.randint(1, 28)),
                    ))
            db.add_all(tasks)
            db.commit()
            print(f"[OK] {len(projects)} Projects, {len(tasks)} Tasks created")

        # ── CRM ──────────────────────────────────────────────────────────
        if db.query(Customer).count() == 0:
            companies = ["TechCorp", "DataFlow", "CloudNine", "StartupXYZ", "DigitalEdge",
                         "InnovateLab", "PixelPerfect", "ByteWorks", "ScaleUp", "MegaGrowth",
                         "SmartSolutions", "FutureForward", "RapidDev", "CoreTech", "NextGen"]
            segments = ["enterprise", "smb", "startup", "individual"]

            customers = []
            for i, company in enumerate(companies):
                customers.append(Customer(
                    name=f"{company} Inc.",
                    email=f"contact@{company.lower()}.com",
                    phone=f"+1-555-{random.randint(1000, 9999)}",
                    company=company,
                    segment=random.choice(segments),
                    lifetime_value=round(random.uniform(5000, 200000), 2),
                ))
            db.add_all(customers)
            db.commit()

            leads = []
            lead_sources = ["website", "referral", "social", "ads", "cold_call"]
            lead_statuses = ["new", "contacted", "qualified", "proposal", "converted", "lost"]
            for i in range(25):
                cust = random.choice(customers) if random.random() > 0.3 else None
                leads.append(Lead(
                    customer_id=cust.id if cust else None,
                    contact_name=f"Lead Contact {i+1}",
                    contact_email=f"lead{i+1}@example.com",
                    source=random.choice(lead_sources),
                    status=random.choice(lead_statuses),
                    estimated_value=round(random.uniform(1000, 50000), 2),
                    notes=f"Lead #{i+1} from {random.choice(lead_sources)}",
                ))
            db.add_all(leads)
            db.commit()

            sales = []
            products = ["SaaS License", "Consulting", "Support Plan", "Custom Dev", "Training"]
            for _ in range(40):
                cust = random.choice(customers)
                sales.append(Sale(
                    customer_id=cust.id,
                    amount=round(random.uniform(1000, 30000), 2),
                    date=date(2025, random.randint(1, 12), random.randint(1, 28)),
                    product_description=random.choice(products),
                    payment_status=random.choice(["paid", "paid", "paid", "pending", "overdue"]),
                ))
            # 2026 sales
            for _ in range(15):
                cust = random.choice(customers)
                sales.append(Sale(
                    customer_id=cust.id,
                    amount=round(random.uniform(2000, 40000), 2),
                    date=date(2026, random.randint(1, 3), random.randint(1, 28)),
                    product_description=random.choice(products),
                    payment_status=random.choice(["paid", "pending"]),
                ))
            db.add_all(sales)
            db.commit()
            print(f"[OK] {len(customers)} Customers, {len(leads)} Leads, {len(sales)} Sales created")

        print("\n[DONE] Seed data complete!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
