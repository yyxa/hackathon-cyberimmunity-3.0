import os
import random
import time
import json
import threading
import multiprocessing

from uuid import uuid4
from flask import Flask, jsonify, abort
import requests
from werkzeug.exceptions import HTTPException


MANAGMENT_URL = 'http://management_system:8000'

_requests_queue: multiprocessing.Queue = None
_response_queue: multiprocessing.Queue = None


HOST = '0.0.0.0'
PORT: int = int(os.getenv("MODULE_PORT"))
MODULE_NAME: str = os.getenv("MODULE_NAME")
MAX_WAIT_TIME: int = 30
app = Flask(__name__)

def send_to_car_control(details):
    if not details:
        abort(400)

    details["deliver_to"] = "car-control"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()

    try:
        _requests_queue.put(details)
        print(f"{MODULE_NAME} update event: {details}")
    except Exception as e:
        print("[COM-MOBILE_DEBUG] malformed request", e)
        abort(400)

def send_to_car_verify_service(details):
    if not details:
        abort(400)

    details["deliver_to"] = "car-verify-service"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()

    try:
        _requests_queue.put(details)
        print(f"{MODULE_NAME} update event: {details}")
    except Exception as e:
        print("[COM-MOBILE_DEBUG] malformed request", e)
        abort(400)
        
def send_to_verify_geo(details):
    if not details:
        abort(400)

    details["deliver_to"] = "car-verify-geodata"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()

    try:
        _requests_queue.put(details)
        print(f"{MODULE_NAME} update event: {details}")
    except Exception as e:
        print("[COM-MOBILE_DEBUG] malformed request", e)
        abort(400)

def send_to_verify_service(details):
    if not details:
        abort(400)

    details["deliver_to"] = "car-verify-service"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()

    try:
        _requests_queue.put(details)
        print(f"{MODULE_NAME} update event: {details}")
    except Exception as e:
        print("[COM-MOBILE_DEBUG] malformed request", e)
        abort(400)
        
def wait_response():
    """ Ожидает завершение выполнения задачи. """
    start_time = time.time()
    while 1:
        if time.time() - start_time > MAX_WAIT_TIME:
            break

        try:
            response = _response_queue.get(timeout=MAX_WAIT_TIME)
        except Exception as e:
            print("timeout...", e)
            continue
        
        # if not isinstance(response, dict):
        #     print("not a dict...")
        #     continue

        data = response.get('data')
        if not data:
            print("something strange...")
            continue

        print("response", response)
        return data

    print("OUT OF TIME...")

    return None

@app.route('/car/status/all', methods=['GET'])
def get_all_car_statuses():
    details_to_send = {
        "operation": "get_cars"
    }
    send_to_car_control(details_to_send)
    data = wait_response()
    return jsonify(data)


@app.route('/car/start/<string:brand>', methods=['POST'])
def start_car(brand):
    details_to_send = {
        "operation": "car_start",
        "brand": brand
    }
    send_to_car_verify_service(details_to_send)
    data = wait_response()
    return jsonify(data)


@app.route('/car/stop/<string:brand>', methods=['POST'])
def stop_car(brand):
    details_to_send = {
        "operation": "car_stop",
        "brand": brand
    }
    send_to_car_verify_service(details_to_send)
    data = wait_response()
    return jsonify(data)


@app.route('/car/status/<string:brand>', methods=['GET'])
def get_car_status(brand):
    details_to_send = {
        "operation": "get_car",
        "brand": brand
    }
    send_to_car_control(details_to_send)
    data = wait_response()
    return jsonify(data)


@app.route('/car/occupy/<string:person>', methods=['POST'])
def occupy_car(person):
    response = requests.post(f'{MANAGMENT_URL}/access/{person}')
    if response.status_code == 200:
        brand = response.json()['car']
        details_to_send = {
            "operation": "occupy",
            "brand": brand,
            "tariff": response.json()['tariff'],
            "person": person
        }
        send_to_car_verify_service(details_to_send)
        data = wait_response()
        return jsonify(data)
    else:
        return jsonify({"access": False, "message": "Доступ до автомобиля не разрешен."}), 404


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    return jsonify({
        "status": e.code,
        "name": e.name,
    }), e.code

    
def start_web(requests_queue, response_queue):
    global _requests_queue
    global _response_queue

    _requests_queue = requests_queue
    _response_queue = response_queue

    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()

