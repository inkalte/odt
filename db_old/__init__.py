from sqlalchemy import Column, Integer, String, create_engine, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from env import db_path

engine = create_engine(db_path, echo=False)
Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'
    id: int = Column(Integer, primary_key=True)
    hostname: str = Column(String, unique=True)
    ip: str = Column(String)
    login: str = Column(String)
    password: str = Column(String)
    type: str = Column(String)
    lpar = relationship('Lpar', uselist=False, back_populates='host')

    def __repr__(self):
        return f'Host({self.hostname} {self.ip})'


class Sys(Base):
    __tablename__ = 'sys'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, unique=True)
    state: str = Column(String)
    type_model: str = Column(String)
    serial_num: str = Column(String)
    configurable_sys_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    curr_avail_sys_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    pend_avail_sys_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    configurable_sys_mem: int = Column(Integer)
    curr_avail_sys_mem: int = Column(Integer)
    pend_avail_sys_mem: int = Column(Integer)
    sys_firmware_mem: int = Column(Integer)
    hmc1_ipaddr: str = Column(String)
    hmc1_ipaddr_secondary: str = Column(String)
    hmc2_ipaddr: str = Column(String)
    hmc2_ipaddr_secondary: str = Column(String)
    lpar = relationship('Lpar', back_populates='sys')

    def __repr__(self):
        return f'Sys(name="{self.name}", ' \
               f'Sys(state="{self.state}", ' \
               f'proc="{self.configurable_sys_proc_units}", ' \
               f'mem="{self.configurable_sys_mem}", ' \
               f'hmc1_ipaddr="{self.hmc1_ipaddr, self.hmc1_ipaddr_secondary}" ' \
               f'hmc2_ipaddr="{self.hmc2_ipaddr, self.hmc2_ipaddr_secondary}"'


class Lpar(Base):
    __tablename__ = 'lpar'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, ForeignKey('host.hostname'), unique=True)
    lpar_id: str = Column(String)
    sys_name: str = Column(String, ForeignKey('sys.name'))
    state: str = Column(String)
    curr_profile: str = Column(String)
    os: str = Column(String)
    min_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    desired_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    max_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    min_procs: int = Column(Integer)
    desired_procs: int = Column(Integer)
    max_procs: int = Column(Integer)
    min_mem: int = Column(Integer)
    desired_mem: int = Column(Integer)
    max_mem: int = Column(Integer)
    ufk_code: str = Column(String, ForeignKey('ufk.code'))
    host = relationship('Host', uselist=False, back_populates='lpar')
    prof = relationship('LparProf', uselist=False, back_populates='lpar')
    sys = relationship('Sys', back_populates='lpar')
    vg = relationship('Vg', back_populates='lpar')
    fcs = relationship('Fcs', back_populates='lpar')
    fcs_map = relationship('FcsMap', back_populates='lpar')
    pv = relationship('Pv', back_populates='lpar')
    ufk = relationship('Ufk', back_populates='lpar')

    def __repr__(self):
        return f'Lpar(name="{self.name}", ' \
               f'lpar_id="{self.lpar_id}", ' \
               f'sys_name="{self.sys_name}", ' \
               f'os="{self.os}", ' \
               f'proc_units="{self.desired_proc_units}", ' \
               f'procs="{self.desired_procs}", ' \
               f'mem="{self.desired_mem}")'


class LparProf(Base):
    __tablename__ = 'lparprof'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, ForeignKey('lpar.name'), unique=True)
    sys_name: str = Column(String, ForeignKey('sys.name'))
    min_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    desired_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    max_proc_units: float = Column(Float(asdecimal=True, decimal_return_scale=1))
    min_procs: int = Column(Integer)
    desired_procs: int = Column(Integer)
    max_procs: int = Column(Integer)
    min_mem: int = Column(Integer)
    desired_mem: int = Column(Integer)
    max_mem: int = Column(Integer)
    lpar = relationship('Lpar', uselist=False, back_populates='prof')

    def __repr__(self):
        return f'LparProf(name="{self.name}", ' \
               f'sys_name="{self.sys_name}", ' \
               f'proc_units="{self.desired_proc_units}", ' \
               f'procs="{self.desired_procs}", ' \
               f'mem="{self.desired_mem}")'


class Vg(Base):
    __tablename__ = 'vg'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    size: int = Column(Integer)
    lpar_name: str = Column(String, ForeignKey('lpar.name'))
    lpar = relationship('Lpar', back_populates='vg')
    pv = relationship('Pv', back_populates='vg')

    def __repr__(self):
        return f'Vg(name="{self.name}", size="{self.size}", lpar_name="{self.lpar_name}")'


class Fcs(Base):
    __tablename__ = 'fcs'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    wwn: str = Column(String)
    lpar_name: str = Column(String, ForeignKey('lpar.name'))
    lpar = relationship('Lpar', back_populates='fcs')

    def __repr__(self):
        return f'Fcs(name="{self.name}", wwn="{self.wwn}")'


class FcsMap(Base):
    __tablename__ = 'fcs_map'
    id: int = Column(Integer, primary_key=True)
    lpar_name: str = Column(String, ForeignKey('lpar.name'))
    clntid: str = Column(String)
    clntname: str = Column(String)
    fc: str = Column(String)
    vfcclient: str = Column(String)
    lpar = relationship('Lpar', back_populates='fcs_map')

    def __repr__(self):
        return f'Fcs_Map(lpar_name="{self.lpar_name}",' \
               f' clntid="{self.clntid}", clntname="{self.clntname}", fc="{self.fc}")'


class Pv(Base):
    __tablename__ = 'pv'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    vg_id: int = Column(Integer, ForeignKey('vg.id'))
    vg_name: str = Column(String)
    lpar_name: str = Column(String, ForeignKey('lpar.name'))
    size: int = Column(Integer)
    vg = relationship('Vg', back_populates='pv')
    lpar = relationship('Lpar', back_populates='pv')

    def __repr__(self):
        return f'Pv(name="{self.name}", size="{self.size}", vg_name="{self.vg_name}", lpar_name="{self.lpar_name}")'


class Ufk(Base):
    __tablename__ = 'ufk'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    code: str = Column(String, unique=True)
    lpar = relationship('Lpar', back_populates='ufk')

    def __repr__(self):
        return f'Ufk(name="{self.name}", code="{self.code}")'


Base.metadata.create_all(engine)
