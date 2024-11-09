from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass()
class Event:
    scheduled_start: datetime
    actual_start: datetime
    completed: datetime
    domain_name: str
    schedule_name: str
    node_name: str
    schedule_type: str
    status: str
    result: str
    reason: str
    rman_log: str = None

    def __repr__(self):
        return f"\n{self.domain_name:<8}" \
               f"{self.schedule_type:<8}" \
               f"{self.node_name:<12}" \
               f"{self.scheduled_start}{'':<5}" \
               f"{self.completed}{'':<5}" \
               f"{self.status:<8}" \
               f"{self.result:<2}" \
               f"{self.reason}\n{self.rman_log}"


@dataclass()
class RmanLogFile:
    node_name: str = None
    schedule_type: str = None
    text: str = None
    offset: timedelta = None
