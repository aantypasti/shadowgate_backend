# shadowgate_api/utils/seed_eligibility.py
import csv
from pathlib import Path
from sqlalchemy.orm import Session
from shadowgate_api.db import SessionLocal, engine, Base
from shadowgate_api.loan_eligibility_model import LoanEligibility

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "loan_eligibility.csv"

def seed_from_csv(csv_path: Path = CSV_PATH):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()
    try:
        count = session.query(LoanEligibility).count()
        if count > 0:
            print(f"[seed] loan_eligibility already has {count} rows; skipping.")
            return

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                bases = int(row["Bases"])
                max_amount = int(row["Max loan"])
                interest = float(row["Interest"])
                loan_type = str(row["Type"]).strip()  # "Std" / "Shp"

                rows.append(LoanEligibility(
                    bases=bases,
                    loan_type=loan_type,
                    max_amount=max_amount,
                    interest=interest,
                ))

        session.bulk_save_objects(rows)
        session.commit()
        print(f"[seed] inserted {len(rows)} rows into loan_eligibility.")
    finally:
        session.close()

if __name__ == "__main__":
    seed_from_csv()
