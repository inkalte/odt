from dataclasses import dataclass


@dataclass
class DsmClientStatus:
    host: str
    output: str = ''
    dsmc_count: int = 0
    dsmcad_count: int = 0

    def __repr__(self):
        return f"DCS(host='{self.host}', dsmc_count={self.dsmc_count}, dsmcad_count={self.dsmcad_count})"
