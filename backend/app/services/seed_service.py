from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.people import Gender, Guardian, Student, Teacher
from app.models.user import User, UserRole
from app.utils.auth_utils import hash_password

DEMO_PASSWORD = "demo123"

DEMO_USERS: list[dict] = [
    {
        "email": "admin@school.com",
        "password": "admin123",
        "first_name": "Super",
        "last_name": "Admin",
        "role": UserRole.super_admin,
    },
    {
        "email": "principal@school.com",
        "password": DEMO_PASSWORD,
        "first_name": "School",
        "last_name": "Principal",
        "role": UserRole.admin,
    },
    {
        "email": "finance@school.com",
        "password": DEMO_PASSWORD,
        "first_name": "Fee",
        "last_name": "Accountant",
        "role": UserRole.accountant,
    },
    {
        "email": "parent@school.com",
        "password": DEMO_PASSWORD,
        "first_name": "John",
        "last_name": "Parent",
        "phone": "+1-555-0100",
        "role": UserRole.parent,
    },
]


class SeedService:
    @staticmethod
    async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def _ensure_user(db: AsyncSession, spec: dict) -> User | None:
        if await SeedService._get_user_by_email(db, spec["email"]):
            return None

        user = User(
            email=spec["email"],
            password_hash=hash_password(spec["password"]),
            first_name=spec["first_name"],
            last_name=spec["last_name"],
            phone=spec.get("phone"),
            role=spec["role"],
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def _ensure_teacher(db: AsyncSession) -> None:
        email = "teacher@school.com"
        if await SeedService._get_user_by_email(db, email):
            return

        user = User(
            email=email,
            password_hash=hash_password(DEMO_PASSWORD),
            first_name="Sarah",
            last_name="Johnson",
            phone="+1-555-0200",
            role=UserRole.teacher,
        )
        db.add(user)
        await db.flush()

        result = await db.execute(select(func.count(Teacher.id)))
        count = result.scalar() or 0

        teacher = Teacher(
            user_id=user.id,
            employee_id=f"EMP{count + 1:05d}",
            department="Mathematics",
            qualification="M.Sc. Mathematics",
            joining_date=date(2024, 6, 1),
            address="123 School Lane",
        )
        db.add(teacher)

    @staticmethod
    async def _ensure_student(db: AsyncSession) -> None:
        email = "student@school.com"
        if await SeedService._get_user_by_email(db, email):
            return

        user = User(
            email=email,
            password_hash=hash_password(DEMO_PASSWORD),
            first_name="Alex",
            last_name="Student",
            role=UserRole.student,
        )
        db.add(user)
        await db.flush()

        result = await db.execute(select(func.count(Student.id)))
        count = result.scalar() or 0

        student = Student(
            user_id=user.id,
            admission_no=f"ADM{count + 1:05d}",
            date_of_birth=date(2012, 3, 15),
            gender=Gender.male,
            blood_group="O+",
            address="456 Student Ave",
            admission_date=date(2024, 8, 1),
        )
        db.add(student)
        await db.flush()

        guardian = Guardian(
            student_id=student.id,
            name="John Parent",
            relationship_type="father",
            phone="+1-555-0100",
            email="parent@school.com",
            occupation="Engineer",
            is_primary=True,
        )
        db.add(guardian)

    @staticmethod
    async def seed_all(db: AsyncSession) -> None:
        """Seed demo users for every RBAC role (idempotent)."""
        for spec in DEMO_USERS:
            await SeedService._ensure_user(db, spec)

        await SeedService._ensure_teacher(db)
        await SeedService._ensure_student(db)
        await db.commit()
