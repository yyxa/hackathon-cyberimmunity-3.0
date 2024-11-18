import os
import json
import threading

from uuid import uuid4
import uuid
from confluent_kafka import Consumer, OFFSET_BEGINNING

from .producer import proceed_to_deliver


MODULE_NAME: str = os.getenv("MODULE_NAME")

skin_data = []
energy_data = []
need_to_check = []

def send_to_engine(details):
    details["deliver_to"] = "car-engine"
    details["operation"] = "stop"
    proceed_to_deliver(str(uuid.uuid4()), details)

def write_data_skin(details):
    skin_data.append(details["data"])

def write_data_energy(details):
    energy_data.append(details["data"])
    
def need_to_check(details):
    need_to_check.append(details["data"])
    
def handle_event(id, details_str):
    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)

    source: str = details.get("source")
    deliver_to: str = details.get("deliver_to")
    data: str = details.get("data")
    operation: str = details.get("operation")

    print(f"[info] handling event {id}, "
          f"{source}->{deliver_to}: {operation}")

    if operation == "data_from_skin_sensors":
        return write_data_skin(details)
    elif operation == "data_from_energy":
        return write_data_energy(details)
    elif operation == "monitor_this":
        return need_to_check(details)

def consumer_job(args, config):
    consumer = Consumer(config)

    def reset_offset(verifier_consumer, partitions):
        if not args.reset:
            return

        for p in partitions:
            p.offset = OFFSET_BEGINNING
        verifier_consumer.assign(partitions)

    topic = MODULE_NAME
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    handle_event(id, details_str)
                except Exception as e:
                    print(f"[error] Malformed event received from " \
                          f"topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()

def start_consumer(args, config):
    print(f'{MODULE_NAME}_consumer started')
    threading.Thread(target=lambda: consumer_job(args, config)).start()