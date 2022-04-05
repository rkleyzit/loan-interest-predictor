from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Index
from sqlalchemy.orm import relationship

from utils.database import Model
from utils.models.table import Table


class ForwardRateRunBatch(Model, Table):
    """SqlAlchemy table definition"""
    __tablename__ = 'ForwardRateRunBatch'

    batch_id = Column('BatchId', Integer, autoincrement=True, primary_key=True)
    reference_rate = Column('ReferenceRate', String, nullable=False)
    source = Column('Source', String, nullable=False)
    run_time = Column('BatchRunTime', DateTime, nullable=False)

    rates = relationship('ForwardRate', back_populates='run_batch')

    Index("forward_rate_run_batch_run_time_desc", batch_id, run_time.desc())

    @classmethod
    def create(cls, reference_rate: str, source: str):
        """Create and validate a new forward rate"""
        batch = ForwardRateRunBatch(
            reference_rate=reference_rate,
            source=source,
            run_time=datetime.now()
        )

        batch.validate()

        return batch

    schema = {
        'reference_rate': {'type': 'string', 'required': True},
        'source': {'type': 'string', 'required': True},
        'run_time': {'type': 'datetime', 'required': True}
    }
