"""
Seed script for Vaultix database.

Creates:
- 7 users (2 admin, 3 analyst, 2 viewer)
- 8 events (3 major fests + 4 nested sub-events + 1 standalone)
- 42 financial records across events, categories, and 8 months
- 2 soft-deleted records
- 25+ audit log entries

Usage:
    python -m scripts.seed
"""

import asyncio
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.event import Event, EventType
from app.models.financial_record import FinancialRecord, RecordType, RecordCategory
from app.models.audit_log import AuditLog, AuditAction, ResourceType


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...\n")

        # ========== USERS ==========
        faculty = User(
            id=uuid.uuid4(),
            name="Dr. Priya Sharma",
            email="faculty@vaultix.dev",
            password_hash=hash_password("faculty123"),
            role=UserRole.admin,
        )
        treasurer = User(
            id=uuid.uuid4(),
            name="Arjun Mehta",
            email="treasurer@vaultix.dev",
            password_hash=hash_password("treasurer123"),
            role=UserRole.admin,
        )
        secretary = User(
            id=uuid.uuid4(),
            name="Sneha Reddy",
            email="secretary@vaultix.dev",
            password_hash=hash_password("secretary123"),
            role=UserRole.analyst,
        )
        hackathon_lead = User(
            id=uuid.uuid4(),
            name="Rohan Kumar",
            email="hackathon@vaultix.dev",
            password_hash=hash_password("hackathon123"),
            role=UserRole.analyst,
        )
        culturx_lead = User(
            id=uuid.uuid4(),
            name="Ananya Gupta",
            email="culturx@vaultix.dev",
            password_hash=hash_password("culturx123"),
            role=UserRole.analyst,
        )
        core_member = User(
            id=uuid.uuid4(),
            name="Karan Singh",
            email="karan@vaultix.dev",
            password_hash=hash_password("karan123"),
            role=UserRole.viewer,
        )
        sponsor_rep = User(
            id=uuid.uuid4(),
            name="Prateek Joshi",
            email="sponsor@vaultix.dev",
            password_hash=hash_password("sponsor123"),
            role=UserRole.viewer,
        )

        all_users = [faculty, treasurer, secretary, hackathon_lead, culturx_lead, core_member, sponsor_rep]
        db.add_all(all_users)
        await db.flush()
        print(f"  ✓ Created {len(all_users)} users")

        # ========== EVENTS ==========
        # 3 Major fests
        techsurge = Event(
            id=uuid.uuid4(), name="TechSurge 2025", type=EventType.major_fest,
            description="Annual technical fest: hackathons, workshops, coding competitions & tech talks spanning 3 days",
            created_by_id=faculty.id,
        )
        culturx = Event(
            id=uuid.uuid4(), name="CulturX 2025", type=EventType.major_fest,
            description="Annual cultural extravaganza with performances, art exhibitions, literary events & band nights",
            created_by_id=faculty.id,
        )
        startup_summit = Event(
            id=uuid.uuid4(), name="Startup Summit 2025", type=EventType.major_fest,
            description="Entrepreneurship summit featuring startup pitches, investor panels & incubation showcases",
            created_by_id=treasurer.id,
        )
        db.add_all([techsurge, culturx, startup_summit])
        await db.flush()

        # Sub-events nested under major fests
        hackathon = Event(
            id=uuid.uuid4(), name="Hackathon", type=EventType.sub_event,
            parent_event_id=techsurge.id,
            description="36-hour hackathon with industry mentors, ₹20K prize pool",
            created_by_id=treasurer.id,
        )
        dsa_bootcamp = Event(
            id=uuid.uuid4(), name="DSA Bootcamp", type=EventType.sub_event,
            parent_event_id=techsurge.id,
            description="3-day intensive DSA & competitive programming bootcamp",
            created_by_id=treasurer.id,
        )
        code_golf = Event(
            id=uuid.uuid4(), name="Code Golf", type=EventType.sub_event,
            parent_event_id=techsurge.id,
            description="Speed coding challenge: solve problems in fewest characters",
            created_by_id=treasurer.id,
        )
        battle_of_bands = Event(
            id=uuid.uuid4(), name="Battle of Bands", type=EventType.sub_event,
            parent_event_id=culturx.id,
            description="Inter-college band competition with professional sound setup",
            created_by_id=treasurer.id,
        )
        pitch_competition = Event(
            id=uuid.uuid4(), name="Pitch Competition", type=EventType.sub_event,
            parent_event_id=startup_summit.id,
            description="Student teams pitch startup ideas to investor panel for seed funding",
            created_by_id=treasurer.id,
        )
        # Standalone sub-event (no parent)
        photo_workshop = Event(
            id=uuid.uuid4(), name="Photography Workshop", type=EventType.sub_event,
            parent_event_id=None,
            description="Weekend workshop on DSLR photography, lighting, and post-processing",
            created_by_id=treasurer.id,
        )
        all_sub_events = [hackathon, dsa_bootcamp, code_golf, battle_of_bands, pitch_competition, photo_workshop]
        db.add_all(all_sub_events)
        await db.flush()

        # Assign event coordinators
        hackathon_lead.assigned_event_id = hackathon.id
        culturx_lead.assigned_event_id = culturx.id
        await db.flush()

        all_events = [techsurge, culturx, startup_summit] + all_sub_events
        print(f"  ✓ Created {len(all_events)} events (3 major + 5 sub-events + 1 standalone)")

        # ========== FINANCIAL RECORDS ==========
        admin_id = treasurer.id  # Most records created by treasurer
        records_data = [
            # === August 2024 — Early planning ===
            {"amount": Decimal("5000.00"), "type": RecordType.expense, "category": RecordCategory.digital_tools,
             "event_id": None, "date": date(2024, 8, 15),
             "notes": "Domain renewal + hosting for club website (vaultix.dev)"},
            {"amount": Decimal("2500.00"), "type": RecordType.expense, "category": RecordCategory.miscellaneous,
             "event_id": None, "date": date(2024, 8, 20),
             "notes": "Stationery and supplies for committee onboarding"},

            # === September 2024 — Grant season ===
            {"amount": Decimal("60000.00"), "type": RecordType.income, "category": RecordCategory.college_grant,
             "event_id": techsurge.id, "date": date(2024, 9, 5),
             "notes": "University annual grant for TechSurge 2025"},
            {"amount": Decimal("30000.00"), "type": RecordType.income, "category": RecordCategory.college_grant,
             "event_id": culturx.id, "date": date(2024, 9, 10),
             "notes": "Cultural committee annual grant for CulturX 2025"},
            {"amount": Decimal("20000.00"), "type": RecordType.income, "category": RecordCategory.college_grant,
             "event_id": startup_summit.id, "date": date(2024, 9, 12),
             "notes": "Entrepreneurship cell grant for Startup Summit 2025"},

            # === October 2024 — Sponsorship outreach ===
            {"amount": Decimal("75000.00"), "type": RecordType.income, "category": RecordCategory.sponsorship_title,
             "event_id": techsurge.id, "date": date(2024, 10, 1),
             "notes": "Title sponsorship from TechCorp India — brand visibility across all TechSurge events"},
            {"amount": Decimal("35000.00"), "type": RecordType.income, "category": RecordCategory.sponsorship_associate,
             "event_id": techsurge.id, "date": date(2024, 10, 15),
             "notes": "Associate sponsorship from CloudBase Solutions — hackathon co-sponsor"},
            {"amount": Decimal("40000.00"), "type": RecordType.income, "category": RecordCategory.sponsorship_title,
             "event_id": culturx.id, "date": date(2024, 10, 20),
             "notes": "Title sponsorship from CreativeMinds Agency for CulturX"},
            {"amount": Decimal("8000.00"), "type": RecordType.expense, "category": RecordCategory.marketing_printing,
             "event_id": techsurge.id, "date": date(2024, 10, 25),
             "notes": "Poster and banner printing for campus sponsorship outreach"},

            # === November 2024 — Registrations open ===
            {"amount": Decimal("15000.00"), "type": RecordType.income, "category": RecordCategory.registration_fees,
             "event_id": hackathon.id, "date": date(2024, 11, 5),
             "notes": "Hackathon registrations — 150 participants @ ₹100"},
            {"amount": Decimal("8000.00"), "type": RecordType.income, "category": RecordCategory.workshop_fees,
             "event_id": dsa_bootcamp.id, "date": date(2024, 11, 10),
             "notes": "DSA Bootcamp registrations — 40 students @ ₹200"},
            {"amount": Decimal("12000.00"), "type": RecordType.income, "category": RecordCategory.registration_fees,
             "event_id": code_golf.id, "date": date(2024, 11, 12),
             "notes": "Code Golf registrations — 120 participants @ ₹100"},
            {"amount": Decimal("5000.00"), "type": RecordType.income, "category": RecordCategory.workshop_fees,
             "event_id": photo_workshop.id, "date": date(2024, 11, 15),
             "notes": "Photography Workshop registrations — 25 students @ ₹200"},
            {"amount": Decimal("10000.00"), "type": RecordType.income, "category": RecordCategory.merchandise_sales,
             "event_id": techsurge.id, "date": date(2024, 11, 18),
             "notes": "TechSurge branded t-shirt pre-orders (100 units @ ₹100)"},

            # === December 2024 — Pre-event logistics ===
            {"amount": Decimal("25000.00"), "type": RecordType.expense, "category": RecordCategory.venue_logistics,
             "event_id": hackathon.id, "date": date(2024, 12, 1),
             "notes": "Auditorium booking and AV setup for hackathon venue"},
            {"amount": Decimal("4500.00"), "type": RecordType.expense, "category": RecordCategory.equipment_av,
             "event_id": hackathon.id, "date": date(2024, 12, 5),
             "notes": "Projector and speaker rental for hackathon"},
            {"amount": Decimal("10000.00"), "type": RecordType.expense, "category": RecordCategory.guest_honorarium,
             "event_id": dsa_bootcamp.id, "date": date(2024, 12, 8),
             "notes": "Honorarium for external DSA instructor (3-day workshop)"},
            {"amount": Decimal("3000.00"), "type": RecordType.expense, "category": RecordCategory.travel,
             "event_id": dsa_bootcamp.id, "date": date(2024, 12, 7),
             "notes": "Cab fare for external instructor pickup & drop"},

            # === January 2025 — TechSurge execution ===
            {"amount": Decimal("12000.00"), "type": RecordType.expense, "category": RecordCategory.food_hospitality,
             "event_id": hackathon.id, "date": date(2025, 1, 10),
             "notes": "Meals and refreshments for 36-hour hackathon — 150 participants"},
            {"amount": Decimal("20000.00"), "type": RecordType.expense, "category": RecordCategory.prizes_certificates,
             "event_id": hackathon.id, "date": date(2025, 1, 12),
             "notes": "Prize money: ₹10K (1st), ₹6K (2nd), ₹4K (3rd)"},
            {"amount": Decimal("6000.00"), "type": RecordType.expense, "category": RecordCategory.prizes_certificates,
             "event_id": code_golf.id, "date": date(2025, 1, 13),
             "notes": "Code Golf prizes and certificates for top 10"},
            {"amount": Decimal("8000.00"), "type": RecordType.expense, "category": RecordCategory.marketing_printing,
             "event_id": techsurge.id, "date": date(2025, 1, 5),
             "notes": "Instagram ads, posters, and standees for TechSurge promotion"},
            {"amount": Decimal("15000.00"), "type": RecordType.income, "category": RecordCategory.sponsorship_associate,
             "event_id": hackathon.id, "date": date(2025, 1, 8),
             "notes": "Late associate sponsor — DevTools Inc for hackathon prizes"},

            # === February 2025 — CulturX execution ===
            {"amount": Decimal("18000.00"), "type": RecordType.expense, "category": RecordCategory.venue_logistics,
             "event_id": culturx.id, "date": date(2025, 2, 5),
             "notes": "Open air theatre booking and stage decoration for CulturX"},
            {"amount": Decimal("15000.00"), "type": RecordType.expense, "category": RecordCategory.guest_honorarium,
             "event_id": battle_of_bands.id, "date": date(2025, 2, 8),
             "notes": "Professional sound engineer for Battle of Bands"},
            {"amount": Decimal("25000.00"), "type": RecordType.income, "category": RecordCategory.registration_fees,
             "event_id": culturx.id, "date": date(2025, 2, 1),
             "notes": "Cultural competition registrations across 5 categories — 500 participants"},
            {"amount": Decimal("7000.00"), "type": RecordType.expense, "category": RecordCategory.food_hospitality,
             "event_id": culturx.id, "date": date(2025, 2, 10),
             "notes": "Refreshments for audience and participants during CulturX"},
            {"amount": Decimal("6000.00"), "type": RecordType.expense, "category": RecordCategory.marketing_printing,
             "event_id": culturx.id, "date": date(2025, 2, 3),
             "notes": "Printing flex banners and standees for CulturX"},
            {"amount": Decimal("10000.00"), "type": RecordType.expense, "category": RecordCategory.prizes_certificates,
             "event_id": culturx.id, "date": date(2025, 2, 12),
             "notes": "Trophies and certificates for cultural competitions"},
            {"amount": Decimal("3500.00"), "type": RecordType.income, "category": RecordCategory.other_income,
             "event_id": culturx.id, "date": date(2025, 2, 11),
             "notes": "Stall rent collected from external food vendors at CulturX"},
            {"amount": Decimal("5000.00"), "type": RecordType.expense, "category": RecordCategory.equipment_av,
             "event_id": battle_of_bands.id, "date": date(2025, 2, 7),
             "notes": "Amplifier, mixer, and mic rental for Battle of Bands"},

            # === March 2025 — Startup Summit ===
            {"amount": Decimal("20000.00"), "type": RecordType.income, "category": RecordCategory.sponsorship_associate,
             "event_id": startup_summit.id, "date": date(2025, 3, 1),
             "notes": "VC firm co-sponsorship for Startup Summit judge panel"},
            {"amount": Decimal("10000.00"), "type": RecordType.expense, "category": RecordCategory.venue_logistics,
             "event_id": startup_summit.id, "date": date(2025, 3, 5),
             "notes": "Conference hall and AV setup for Startup Summit"},
            {"amount": Decimal("8000.00"), "type": RecordType.income, "category": RecordCategory.registration_fees,
             "event_id": pitch_competition.id, "date": date(2025, 3, 3),
             "notes": "Pitch Competition registrations — 40 teams @ ₹200"},
            {"amount": Decimal("15000.00"), "type": RecordType.expense, "category": RecordCategory.guest_honorarium,
             "event_id": startup_summit.id, "date": date(2025, 3, 10),
             "notes": "Speaker honorarium — serial entrepreneur keynote"},
            {"amount": Decimal("5000.00"), "type": RecordType.expense, "category": RecordCategory.food_hospitality,
             "event_id": startup_summit.id, "date": date(2025, 3, 10),
             "notes": "Networking lunch for speakers, judges, and finalists"},

            # === April 2025 — Wrap-up ===
            {"amount": Decimal("12000.00"), "type": RecordType.income, "category": RecordCategory.alumni_donation,
             "event_id": None, "date": date(2025, 4, 1),
             "notes": "Donation from 2023 batch alumni for general club activities"},
            {"amount": Decimal("3000.00"), "type": RecordType.expense, "category": RecordCategory.miscellaneous,
             "event_id": None, "date": date(2025, 4, 5),
             "notes": "End-of-year team dinner for core committee"},
            {"amount": Decimal("4000.00"), "type": RecordType.expense, "category": RecordCategory.digital_tools,
             "event_id": None, "date": date(2025, 4, 8),
             "notes": "Canva Pro + Notion team subscription renewal"},
            {"amount": Decimal("2000.00"), "type": RecordType.income, "category": RecordCategory.merchandise_sales,
             "event_id": culturx.id, "date": date(2025, 2, 12),
             "notes": "Leftover CulturX merchandise sold at discounted rates"},
            {"amount": Decimal("3500.00"), "type": RecordType.expense, "category": RecordCategory.travel,
             "event_id": startup_summit.id, "date": date(2025, 3, 9),
             "notes": "Airport pickup and hotel transfer for keynote speaker"},
        ]

        created_records = []
        for rec_data in records_data:
            record = FinancialRecord(id=uuid.uuid4(), created_by_id=admin_id, **rec_data)
            db.add(record)
            created_records.append(record)
        await db.flush()
        print(f"  ✓ Created {len(created_records)} financial records")

        # Soft-delete 2 records
        deleted_records = [created_records[-4], created_records[1]]  # dinner + stationery
        for dr in deleted_records:
            dr.is_deleted = True
            dr.deleted_at = datetime.now(timezone.utc)
            dr.deleted_by_id = faculty.id
        await db.flush()
        print(f"  ✓ Soft-deleted {len(deleted_records)} records")

        # ========== AUDIT LOGS ==========
        # Event creations
        for event in all_events:
            db.add(AuditLog(
                actor_id=faculty.id if event.type == EventType.major_fest else treasurer.id,
                action=AuditAction.created,
                resource_type=ResourceType.event,
                resource_id=event.id,
                new_data={"name": event.name, "type": event.type.value},
            ))

        # Sample record creations (first 8)
        for record in created_records[:8]:
            db.add(AuditLog(
                actor_id=admin_id,
                action=AuditAction.created,
                resource_type=ResourceType.financial_record,
                resource_id=record.id,
                new_data={
                    "amount": str(record.amount),
                    "type": record.type.value,
                    "category": record.category.value,
                },
            ))

        # Soft-delete audit entries
        for dr in deleted_records:
            db.add(AuditLog(
                actor_id=faculty.id,
                action=AuditAction.deleted,
                resource_type=ResourceType.financial_record,
                resource_id=dr.id,
                old_data={
                    "amount": str(dr.amount),
                    "type": dr.type.value,
                    "notes": dr.notes,
                },
            ))

        # User creation audit entries
        for u in all_users:
            db.add(AuditLog(
                actor_id=faculty.id,
                action=AuditAction.created,
                resource_type=ResourceType.user,
                resource_id=u.id,
                new_data={"name": u.name, "email": u.email, "role": u.role.value},
            ))

        # Role change audit: hackathon_lead was originally viewer, promoted to analyst
        db.add(AuditLog(
            actor_id=faculty.id,
            action=AuditAction.role_changed,
            resource_type=ResourceType.user,
            resource_id=hackathon_lead.id,
            old_data={"role": "viewer"},
            new_data={"role": "analyst"},
        ))

        # Update audit: Treasurer updated a record amount
        db.add(AuditLog(
            actor_id=treasurer.id,
            action=AuditAction.updated,
            resource_type=ResourceType.financial_record,
            resource_id=created_records[5].id,
            old_data={"amount": "70000.00"},
            new_data={"amount": str(created_records[5].amount)},
        ))

        await db.commit()
        total_audit = len(all_events) + 8 + len(deleted_records) + len(all_users) + 2
        print(f"  ✓ Created {total_audit} audit log entries")

        print("\n" + "=" * 50)
        print("SEED COMPLETE!")
        print("=" * 50)
        print(f"  Users:     {len(all_users)}")
        print(f"  Events:    {len(all_events)} (3 major + {len(all_sub_events)} sub-events)")
        print(f"  Records:   {len(created_records)} ({len(deleted_records)} soft-deleted)")
        print(f"  Audit Logs: {total_audit}")
        print()
        print("Login credentials:")
        print("  ┌──────────────────────────────────────────────────────────────")
        print("  │ ADMIN")
        print("  │   faculty@vaultix.dev    / faculty123     (Faculty Advisor)")
        print("  │   treasurer@vaultix.dev  / treasurer123   (Club Treasurer)")
        print("  │")
        print("  │ ANALYST")
        print("  │   secretary@vaultix.dev  / secretary123   (General view)")
        print(f"  │   hackathon@vaultix.dev  / hackathon123   (→ {hackathon.name} only)")
        print(f"  │   culturx@vaultix.dev    / culturx123     (→ {culturx.name} only)")
        print("  │")
        print("  │ VIEWER")
        print("  │   karan@vaultix.dev      / karan123       (Core member)")
        print("  │   sponsor@vaultix.dev    / sponsor123     (Sponsor rep)")
        print("  └──────────────────────────────────────────────────────────────")


if __name__ == "__main__":
    asyncio.run(seed())
