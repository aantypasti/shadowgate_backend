# shadowgate_api/routers/loan_eligibility.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from shadowgate_api.db import get_db
from shadowgate_api.utils.auth_simple import get_current_user  # adjust if you use utils.auth
from shadowgate_api.loan_eligibility_model import LoanEligibility

router = APIRouter(prefix="/api/loan", tags=["loan"])

# Public/neutral lookup by explicit base count (handy for admin/testing)
@router.get("/eligibility/{bases}")
def get_eligibility_for_bases(bases: int, db: Session = Depends(get_db)):
    rows = (
        db.query(LoanEligibility)
        .filter(LoanEligibility.bases == bases)
        .order_by(LoanEligibility.loan_type.asc(), LoanEligibility.max_amount.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No eligibility found for given bases")
    return [
        {
            "bases": r.bases,
            "type": r.loan_type,      # "Std" or "Shp"
            "max_amount": r.max_amount,
            "interest": r.interest,
        }
        for r in rows
    ]

# Authenticated lookup for the current user (uses users.bases)
@router.get("/eligibility/mine")
def get_my_eligibility(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    bases = getattr(current_user, "bases", None)
    if bases is None:
        raise HTTPException(status_code=400, detail="User has no 'bases' field set")

    rows = (
        db.query(LoanEligibility)
        .filter(LoanEligibility.bases == bases)
        .order_by(LoanEligibility.loan_type.asc(), LoanEligibility.max_amount.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No eligibility found for user")
    return [
        {
            "bases": r.bases,
            "type": r.loan_type,
            "max_amount": r.max_amount,
            "interest": r.interest,
        }
        for r in rows
    ]
