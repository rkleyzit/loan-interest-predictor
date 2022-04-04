from datetime import date
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from utils.models.forward_rate_run_batch import ForwardRateRunBatch
from utils.models.forward_rate import ForwardRate
from utils.database import session

router = APIRouter()
prefix = '/interest-rates'


class LoanDetails(BaseModel):
    maturity_date: date
    reference_rate: str
    rate_floor: float
    rate_ceiling: float
    rate_spread: float


def calculate_loan_interest_rate(loan_details: LoanDetails, reference_rate: ForwardRate) -> dict:
    """Calculated the predicted rate for a give day's reference rate combined with the loan details"""
    # assuming both reference rate and loan_details rates given as decimal
    predicted_rate = loan_details.rate_spread + reference_rate.predicted_rate
    predicted_rate = max(loan_details.rate_floor, predicted_rate)
    predicted_rate = min(loan_details.rate_ceiling, predicted_rate)

    return {
        'date': reference_rate.effective_date.strftime('%Y-%m-%d'),
        'rate': predicted_rate
    }


@router.post(f'/predict')
async def predict_rates(loan_details: LoanDetails) -> List[dict]:
    """Return a list of predicted interest rates by date for the given loan"""
    # find latest batch for the given reference rate
    latest_batch = session.query(
        ForwardRateRunBatch
    ).filter_by(
        reference_rate=loan_details.reference_rate
    ).order_by(
        ForwardRateRunBatch.run_time.desc()
    ).first()

    # query reference rates from the above batch with an effective date before the loan's maturity
    reference_rates = session.query(
        ForwardRate
    ).filter(
        ForwardRate.batch_id == latest_batch.batch_id,
        ForwardRate.effective_date <= loan_details.maturity_date
    ).order_by(
        ForwardRate.effective_date.asc()
    ).all()

    return [calculate_loan_interest_rate(loan_details, rate) for rate in reference_rates]
