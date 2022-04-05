from datetime import date
from unittest import TestCase

from utils.models.forward_rate import ForwardRate
from api.routes.interest_rate_curve import LoanDetails, calculate_loan_interest_rate


class EtlTest(TestCase):
    def setUp(self) -> None:
        self.sofr = ForwardRate.create(date(2022, 3, 28), 0.0031258, 1)

    def calculate_loan_interest_rate_ceiling_test(self):
        """Assert that predicted rate does not exceed ceiling"""
        spread = 0.05
        ceiling = 0.003
        floor = 0.001
        loan_details = LoanDetails(
            maturity_date=date(2022, 2, 1),
            reference_rate='SOFR',
            rate_floor=floor,
            rate_ceiling=ceiling,
            rate_spread=spread
        )
        predicted_rate = calculate_loan_interest_rate(loan_details, self.sofr).get('rate')
        self.assertEqual(predicted_rate, ceiling)

    def calculate_loan_interest_rate_floor_test(self):
        """Assert that predicted rate does not fall below floor"""
        floor = 0.1
        ceiling = 0.3
        spread = 0.0025
        loan_details = LoanDetails(
            maturity_date=date(2022, 2, 1),
            reference_rate='SOFR',
            rate_floor=floor,
            rate_ceiling=ceiling,
            rate_spread=spread
        )
        predicted_rate = calculate_loan_interest_rate(loan_details, self.sofr).get('rate')
        self.assertEqual(predicted_rate, floor)

    def calculate_loan_interest_rate_test(self):
        """Assert that predicted rate is the sum of the spread and reference rate if between floor and ceiling"""
        floor = 0.001
        ceiling = 1
        spread = 0.0025
        loan_details = LoanDetails(
            maturity_date=date(2022, 2, 1),
            reference_rate='SOFR',
            rate_floor=floor,
            rate_ceiling=ceiling,
            rate_spread=spread
        )
        predicted_rate = calculate_loan_interest_rate(loan_details, self.sofr).get('rate')
        self.assertEqual(predicted_rate, spread + self.sofr.predicted_rate)
