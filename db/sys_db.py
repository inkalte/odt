from pydantic import BaseModel, Field
from db import JsonDb
from logs import get_logger

logger = get_logger(__file__)


class Sys(BaseModel):
    name: str
    state: str = Field(repr=False)
    type_model: str = Field(repr=False)
    serial_num: str = Field(repr=False)
    configurable_sys_proc_units: float = Field(repr=False)
    curr_avail_sys_proc_units: float = Field(repr=False)
    pend_avail_sys_proc_units: float = Field(repr=False)
    configurable_sys_mem: int = Field(repr=False)
    curr_avail_sys_mem: int = Field(repr=False)
    pend_avail_sys_mem: int = Field(repr=False)
    sys_firmware_mem: int = Field(repr=False)
    hmc1_ipaddr: str = Field(repr=False)
    hmc1_ipaddr_secondary: str = Field(repr=False)
    hmc2_ipaddr: str = Field(repr=False)
    hmc2_ipaddr_secondary: str = Field(repr=False)
    # lpar = relationship('Lpar', back_populates='sys')


class SysDb(JsonDb):

    def add(self, child: Sys):
        if self.children.get(child.name):
            logger.warning(f'{child} exist')
        else:
            self.children[child.name] = child.model_dump(mode='json')
            self.save()


sys_db = SysDb('sys_db')
