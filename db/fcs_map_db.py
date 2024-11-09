from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class FcsMap(BaseModel):
    lpar_fc: str
    lpar: str
    clntid: str
    clntname: str
    fc: str
    vfcclient: str
    # lpar = relationship('Lpar', back_populates='fcs_map')


class FcsMapDb(JsonDb):

    def add(self, child: FcsMap):
        if self.children.get(child.lpar_fc):
            logger.warning(f'{child} exist')
        else:
            self.children[child.lpar_fc] = child.model_dump(mode='json')
            self.save()


fcs_map_db = FcsMapDb('fcs_map_db')
