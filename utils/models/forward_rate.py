from datetime import date
from sqlalchemy import Column, Float, Date, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from utils.database import Model
from utils.models.forward_rate_run_batch import ForwardRateRunBatch
from utils.models.table import Table


class ForwardRate(Model, Table):
    """SqlAlchemy table definition"""
    __tablename__ = 'ForwardRate'

    rate_id = Column('RateId', Integer, autoincrement=True, primary_key=True)
    effective_date = Column('EffectiveDate', Date, nullable=False)
    predicted_rate = Column('PredictedRate', Float, nullable=False)
    batch_id = Column('BatchId', Integer, ForeignKey(ForwardRateRunBatch.batch_id))

    run_batch = relationship('ForwardRateRunBatch', back_populates='rates')

    Index("forward_rate_effective_date_asc", rate_id, effective_date.asc())

    @classmethod
    def create(cls, effective_date: date, predicted_rate: float, batch_id: int):
        """Create and validate a new forward rate"""
        fr = ForwardRate(
            effective_date=effective_date,
            predicted_rate=predicted_rate,
            batch_id=batch_id
        )

        fr.validate()

        return fr

    schema = {
        'effective_date': {'type': 'date', 'required': True},
        'predicted_rate': {'type': 'float', 'required': True},
        'batch_id': {'type': 'integer', 'required': True},
    }
