import sys
import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import User, Role, Permission
from app.models.newsletter import Newsletter
from app.models.site_content import SiteContent


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SUPER ADMIN CREDENTIALS (edit or override via env)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADMIN_EMAIL      = os.getenv("SEED_ADMIN_EMAIL")
ADMIN_FIRST_NAME = os.getenv("SEED_ADMIN_FIRST_NAME", "Super")
ADMIN_LAST_NAME  = os.getenv("SEED_ADMIN_LAST_NAME", "Admin")
ADMIN_PASSWORD   = os.getenv("SEED_ADMIN_PASSWORD")
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ── Roles ──
ROLES = [
    {"name": "super_admin", "description": "Super Admin"},
    {"name": "author_ce", "description": "Civil Engineering Author"},
    {"name": "author_ee", "description": "Electrical Engineering Author"},
    {"name": "author_it", "description": "Information Technology Author"},
]

# ── Permissions ──
PERMISSIONS = [
    "user.manage",
    "article.create",
    "article.archive",
    "article.approve",
    "article.update",
]

# ── Role → Permission mapping ──
ROLE_PERMISSIONS = {
    "super_admin": PERMISSIONS,
    "author_ce": ["article.create", "article.update"],
    "author_ee": ["article.create", "article.update"],
    "author_it": ["article.create", "article.update"],
}

# ── Users (only super admin — other users created via User Management) ──
USERS = [
    {"email": ADMIN_EMAIL, "first_name": ADMIN_FIRST_NAME, "last_name": ADMIN_LAST_NAME, "role_name": "super_admin"},
]

# ── Site Content Defaults ──
SITE_CONTENT = {
    "home": {
        "collegeSection": {
            "title": "College of Engineering and Information Technology",
            "description": "Our college offers Civil Engineering, Electrical Engineering, and Information Technology programs. Each program is supported by a dedicated student organization:",
        },
        "deanSection": {
            "name": "Engr. Jordan Velasco",
            "photoUrl": "/Engr-Jordan.jpg",
            "description": "Under his guidance, the College continues to uphold its mission of producing future-ready engineers and IT professionals who are equipped to meet the evolving demands of society and industry.",
        },
        "registrarSection": {
            "title": "Registrar's Office",
            "description": "The Registrar's Office maintains academic records, coordinates course registration, and ensures the integrity of academic policies and procedures.",
            "phone": "8352 7000 local 125",
            "email": "registrarsoffice_plv@yahoo.com",
            "location": "Maysan Road corner Tongco Street, Maysan, Valenzuela City, Valenzuela, Philippines",
            "hours": "Monday-Friday, 8:00 AM - 5:00 PM",
            "services": [
                {"id": "1", "title": "Course Registration & Add/Drop"},
                {"id": "2", "title": "Transcript Requests"},
                {"id": "3", "title": "Degree Verification"},
                {"id": "4", "title": "Graduation Processing"},
            ],
        },
    },
    "academics": {
        "aboutCEIT": {
            "description": "The Engineering and Information Technology programs are designed to:",
            "bulletPoints": [
                {"id": "1", "text": "Acquire full understanding of scientific principles and knowledge in their respective fields"},
                {"id": "2", "text": "Develop a high level of competence in engineering and IT methods and applications"},
                {"id": "3", "text": "Communicate effectively and succinctly the results of technical studies (both verbally and in writing)"},
                {"id": "4", "text": "Nurture the desire for continuing professional growth and explore new horizons in technology"},
                {"id": "5", "text": "Imbue graduates with socially and morally sound motivations and principles"},
            ],
        },
        "coreValues": [
            {"id": "1", "text": "Academic Excellence"},
            {"id": "2", "text": "Integrity and Professional Leadership"},
            {"id": "3", "text": "Scholarly Research"},
            {"id": "4", "text": "Commitment to Service"},
            {"id": "5", "text": "Lifelong Learning"},
        ],
        "collegeAim": [
            {"id": "1", "text": "To become the premiere institution of higher learning in Valenzuela City"},
            {"id": "2", "text": "To produce competent and committed engineers and IT professionals"},
            {"id": "3", "text": "To contribute to the development of the City of Valenzuela and the nation"},
        ],
        "academicSupport": [
            {"id": "1", "text": "Engineering seminars and review sessions for graduating students"},
            {"id": "2", "text": "Assessment examinations to monitor board exam readiness"},
            {"id": "3", "text": "Laboratory facilities for hands-on learning"},
            {"id": "4", "text": "Industry linkages and research engagements"},
        ],
        "admission": "ADMISSION REQUIREMENTS\n\u2022 Grade 12 students who are expected to graduate at the end of the Academic Year 2025-2026.\n\u2022 Graduate of Senior High School of the previous Academic Year (2024-2025 and below) who have not enrolled in any colleges or universities.\n\u2022 College Transferee - the applicant must be an incoming zero year level student at the time of application for the PLV.\n\u2022 Alternative Learning System (ALS) or Philippine Education Placement Test (PEPT) completers whose eligibility is equivalent to a Senior High School Graduate as attested on the Certificate of Rating.\n\nPOLICIES & QUALIFICATIONS\n\u2022 The applicant must be a registered voter of Valenzuela City.\n\u2022 One (1) or both biological parents of the applicant must be a registered voter of Valenzuela City.\n\u2022 The applicant must be a Filipino citizen.\n\u2022 The applicant must comply with the Academic Residency Requirements.",
    },
    "administration": {
        "boardOfRegents": {
            "members": [
                {"id": "1", "name": "City Mayor Weslie T. Gatchalian", "position": "Chairman", "photo": ""},
                {"id": "2", "name": "Atty. Danilo L. Concepcion", "position": "Vice-Chairman", "photo": ""},
                {"id": "3", "name": "Dr. Nede\u00f1a C. Torralba", "position": "PLV President", "photo": ""},
                {"id": "4", "name": "Regent Lorena C. Natividad-Borja", "position": "Regent", "photo": ""},
                {"id": "5", "name": "Regent Floro P. Alejo", "position": "Regent", "photo": ""},
                {"id": "6", "name": "Regent Wilfredo E. Cabral", "position": "Regent", "photo": ""},
                {"id": "7", "name": "Regent Angeleca SJ. Villena", "position": "Regent", "photo": ""},
                {"id": "8", "name": "Atty. Allan Roullo Yap", "position": "Member", "photo": ""},
                {"id": "9", "name": "Adelia E. Soriano", "position": "Board Secretary", "photo": ""},
                {"id": "10", "name": "Ulysses Hermogenes C. Aguilar", "position": "Board Treasurer", "photo": ""},
                {"id": "11", "name": "Elizabeth A. Chongco", "position": "Technical Working Group", "photo": ""},
                {"id": "12", "name": "Pia Febes P. Aquino", "position": "Technical Working Group", "photo": ""},
                {"id": "13", "name": "Flocerfida D. Villamar", "position": "Technical Working Group", "photo": ""},
                {"id": "14", "name": "Erlindo C. Dionisio", "position": "Technical Working Group", "photo": ""},
                {"id": "15", "name": "Leonora B. Katalbas", "position": "Technical Working Group", "photo": ""},
                {"id": "16", "name": "Ana Maria C. Fernandez", "position": "Technical Working Group", "photo": ""},
                {"id": "17", "name": "Carolina V. Santiago", "position": "Technical Working Group", "photo": ""},
                {"id": "18", "name": "Lanilyn A. Dero\u00f1a", "position": "Technical Working Group", "photo": ""},
            ],
        },
        "organizationalChart": {
            "members": [
                {"id": "1", "name": "Dr. Nedena C. Torralba", "position": "University President", "photo": "/pres_torralba.png"},
                {"id": "2", "name": "Dr. Michville Rivera", "position": "Vice President for Academic Affairs", "photo": "/vpaa_rivera.png"},
                {"id": "3", "name": "Engr. Jordan N. Velasco", "position": "Dean, College of CEIT", "photo": "/engr_jordan-velasco.png"},
                {"id": "4", "name": "Norie Caunda", "position": "Secretary, College of CEIT", "photo": "/norie_caunda.png"},
                {"id": "5", "name": "Engr. Tirao", "position": "Civil Engineering Department Chairperson", "photo": "/engr_tirao.png"},
                {"id": "6", "name": "Alex Montano", "position": "Electrical Engineering Department Chairperson", "photo": "/alex_monstano.png"},
                {"id": "7", "name": "Kenmar Bernardino", "position": "Information Technology Department Chairperson", "photo": "/kenmar_bernardino.png"},
                {"id": "8", "name": "Engr. Darryl John Bandino", "position": "CE Department Research Coordinator", "photo": "/john-bandino.png"},
                {"id": "9", "name": "Engr. Erica Cruz", "position": "EE Department Research Coordinator", "photo": "/erika_cruz.png"},
                {"id": "10", "name": "Patrick Luis Francisco", "position": "IT Department Research Coordinator", "photo": "/patrick_francisco.png"},
            ],
        },
    },
}

# ── Default newsletter ──
DEFAULT_NEWSLETTER = {
    "title": "Auralis - The Blueprint",
    "volume": "Vol. 5",
    "issue": "Issue 2",
    "month_year": "February 2026",
    "summary": "This issue highlights student achievements, faculty milestones, and key CEIT initiatives.",
    "highlights": "From the Dean's Desk; Regional Quiz Bee; ITlympics Highlights; Industry Partnerships",
    "tags": "CEIT, Engineering, IT",
    "pages": 24,
    "flipbook_url": "https://online.fliphtml5.com/AURALIS2026/dvtm/",
    "is_latest": 1,
}


async def seed_db():
    async with AsyncSessionLocal() as db:
        if not ADMIN_EMAIL or not ADMIN_PASSWORD:
            print("ERROR: SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD env vars are required. Set them and restart.")
            return

        try:
            # ── Roles ──
            for role_data in ROLES:
                existing = (await db.execute(select(Role).filter(Role.name == role_data["name"]))).scalars().first()
                if not existing:
                    db.add(Role(name=role_data["name"], description=role_data["description"]))
                    print(f"  + Role '{role_data['name']}'")
                else:
                    print(f"  = Role '{role_data['name']}' exists")
            await db.commit()

            # ── Permissions ──
            for perm_name in PERMISSIONS:
                existing = (await db.execute(select(Permission).filter(Permission.name == perm_name))).scalars().first()
                if not existing:
                    db.add(Permission(name=perm_name))
                    print(f"  + Permission '{perm_name}'")
                else:
                    print(f"  = Permission '{perm_name}' exists")
            await db.commit()

            # ── Assign permissions to roles ──
            for role_name, perms in ROLE_PERMISSIONS.items():
                role = (await db.execute(
                    select(Role).filter(Role.name == role_name).options(selectinload(Role.permissions))
                )).scalars().first()
                if role:
                    for perm_name in perms:
                        permission = (await db.execute(select(Permission).filter(Permission.name == perm_name))).scalars().first()
                        if permission and permission not in role.permissions:
                            role.permissions.append(permission)
                    await db.commit()

            # ── Users ──
            for user_data in USERS:
                existing = (await db.execute(select(User).filter(User.email == user_data["email"]))).scalars().first()
                if not existing:
                    role = (await db.execute(select(Role).filter(Role.name == user_data["role_name"]))).scalars().first()
                    if role:
                        db.add(User(
                            email=user_data["email"],
                            first_name=user_data["first_name"],
                            last_name=user_data["last_name"],
                            role_id=role.id,
                            hashed_password=get_password_hash(ADMIN_PASSWORD),
                        ))
                        await db.commit()
                        print(f"  + User '{user_data['email']}'")
                else:
                    print(f"  = User '{user_data['email']}' exists")

            # ── Site Content ──
            for page, content in SITE_CONTENT.items():
                existing = (await db.execute(select(SiteContent).filter(SiteContent.page == page))).scalars().first()
                if not existing:
                    db.add(SiteContent(page=page, content=content))
                    print(f"  + SiteContent '{page}'")
                else:
                    print(f"  = SiteContent '{page}' exists")
            await db.commit()

            # ── Newsletter ──
            existing_nl = (await db.execute(select(Newsletter).limit(1))).scalars().first()
            if not existing_nl:
                db.add(Newsletter(**DEFAULT_NEWSLETTER))
                await db.commit()
                print(f"  + Newsletter '{DEFAULT_NEWSLETTER['title']}'")
            else:
                print(f"  = Newsletter already exists")

            print("\nSeeding complete.")

        except Exception as e:
            print(f"Error seeding database: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(seed_db())
