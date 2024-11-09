from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class LparProf(BaseModel):
    name: str
    sys_name: str
    min_proc_units: float = Field(repr=False)
    desired_proc_units: float = Field(repr=False)
    max_proc_units: float = Field(repr=False)
    min_procs: int = Field(repr=False)
    desired_procs: int = Field(repr=False)
    max_procs: int = Field(repr=False)
    min_mem: int = Field(repr=False)
    desired_mem: int = Field(repr=False)
    max_mem: int = Field(repr=False)
    # lpar = relationship('Lpar', uselist=False, back_populates='prof')


class LparProfDb(JsonDb):

    def add(self, child: LparProf):
        if self.children.get(child.name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.name] = child.model_dump(mode='json')
            self.save()


lpar_prof_db = LparProfDb('lpar_prof_db')
