import requests
import time


MOBILE_URL = 'http://0.0.0.0:8002'
client = {"name": "Иван Иванов", "experience": 1}

# Тест базового сценария поездки клиента от аренды до завершения поездки
def test_full_func():
    prepayment = requests.post(f'{MOBILE_URL}/cars', json=client)
    response = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment.json())
    car = requests.post(f'{MOBILE_URL}/start_drive', json=client)
    time.sleep(5)  # Сколько времени будет длиться поездка
    invoice = requests.post(f'{MOBILE_URL}/stop_drive', json=client)
    response = requests.post(f'{MOBILE_URL}/final_pay', json=invoice.json())
    assert response.status_code == 200
    data = response.json()
    assert 'car' in data
    assert 'created_at' in data
    assert 'elapsed_time' in data
    assert 'name' in data
    assert 'final_amount' in data
    assert 'tarif' in data


client2 = {"name": "Иван Иванов", "experience": 1}
client3 = {"name": "Иван Машков", "experience": 10}

def test_multiple_clients():
    prepayment_client1 = requests.post(f'{MOBILE_URL}/cars', json=client2)
    response_client1 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client1.json())
    car_client1 = requests.post(f'{MOBILE_URL}/start_drive', json=client2)
    time.sleep(5)
    prepayment_client2 = requests.post(f'{MOBILE_URL}/cars', json=client3)
    response_client2 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client2.json())
    car_client2 = requests.post(f'{MOBILE_URL}/start_drive', json=client3)
    time.sleep(5)
    invoice_client1 = requests.post(f'{MOBILE_URL}/stop_drive', json=client2)
    final_pay_client1 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client1.json())
    
    assert final_pay_client1.status_code == 200
    data_client1 = final_pay_client1.json()
    assert 'car' in data_client1
    assert 'created_at' in data_client1
    assert 'elapsed_time' in data_client1
    assert 'name' in data_client1
    assert 'final_amount' in data_client1
    assert 'tarif' in data_client1

    time.sleep(5)
    invoice_client2 = requests.post(f'{MOBILE_URL}/stop_drive', json=client3)
    final_pay_client2 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client2.json())
    
    assert final_pay_client2.status_code == 200
    data_client2 = final_pay_client2.json()
    assert 'car' in data_client2
    assert 'created_at' in data_client2
    assert 'elapsed_time' in data_client2
    assert 'name' in data_client2
    assert 'final_amount' in data_client2
    assert 'tarif' in data_client2

    # Дополнительно проверяем, что оба клиента получили разные автомобили
    assert data_client1['car'] != data_client2['car']

client2 = {"name": "Иван Иванов", "experience": 1}
client3 = {"name": "Иван Машков", "experience": 10}
client4 = {"name": "Вова Ширинкин", "experience": 5}

def test_triple_clients():
    prepayment_client1 = requests.post(f'{MOBILE_URL}/cars', json=client2)
    response_client1 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client1.json())
    car_client1 = requests.post(f'{MOBILE_URL}/start_drive', json=client2)
    time.sleep(5)


    prepayment_client2 = requests.post(f'{MOBILE_URL}/cars', json=client3)
    response_client2 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client2.json())
    car_client2 = requests.post(f'{MOBILE_URL}/start_drive', json=client3)
    time.sleep(7)


    invoice_client1 = requests.post(f'{MOBILE_URL}/stop_drive', json=client2)
    final_pay_client1 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client1.json())

    assert final_pay_client1.status_code == 200
    data_client1 = final_pay_client1.json()
    assert 'car' in data_client1
    assert 'created_at' in data_client1
    assert 'elapsed_time' in data_client1
    assert 'name' in data_client1
    assert 'final_amount' in data_client1
    assert 'tarif' in data_client1


    prepayment_client3 = requests.post(f'{MOBILE_URL}/cars', json=client4)
    response_client3 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client3.json())
    car_client3 = requests.post(f'{MOBILE_URL}/start_drive', json=client4)
    time.sleep(10)


    invoice_client2 = requests.post(f'{MOBILE_URL}/stop_drive', json=client3)
    final_pay_client2 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client2.json())

    assert final_pay_client2.status_code == 200
    data_client2 = final_pay_client2.json()
    assert 'car' in data_client2
    assert 'created_at' in data_client2
    assert 'elapsed_time' in data_client2
    assert 'name' in data_client2
    assert 'final_amount' in data_client2
    assert 'tarif' in data_client2


    invoice_client3 = requests.post(f'{MOBILE_URL}/stop_drive', json=client4)
    final_pay_client3 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client3.json())

    assert final_pay_client3.status_code == 200
    data_client3 = final_pay_client3.json()
    assert 'car' in data_client3
    assert 'created_at' in data_client3
    assert 'elapsed_time' in data_client3
    assert 'name' in data_client3
    assert 'final_amount' in data_client3
    assert 'tarif' in data_client3


    assert data_client1['car'] != data_client2['car']
    assert data_client1['car'] != data_client3['car']
    assert data_client2['car'] != data_client3['car']

def test_3_in_row():
    prepayment_client1 = requests.post(f'{MOBILE_URL}/cars', json=client2)
    response_client1 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client1.json())
    car_client1 = requests.post(f'{MOBILE_URL}/start_drive', json=client2)
    time.sleep(1)
    prepayment_client2 = requests.post(f'{MOBILE_URL}/cars', json=client3)
    response_client2 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client2.json())
    car_client2 = requests.post(f'{MOBILE_URL}/start_drive', json=client3)
    time.sleep(1)
    prepayment_client3 = requests.post(f'{MOBILE_URL}/cars', json=client4)
    response_client3 = requests.post(f'{MOBILE_URL}/prepayment', json=prepayment_client3.json())
    car_client3 = requests.post(f'{MOBILE_URL}/start_drive', json=client4)
    time.sleep(1)
    invoice_client1 = requests.post(f'{MOBILE_URL}/stop_drive', json=client2)
    final_pay_client1 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client1.json())
    assert final_pay_client1.status_code == 200

    invoice_client2 = requests.post(f'{MOBILE_URL}/stop_drive', json=client3)
    final_pay_client2 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client2.json())
    assert final_pay_client2.status_code == 200

    invoice_client3 = requests.post(f'{MOBILE_URL}/stop_drive', json=client4)
    final_pay_client3 = requests.post(f'{MOBILE_URL}/final_pay', json=invoice_client3.json())
    assert final_pay_client3.status_code == 200
