from unittest import TestCase
from decimal import Decimal

from core.steering.steering_controller import _calculate_angle_of_deviation, _angle_to_servo_duration


class Test(TestCase):
    def test__calculate_angle_of_deviation(self):

        # 90 degrees to the right - Q1
        current_read = 0
        set_head = 90

        expected_value = -90
        actual_value = _calculate_angle_of_deviation(current_read, set_head)

        self.assertEqual(expected_value, actual_value)

        # 10 degrees to the left - Q1
        current_read = 90
        set_head = 80

        expected_value = 10
        actual_value = _calculate_angle_of_deviation(current_read, set_head)

        self.assertEqual(expected_value, actual_value)

        # 20 degrees to the left - Q1 -> Q2
        current_read = 10
        set_head = 350

        expected_value = 20
        actual_value = _calculate_angle_of_deviation(current_read, set_head)

        self.assertEqual(expected_value, actual_value)

        # 50 degrees to the right - Q2 -> Q1
        current_read = 340
        set_head = 30

        expected_value = -50
        actual_value = _calculate_angle_of_deviation(current_read, set_head)

        self.assertEqual(expected_value, actual_value)

    def test__angle_to_servo_duration(self):
        self.assertEquals(-1, _angle_to_servo_duration(-90))
        self.assertEquals(-0.5, _angle_to_servo_duration(-45))
        self.assertEquals(0, _angle_to_servo_duration(0))
        self.assertEquals(0.5, _angle_to_servo_duration(45))
        self.assertEquals(1, _angle_to_servo_duration(90))
