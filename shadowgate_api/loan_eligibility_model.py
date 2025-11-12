# shadowgate_api/loan_eligibility_model.py
from sqlalchemy import Column, Integer, String, Float, Numeric, UniqueConstraint, Index
from shadowgate_api.db import Base

class LoanEligibility(Base):
    __tablename__ = "loan_eligibility"

    id = Column(Integer, primary_key=True, index=True)

    # number of bases the rule applies to (exact match in your CSV)
    bases = Column(Integer, nullable=False, index=True)

    # 'Std' or 'Shp' (we'll normalize to lowercase in API if you want)
    loan_type = Column(String(8), nullable=False)

    # max loan amount allowed for this row (integer cents or whole units)
    max_amount = Column(Integer, nullable=False)

    # interest rate as percent (e.g., 2.5)
    interest = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("bases", "loan_type", "max_amount", name="uq_eligibility_row"),
        Index("ix_eligibility_lookup", "bases", "loan_type"),
    )
