from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class Lpar(BaseModel):
    id: int
    name: str
    lpar_id: str
    sys_name: str
    state: str
    curr_profile: str = Field(repr=False)
    os: str = Field(repr=False)
    min_proc_units: float = Field(repr=False)
    desired_proc_units: float = Field(repr=False)
    max_proc_units: float = Field(repr=False)
    min_procs: int = Field(repr=False)
    desired_procs: int = Field(repr=False)
    max_procs: int = Field(repr=False)
    min_mem: int = Field(repr=False)
    desired_mem: int = Field(repr=False)
    max_mem: int = Field(repr=False)
    ufk_code: str = Field(repr=False)
    # host = relationship('Host', uselist=False, back_populates='lpar')
    # prof = relationship('LparProf', uselist=False, back_populates='lpar')
    # sys = relationship('Sys', back_populates='lpar')
    # vg = relationship('Vg', back_populates='lpar')
    # fcs = relationship('Fcs', back_populates='lpar')
    # fcs_map = relationship('FcsMap', back_populates='lpar')
    # pv = relationship('Pv', back_populates='lpar')
    # ufk = relationship('Ufk', back_populates='lpar')


class LparDb(JsonDb):

    def add(self, child: Lpar):
        if self.children.get(child.name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.name] = child.model_dump(mode='json')
            self.save()


lpar_db = LparDb('lpar_db')
