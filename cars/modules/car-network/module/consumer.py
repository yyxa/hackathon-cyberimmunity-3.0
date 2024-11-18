import os
import json
import threading
import uuid
import requests
import multiprocessing
from confluent_kafka import Consumer, OFFSET_BEGINNING

from .producer import proceed_to_deliver

PAYMENT_URL = 'http://payment_system:8000'
MANAGMENT_URL = 'http://management_system:8000'
MOBILE_URL = 'http://mobile-client:8000'
_response_queue: multiprocessing.Queue = None
MODULE_NAME = os.getenv("MODULE_NAME")

# def send_to_car_control(details):
#     details["deliver_to"] = "car-control"
#     proceed_to_deliver(str(uuid.uuid4()), details)

def send_to_car_verify_service(details):
    details["deliver_to"] = "car-verify-service"
    proceed_to_deliver(str(uuid.uuid4()), details)
    
def send_telemetry_to_managment(details):
    requests.post(f'{MANAGMENT_URL}/telemetry/{details["brand"]}', json={'status': details["status"]})

def send_return_to_managment(details):
    invoice_id = requests.post(f'{MANAGMENT_URL}/return/{details["occupied_by"]}', json={'status': details["status"]})
    details["operation"] = "invoice_id"
    details["invoice_id"] = invoice_id.json()['id']
    details["invoice_id_status_code"] = invoice_id.status_code

    send_to_car_verify_service(details)

def send_to_managment(details):
    _response_queue.put(details)
    
def handle_event(id, details_str):

    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)

    source: str = details.get("source")
    deliver_to: str = details.get("deliver_to")
    data: str = details.get("data")
    operation: str = details.get("operation")

    print(f"[info] handling event {id}, "
          f"{source}->{deliver_to}: {operation}")

    if operation == "telemetry_response":
        return send_telemetry_to_managment(details)
    elif operation == "return":
        return send_return_to_managment(details)
    elif operation == "cars":
        return send_to_managment(details)
    elif operation == "car":
        return send_to_managment(details)
    elif operation == "occupy_response":
        return send_to_managment(details)
    elif operation == "invoice_id_response":
        return send_to_managment(details)
    elif operation == "car_start_response":
        return send_to_managment(details)
        
    

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


def start_consumer(args, config, response_queue):
    global _response_queue
    _response_queue = response_queue
    print(f'{MODULE_NAME}_consumer started')

    threading.Thread(target=lambda: consumer_job(args, config)).start()