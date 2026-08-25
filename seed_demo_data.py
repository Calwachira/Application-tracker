"""
Optional: populate applications.db with a handful of sample rows so you can
see the tracker in action before adding your own applications.

Run once:
    python seed_demo_data.py
"""

from app import Database

SAMPLE = [
    {"company": "Safaricom PLC", "role": "Data Analyst", "status": "Interview",
     "date_applied": "2026-08-01", "location": "Nairobi, KE", "salary": "KES 120k/mo",
     "source": "LinkedIn", "url": "", "contact": "recruiter@safaricom.co.ke",
     "notes": "Technical interview scheduled for next week."},
    {"company": "Remotasks", "role": "Data Annotator", "status": "Applied",
     "date_applied": "2026-08-10", "location": "Remote", "salary": "$8/hr",
     "source": "Company site", "url": "", "contact": "", "notes": ""},
    {"company": "KPMG Kenya", "role": "Junior Data Analyst", "status": "Screening",
     "date_applied": "2026-08-05", "location": "Nairobi, KE", "salary": "TBD",
     "source": "Referral", "url": "", "contact": "Jane (referral)", "notes": "Phone screen passed."},
    {"company": "Andela", "role": "Data Analyst (Junior)", "status": "Wishlist",
     "date_applied": "", "location": "Remote", "salary": "TBD",
     "source": "Company site", "url": "", "contact": "", "notes": "Plan to apply this week."},
    {"company": "Twiga Foods", "role": "Business/Data Analyst", "status": "Rejected",
     "date_applied": "2026-07-20", "location": "Nairobi, KE", "salary": "",
     "source": "LinkedIn", "url": "", "contact": "", "notes": "Went with a more senior candidate."},
]

if __name__ == "__main__":
    db = Database()
    for row in SAMPLE:
        db.add(row)
    print(f"Seeded {len(SAMPLE)} sample applications into applications.db")
