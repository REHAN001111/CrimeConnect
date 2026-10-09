import os
from datetime import datetime, timezone, date, time, timedelta
from app import create_app
from extensions import db
from models import User, Complaint, ComplaintHistory, AdminNote

def seed_database():
    """Populate database with default admin, demo citizens, and realistic fictional incident reports."""
    app = create_app()
    with app.app_context():
        print("[*] Recreating database tables...")
        db.drop_all()
        db.create_all()

        print("[*] Creating administrative and demo user accounts...")
        # 1. Administrator Account
        admin = User(
            full_name="Chief Admin Officer",
            email="admin@crimeconnect.local",
            phone="555-0199",
            role="admin"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

        # 2. Citizen Account 1
        citizen1 = User(
            full_name="Alex Morgan",
            email="citizen@crimeconnect.local",
            phone="555-0142",
            role="user"
        )
        citizen1.set_password("Citizen@123")
        db.session.add(citizen1)

        # 3. Citizen Account 2
        citizen2 = User(
            full_name="Jane Doe",
            email="jane@crimeconnect.local",
            phone="555-0188",
            role="user"
        )
        citizen2.set_password("Citizen@123")
        db.session.add(citizen2)

        db.session.commit()

        print("[*] Seeding realistic fictional complaints...")
        now = datetime.now(timezone.utc)

        # Record 1: Cybercrime
        c1 = Complaint(
            reference_number="CR-20261001-A104E",
            user_id=citizen1.id,
            category="Cybercrime",
            title="Phishing Email and Unauthorized Debit Scam",
            description=(
                "Received a fraudulent notification purporting to be from the campus finance office. "
                "Clicked a link asking to verify tuition payment and entered bank credentials. "
                "Subsequently noticed an unauthorized transfer of $140.00 to a fictional merchant."
            ),
            incident_date=date(2026, 10, 1),
            incident_time=time(14, 30),
            incident_location="Online / Student Portal Email",
            witness_information="Roommate witnessed email delivery and initial panic.",
            status=Complaint.STATUS_UNDER_REVIEW,
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=5)
        )
        db.session.add(c1)
        db.session.flush()

        h1_1 = ComplaintHistory(
            complaint_id=c1.id,
            previous_status="None",
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks="Complaint submitted by citizen and queued for triage.",
            changed_by=citizen1.id,
            created_at=c1.created_at
        )
        h1_2 = ComplaintHistory(
            complaint_id=c1.id,
            previous_status=Complaint.STATUS_SUBMITTED,
            new_status=Complaint.STATUS_UNDER_REVIEW,
            public_remarks="Report assigned to Cyber Triage Unit. Reviewing server logs and phishing URL.",
            changed_by=admin.id,
            created_at=c1.updated_at
        )
        n1 = AdminNote(
            complaint_id=c1.id,
            admin_id=admin.id,
            note="Domain registrant traced to known educational phishing campaign. Bank liaison contacted.",
            created_at=c1.updated_at
        )
        db.session.add_all([h1_1, h1_2, n1])

        # Record 2: Theft
        c2 = Complaint(
            reference_number="CR-20261002-B892F",
            user_id=citizen1.id,
            category="Theft",
            title="Stolen Mountain Bike from North Campus Racks",
            description=(
                "Blue Trek Marlin 5 bicycle was securely U-locked to bike rack outside Engineering Hall at 9:00 AM. "
                "Upon return at 4:30 PM, the cable was severed and the bicycle was missing."
            ),
            incident_date=date(2026, 10, 2),
            incident_time=time(16, 30),
            incident_location="Engineering Hall, Rack #4",
            witness_information="Campus security guard saw an unidentified person with bolt cutters around 2 PM.",
            status=Complaint.STATUS_RESOLVED,
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=1)
        )
        db.session.add(c2)
        db.session.flush()

        h2_1 = ComplaintHistory(
            complaint_id=c2.id,
            previous_status="None",
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks="Theft report filed with serial number registered.",
            changed_by=citizen1.id,
            created_at=c2.created_at
        )
        h2_2 = ComplaintHistory(
            complaint_id=c2.id,
            previous_status=Complaint.STATUS_SUBMITTED,
            new_status=Complaint.STATUS_UNDER_REVIEW,
            public_remarks="CCTV footage checked from Hall entrance cameras.",
            changed_by=admin.id,
            created_at=c2.created_at + timedelta(days=1)
        )
        h2_3 = ComplaintHistory(
            complaint_id=c2.id,
            previous_status=Complaint.STATUS_UNDER_REVIEW,
            new_status=Complaint.STATUS_RESOLVED,
            public_remarks="Bicycle recovered by campus security patrol near perimeter fence. Ready for owner verification and collection.",
            changed_by=admin.id,
            created_at=c2.updated_at
        )
        n2 = AdminNote(
            complaint_id=c2.id,
            admin_id=admin.id,
            note="Item matches description 100%. Security locker custody receipt #4409 signed.",
            created_at=c2.updated_at
        )
        db.session.add_all([h2_1, h2_2, h2_3, n2])

        # Record 3: Fraud
        c3 = Complaint(
            reference_number="CR-20261004-C447A",
            user_id=citizen2.id,
            category="Fraud",
            title="Counterfeit Textbook Sale on Student Forum",
            description=(
                "Agreed to purchase a required Organic Chemistry textbook from a local classified post. "
                "Transferred payment via digital peer-to-peer app, but the seller deactivated account and never delivered item."
            ),
            incident_date=date(2026, 10, 4),
            incident_time=time(11, 15),
            incident_location="Student Forum & Union Courtyard",
            witness_information="None.",
            status=Complaint.STATUS_INFO_REQUESTED,
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=2)
        )
        db.session.add(c3)
        db.session.flush()

        h3_1 = ComplaintHistory(
            complaint_id=c3.id,
            previous_status="None",
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks="Fraud complaint submitted.",
            changed_by=citizen2.id,
            created_at=c3.created_at
        )
        h3_2 = ComplaintHistory(
            complaint_id=c3.id,
            previous_status=Complaint.STATUS_SUBMITTED,
            new_status=Complaint.STATUS_INFO_REQUESTED,
            public_remarks="Please provide transaction reference number and full chat screenshots showing seller username.",
            changed_by=admin.id,
            created_at=c3.updated_at
        )
        db.session.add_all([h3_1, h3_2])

        # Record 4: Harassment
        c4 = Complaint(
            reference_number="CR-20261005-D312E",
            user_id=citizen2.id,
            category="Harassment",
            title="Unsolicited Defamatory Comments in Public Chat",
            description=(
                "An anonymous handle has repeatedly posted threatening and defamatory remarks "
                "across the student project collaboration workspace."
            ),
            incident_date=date(2026, 10, 5),
            incident_time=time(20, 00),
            incident_location="IT Lab Slack Workspace",
            witness_information="Classmates in group project thread #team-alpha.",
            status=Complaint.STATUS_UNDER_REVIEW,
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1)
        )
        db.session.add(c4)
        db.session.flush()

        h4_1 = ComplaintHistory(
            complaint_id=c4.id,
            previous_status="None",
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks="Harassment report recorded under strict confidentiality.",
            changed_by=citizen2.id,
            created_at=c4.created_at
        )
        db.session.add(h4_1)

        # Record 5: Vandalism
        c5 = Complaint(
            reference_number="CR-20261007-E7719",
            user_id=citizen1.id,
            category="Vandalism",
            title="Graffiti Painted on Library Outer Wall",
            description=(
                "Noticed spray-paint vandalism along the exterior north wall of the Central Memorial Library."
            ),
            incident_date=date(2026, 10, 7),
            incident_time=time(7, 45),
            incident_location="Central Library North Facade",
            witness_information="Library opening staff.",
            status=Complaint.STATUS_CLOSED,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(hours=6)
        )
        db.session.add(c5)
        db.session.flush()

        h5_1 = ComplaintHistory(
            complaint_id=c5.id,
            previous_status="None",
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks="Vandalism report received.",
            changed_by=citizen1.id,
            created_at=c5.created_at
        )
        h5_2 = ComplaintHistory(
            complaint_id=c5.id,
            previous_status=Complaint.STATUS_SUBMITTED,
            new_status=Complaint.STATUS_CLOSED,
            public_remarks="Facilities management dispatched. Wall repainted. CCTV footage archived.",
            changed_by=admin.id,
            created_at=c5.updated_at
        )
        db.session.add_all([h5_1, h5_2])

        # Record 6: Missing Property
        c6 = Complaint(
            reference_number="CR-20261009-F909A",
            user_id=citizen2.id,
            category="Missing Property",
            title="Misplaced Black Backpack with Lab Notebooks",
            description=(
                "Left a black Jansport backpack containing lab notebooks and a TI-84 calculator on the third floor study bench."
            ),
            incident_date=date(2026, 10, 9),
            incident_time=time(13, 00),
            incident_location="Science Complex Floor 3",
            witness_information="Study group peers.",
            status=Complaint.STATUS_SUBMITTED,
            created_at=now,
            updated_at=now
        )
        db.session.add(c6)
        db.session.flush()

        h6_1 = ComplaintHistory(
            complaint_id=c6.id,
            previous_status="None",
            new_status=Complaint.STATUS_SUBMITTED,
            public_remarks="Report filed. Forwarded to Lost & Found desk.",
            changed_by=citizen2.id,
            created_at=c6.created_at
        )
        db.session.add(h6_1)

        db.session.commit()

        print("\n=======================================================")
        print("  CrimeConnect Database Initialized and Seeded!       ")
        print("=======================================================")
        print("  [Demo Accounts Created]")
        print("  1. Administrator Account:")
        print("     Email:    admin@crimeconnect.local")
        print("     Password: Admin@123")
        print("     Role:     admin")
        print("\n  2. Citizen Account 1:")
        print("     Email:    citizen@crimeconnect.local")
        print("     Password: Citizen@123")
        print("     Role:     user")
        print("\n  3. Citizen Account 2:")
        print("     Email:    jane@crimeconnect.local")
        print("     Password: Citizen@123")
        print("     Role:     user")
        print("=======================================================")

if __name__ == '__main__':
    seed_database()
