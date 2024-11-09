from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class Ufk(BaseModel):
    name: str
    code: str
    # lpar = relationship('Lpar', back_populates='ufk')


class UfkDb(JsonDb):

    def add(self, child: Ufk):
        if self.children.get(child.name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.name] = child.model_dump(mode='json')
            self.save()


ufk_db = UfkDb('ufk_db')
