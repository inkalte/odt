from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class Vg(BaseModel):
    name: str
    size: int = Field(repr=False)
    lpar: str
    # lpar = relationship('Lpar', back_populates='vg')
    # pv = relationship('Pv', back_populates='vg')


class VgDb(JsonDb):

    def add(self, child: Vg):
        if self.children.get(child.name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.name] = child.model_dump(mode='json')
            self.save()


vg_db = VgDb('vg_db')
