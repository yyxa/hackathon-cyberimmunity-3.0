import os
import json
import random
import threading

import time
from uuid import uuid4
import uuid
from confluent_kafka import Consumer, OFFSET_BEGINNING
from pathlib import Path
import json
from .producer import proceed_to_deliver


MODULE_NAME: str = os.getenv("MODULE_NAME")

class Car:
    def __init__(self, brand, has_air_conditioner=False, has_heater=False, has_navigator=False):
        self.speed = 0
        self.coordinates = (0, 0)
        self.occupied_by = None
        self.start_time = None
        self.brand = brand
        self.has_air_conditioner = has_air_conditioner
        self.has_heater = has_heater
        self.has_navigator = has_navigator
        self.is_running = False
        self.tariff = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            return f"{self.brand} поездка началась."
        else:
            return f"{self.brand} поездка ещё идет."

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.speed = 0
            self.occupied_by = None
            return f"{self.brand} поездка завершена."
        else:
            return f"{self.brand} на парковке."

    def get_status(self):
        elapsed_time = 0
        if self.start_time is not None and self.is_running:
            elapsed_time = round(time.time() - self.start_time, 2)  # Время в секундах
        return {
            "brand": self.brand,
            "is_running": self.is_running,
            "speed": self.speed,
            "coordinates": self.coordinates,
            "occupied_by": self.occupied_by,
            "trip_time": elapsed_time,
            "has_air_conditioner": self.has_air_conditioner,
            "has_heater": self.has_heater,
            "has_navigator": self.has_navigator,
            "tariff ": self.tariff
        }

    def update_coordinates(self, x, y):
        self.coordinates = (x, y)

    def set_speed(self, speed):
        if self.is_running:
            self.speed = speed
            return f"Скорость {self.brand} изменена на {self.speed} км/ч."
        else:
            return f"{self.brand} не парковке, скорость не может быть изменена."

    def occupy(self, person, tarif):
        self.occupied_by = person
        self.tariff = tarif
        return f"{self.brand} арендован {self.occupied_by}."
    
# Функция для загрузки автомобилей из JSON файла
def load_cars_from_json(cars_json):
    return [Car(**car) for car in cars_json]


cars_json = [
    {
        "brand": "Toyota",
        "has_air_conditioner": True,
        "has_heater": False,
        "has_navigator": True 
    },
    {
        "brand": "Honda",
        "has_air_conditioner": False,
        "has_heater": True,
        "has_navigator": False 
    },
    {
        "brand": "Ford",
        "has_air_conditioner": True,
        "has_heater": True,
        "has_navigator": True
    }
]

cars = load_cars_from_json(cars_json)

def get_cars(details):
    details["operation"] = "cars"
    details["data"] = [car.get_status() for car in cars]

    return send_to_network(str(uuid.uuid4()), details)
    
def get_car(details):
    brand = details["brand"]
    details["operation"] = "car"
    car = next((car for car in cars if car.brand.lower() == brand.lower()), None)
    if car:
        details["data"] = car.get_status()
        return send_to_network(str(uuid.uuid4()), details)
    else:
        details["data"] = {"error": "Автомобиль не найден."}
        return send_to_network(str(uuid.uuid4()), details)

def simulate_drive(car):
    while car.is_running:
        new_speed = random.randint(10, 100)
        car.set_speed(new_speed)

        x_change = random.uniform(-2, 2)
        y_change = random.uniform(-2, 2)
        current_coordinates = car.coordinates
        new_coordinates = (current_coordinates[0] + x_change, current_coordinates[1] + y_change)
        car.update_coordinates(*new_coordinates)

        print(f"{car.brand} Скорость: {car.speed:.2f} км/ч, Координаты: {car.coordinates}")
        
        details = {
        "operation": "telemetry_response",
        "brand": car.brand,
        "status": car.get_status()
        }
        send_to_network(str(uuid.uuid4()), details)
        time.sleep(1)
        
def car_start(details):
    brand = details["brand"]
    details["operation"] = "car_start_response"
    
    car = next((car for car in cars if car.brand.lower() == brand.lower()), None)
    if car:
        message = car.start()
        thread = threading.Thread(target=simulate_drive, args=(car))
        thread.start()
        details["data"] = {"message": message}
        return send_to_network(str(uuid.uuid4()), details)
    else:
        details["data"] = {"error": "Автомобиль не найден."}
        return send_to_network(str(uuid.uuid4()), details)
    
def car_stop(details):
    brand = details["brand"]
    details["operation"] = "return"
    car = next((car for car in cars if car.brand.lower() == brand.lower()), None)
    if car:
        status = car.get_status()
        details["occupied_by"] = car.occupied_by
        details["status"] = status
        
        return send_to_network(str(uuid.uuid4()), details)
        
    else:
        details["data"] = {"error": "Автомобиль не найден."}
        return send_to_network(str(uuid.uuid4()), details)
    
def invoice_id(details):
    details["operation"] = "invoice_id_response"
    invoice_id = details["invoice_id"]
    brand = details["brand"]
    car = next((car for car in cars if car.brand.lower() == brand.lower()), None)
    
    if details["invoice_id_status_code"] == 200:
        message = car.stop()
        details["data"] = {"message": message, 'invoice_id': invoice_id}
        return send_to_network(str(uuid.uuid4()), details)
    else:
        message = car.stop()
        details["data"] = {"message": message}
        return send_to_network(str(uuid.uuid4()), details)

def occupy(details):
    details["operation"] = "occupy_response"
    brand = details["brand"]
    person = details["person"]
    car = next((car for car in cars if car.brand.lower() == brand.lower()), None)
    if car and details["person"] is not None:
        tariff = details["tariff"]
        message = car.occupy(person, tariff)
        details["data"] = {"access": True, "car": car.brand, "message": message}
        return send_to_network(str(uuid.uuid4()), details)
    else:
        details["data"] = {"access": False, "message": "Автомобиль не найден или не указан клиент."}
        return send_to_network(str(uuid.uuid4()), details) 

def driver_verify_data(details):
    return
              
def send_to_network(id, details):
    details["deliver_to"] = "car-network"
    proceed_to_deliver(id, details)


def handle_event(id, details_str):
    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)

    source: str = details.get("source")
    deliver_to: str = details.get("deliver_to")
    data: str = details.get("data")
    operation: str = details.get("operation")

    print(f"[info] handling event {id}, "
          f"{source}->{deliver_to}: {operation}")

    if operation == "get_cars":
        return get_cars(details)
    elif operation == "get_car":
        return get_car(details)
    elif operation == "car_start":
        return car_start(details)
    elif operation == "car_stop":
        return car_stop(details)
    elif operation == "invoice_id":
        return invoice_id(details)
    elif operation == "occupy":
        return occupy(details)
    elif operation == "car-driver-verify-data":
        return driver_verify_data(details)
    # elif operation == "answer_cars":
    #     details["data"] = [car['brand'] for car in data if car['occupied_by'] is None]
    #     return send_to_profile_client(id, details)
    # elif operation == "get_status":
    #     return send_to_verify(id, details)
    # elif operation == "answer_status":
    #     return send_to_profile_client(id, details)
    # elif operation == "access":
    #     return send_to_profile_client(id, details)
    # elif operation == "confirm_access":
    #     return send_to_verify(id, details)
    # elif operation == "return":
    #     return send_to_profile_client(id, details)
    # elif operation == "telemetry":
    #     speed = data.get('speed')
    #     coordinates = data.get('coordinates')
    #     print(f"{details["car"]} Скорость: {speed:.2f} км/ч, Координаты: {coordinates}")


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