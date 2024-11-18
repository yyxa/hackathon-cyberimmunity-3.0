import os
import sys
import unittest


__location__: str = os.path.dirname(os.path.abspath(__file__))
monitor_path: str = os.path.join(__location__,
                                 os.pardir,
                                 'cars', 'modules', 'car-monitor', 'module')

if not os.path.exists:
    print('failed to find policies in', monitor_path)
    exit(1)
else:
    sys.path.insert(1, monitor_path)
    from policies import policies, check_operation


length: int = len(policies)
event_id: int = 0


# def next_event(self) -> int:
#     global event_id

#     event_id += 1
#     return event_id


class TestOperation(unittest.TestCase):
    event_id = 0

    def next_event(self) -> int:
        self.event_id += 1
        return self.event_id

    def test_true(self):
        result = check_operation(self.next_event(), {
            'source': policies[1]['src'],
            'deliver_to': policies[1]['dst']
        })

        self.assertEqual(result, True)

    def test_false(self):
        result = check_operation(self.next_event(), {
            'source': 'foo',
            'deliver_to': 'bar'
        })

        self.assertEqual(result, False)

    def test_true2(self):
        result = check_operation(self.next_event(), {
            'source': policies[2]['src'],
            'deliver_to': policies[2]['dst']
        })

        self.assertEqual(result, True)

    def test_blank(self):
        result = check_operation(self.next_event(), {
            'source': '',
            'deliver_to': ''
        })

        self.assertEqual(result, False)

    def test_car_network(self):
        ops = (
            ('car-verify-service', 'car-network', True),
            ('car-verify-payment', 'car-network', True),
            ('car-control', 'car-network', True),
            ('car-network', 'car-verify-service', True),
            ('car-network', 'car-control', True),
            ('car-network', 'car-verify-geodata', True),

            ('car-gps', 'car-network', False),
            ('car-complex', 'car-network', False),
            ('car-get-speed-from-geo', 'car-network', False),
            ('car-verify-speed', '', False),
            ('car-engine', 'car-network', False),
            ('car-speed-lower', 'car-network', False),
            ('car-verify-driver', 'car-network', False)
        )

        for op in ops:
            result = check_operation(self.next_event(), {
                'source': op[0],
                'deliver_to': op[1]
            })

            self.assertEqual(result, op[2])

    def test_car_verify_service(self):
        ops = (
            ('car-network', 'car-verify-service', True),
            ('car-verify-payment', 'car-verify-service', True),
            ('car-verify-service', 'car-verify-service', False),
            ('car-control', 'car-verify-service', False),
            ('', 'car-verify-service', False),
            ('car-verify-service', '', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_verify_payment(self):
        ops = (
            ('car-verify-service', 'car-verify-payment', True),
            ('car-network', 'car-verify-payment', False),
            ('car-verify-payment', 'car-manager-service', True),
            ('', 'car-verify-payment', False),
            ('car-verify-payment', '', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_control(self):
        ops = (
            ('car-network', 'car-control', True),
            ('car-verify-service', 'car-control', True),
            ('car-verify-geodata', 'car-control', True),
            ('car-get-speed-from-geo', 'car-control', True),
            ('car-verify-speed', 'car-control', True),
            ('car-verify-driver', 'car-control', True),
            ('car-control', 'car-network', True),
            ('car-control', 'car-complex', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_verify_geodata(self):
        ops = (
            ('car-complex', 'car-verify-geodata', True),
            ('car-network', 'car-verify-geodata', True),
            ('car-adas', 'car-verify-geodata', True),
            ('data', 'car-verify-geodata', True),
            ('car-verify-geodata', 'car-verify-geodata', False),
            ('car-gps', 'car-verify-geodata', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_data(self):
        ops = (
            ('car-verify-geodata', 'car-data', True),
            ('car-verify-speed', 'car-data', True),
            ('car-data', 'car-data', False),
            ('car-network', 'car-data', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_get_speed_from_geo(self):
        ops = (
            ('car-gps', 'car-get-speed-from-geo', True),
            ('car-glonass', 'car-get-speed-from-geo', True),
            ('car-complex', 'car-get-speed-from-geo', False),
            ('car-verify-service', 'car-get-speed-from-geo', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_monitoring(self):
        ops = (
            ('car-verify-payment', 'car-monitoring', True),
            ('car-energy', 'car-monitoring', True),
            ('car-skin-sensors', 'car-monitoring', True),
            ('car-monitoring', 'car-engine', True),
            ('car-monitoring', 'car-monitoring', False),
            ('car-verify-service', 'car-monitoring', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])

    def test_car_engine(self):
        ops = (
            ('car-monitoring', 'car-engine', True),
            ('car-control', 'car-engine', True),
            ('car-verify-driver', 'car-engine', True),
            ('car-engine', 'car-engine', False),
            ('car-network', 'car-engine', False),
        )
        for op in ops:
            result = check_operation(self.next_event(), {'source': op[0], 'deliver_to': op[1]})
            self.assertEqual(result, op[2])


if __name__ == '__main__':
    unittest.main(verbosity=2)
