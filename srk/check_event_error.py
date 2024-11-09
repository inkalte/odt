from share.misc import timeit
from sqlalchemy.orm import Session, sessionmaker
from env import logger
from srk import Event, engine


@timeit
def check_event_error():
    event_for_check = get_event_for_check()
    check_error(event_for_check)


def check_error(event_for_check: {}):
    for node_name, events in event_for_check.items():
        print(node_name.rstrip('_ORACLE'))
        for event in events:
            print('\t', event)


def get_event_for_check() -> []:
    session: Session = sessionmaker(bind=engine)()
    events_dict = {}
    events = session.query(Event).filter(Event.status == 'Failed', ~Event.checked).order_by(Event.type).all()
    logger.info(f'event for check {len(events)}')
    for event in events:
        if events_dict.get(event.node_name):
            events_dict[event.node_name].append(event)
        else:
            events_dict[event.node_name] = [event, ]
    return events_dict


if __name__ == '__main__':
    check_event_error()
