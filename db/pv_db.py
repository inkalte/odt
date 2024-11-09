from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class Pv(BaseModel):
    lpar_vg_name: str
    name: str
    vg_id: int
    vg_name: str
    lpar: str
    size: int
    # vg = relationship('Vg', back_populates='pv')
    # lpar = relationship('Lpar', back_populates='pv')


class PvDb(JsonDb):

    def add(self, child: Pv):
        if self.children.get(child.lpar_vg_name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.lpar_vg_name] = child.model_dump(mode='json')
            self.save()


pv_db = PvDb('pv_db')
