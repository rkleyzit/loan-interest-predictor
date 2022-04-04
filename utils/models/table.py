from abc import abstractmethod
from cerberus import Validator
from sqlalchemy.orm.state import InstanceState


class Table:
    @property
    @abstractmethod
    def schema(self):
        pass

    def to_dict(self) -> dict:
        """Convert Sqlalchemy table properties to dict"""
        return {k: v for k, v in vars(self).items() if not isinstance(v, InstanceState)}

    def validate(self):
        """Validate that row instance conforms to table schema"""
        if not self.schema:
            return None

        v = Validator(self.schema, allow_unknown=True)
        res = v.validate(Table.to_dict(self))

        if not res:
            raise Exception(f'{self.__tablename__} object validation error: {v.errors}')
