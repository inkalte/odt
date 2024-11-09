from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class Fcs(BaseModel):
    name: str = Field(repr=False)
    wwn: str = Field(repr=False)
    lpar: str
    # lpar = relationship('Lpar', back_populates='fcs')


class FcsDb(JsonDb):

    def add(self, child: Fcs):
        if self.children.get(child.name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.name] = child.model_dump(mode='json')
            self.save()


fcs_db = FcsDb('fcs_db')
