import serial
import time
from enum import Enum

serial_port_id = "COM10"

import unittest

# See mode.h's mode_type in midi_cv_gate_firmware
class System_Mode(Enum):
    FIRST_PRIO_POLY = 0
    MODE_32_GATES = 1
    FIRST_PRIO_POLY_QUAD_HARMONIC = 2
    DRONE = 3
    TEST_MODE = 4
    CNT = 5
    CONFIG = CNT + 1  # After SYSTEM_MODE_CNT so it isn't saved.
    DEFAULT = FIRST_PRIO_POLY


class Midi_CV_Gate_Test(unittest.TestCase):
    """
    Base class for test suite. Common setUp and utility functions.
    """

    _voltage_map = None  # first caller of _read_voltage_map() sets this.

    @classmethod
    def setUpClass(cls):
        cls._read_voltage_map("calibration\cal_vals_converted.txt")
        cls.ser = serial.Serial()
        cls.ser.baudrate = 115200
        cls.ser.port = serial_port_id
        cls.ser.timeout = 1
        cls.ser.open()
        time.sleep(1.5)  # Necessary delay (on windows) so first messages aren't lost.

    @classmethod
    def tearDownClass(cls):
        cls.ser.close()

    @classmethod
    def send_command_return_response(cls, command="read_digital", verbose=False):
        """
        Send a command to the test fixture and read the response.
        """
        cls.ser.write(bytearray("{}\n".format(command), "ascii"))
        # ser.flush()
        time.sleep(0.2)
        # read the echo'd command
        result = cls.ser.read_until().decode("ascii").rstrip("\n")
        # print(result)
        # read the response
        result = cls.ser.read_until().decode("ascii").rstrip("\n").rstrip("\r")
        if verbose:
            print(result)
        return result

    def setUp(self):
        self.send_command_return_response(command="switch_on")
        time.sleep(0.2)
        self.send_command_return_response(command="switch_off")
        pass

    def tearDown(self):
        pass

    def check_digital_values(self, expected_values):
        expected_response = f"digital_values={expected_values}"
        actual_response = self.send_command_return_response(command="read_digital")
        self.assertEqual(expected_response, actual_response)

    def change_dut_mode(self, mode: System_Mode):
        # print(f"change to mode {mode.name} ({mode.value})")
        response = self.send_command_return_response(
            command=f"midi_change_mode={mode.value}"
        )
        self.assertEqual("sent", response)

    def all_sound_off(self):
        response = self.send_command_return_response(command=f"midi_all_sound_off")
        self.assertEqual("sent", response)

    def all_notes_off(self):
        response = self.send_command_return_response(command=f"midi_all_notes_off")
        self.assertEqual("sent", response)

    def check_cvs_are_off(self):
        expected_voltages = "voltages=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)

    def check_all_off(self):
        self.check_digital_values("0000")
        self.check_cvs_are_off()

    def compare_analog_values(self, expected_value, actual_value, tolerance=5):
        """
        Compare the analog values returned from the test fixture with an expected set of values.
        """
        if expected_value == actual_value:
            return (True, "Exact Match")

        if not actual_value.startswith("analog_values="):
            return (False, 'actual_value missing "analog_values="')

        if not expected_value.startswith("analog_values="):
            return (False, 'expected_value missing "analog_values="')

        expected_values = (
            expected_value.replace("analog_values=", "").rstrip(",").split(",")
        )
        actual_values = (
            actual_value.replace("analog_values=", "").rstrip(",").split(",")
        )

        if len(expected_values) != 16:
            return (False, "expected_value doesn't contain 16 entries")

        if len(actual_values) != 16:
            return (False, "actual_values doesn't contain 16 entries")

        try:
            expected_values = [int(a, base=16) for a in expected_values]
        except ValueError as e:
            return (False, "expected_value doesn't contain hex integers")

        try:
            actual_values = [int(a, base=16) for a in actual_values]
        except ValueError as e:
            return (False, "actual_value doesn't contain hex integers")

        msg = ""
        for idx, (ev, av) in enumerate(zip(expected_values, actual_values)):
            if abs(ev - av) > tolerance:
                msg += f"actual_value[{idx}]={av} is too far from expected_value[{idx}]={ev}\n"
        if msg != "":
            return (False, msg)

        return (True, "Close Match")

    def compare_analog_values_to_voltages(
        self, expected_voltage, actual_value, tolerance=0.01
    ):
        """
        Compare the analog values returned from the test fixture with an expected set of values.
        """
        if not actual_value.startswith("analog_values="):
            return (False, 'actual_value missing "analog_values="')

        if not expected_voltage.startswith("voltages="):
            return (False, 'expected_voltage missing "voltages="')

        expected_voltages = (
            expected_voltage.replace("voltages=", "").rstrip(",").split(",")
        )
        actual_values = (
            actual_value.replace("analog_values=", "").rstrip(",").split(",")
        )

        if len(expected_voltages) != 16:
            return (False, "expected_voltage doesn't contain 16 entries")

        if len(actual_values) != 16:
            return (False, "actual_values doesn't contain 16 entries")

        try:
            expected_voltages = [float(a) for a in expected_voltages]
        except ValueError as e:
            return (False, "expected_voltage doesn't contain floats")

        try:
            actual_values = [[int(a, base=16)] for a in actual_values]
        except ValueError as e:
            return (False, "actual_value doesn't contain hex integers")

        actual_voltages = [
            a[0] for a in self.convert_data_to_voltage(actual_values, 16)
        ]
        # print(actual_voltages)

        msg = ""
        for idx, (ev, av) in enumerate(zip(expected_voltages, actual_voltages)):
            if abs(ev - av) > tolerance:
                msg += f"actual_voltage[{idx}]={av} is too far from expected_voltage[{idx}]={ev} ({abs(ev - av)} V)\n"
        if msg != "":
            return (False, msg)

        return (True, "Close Match")

    @classmethod
    def convert_data_to_voltage(cls, data, max_cvs):
        cvs = list(range(0, max_cvs))

        data_out = []

        for cv in cvs:
            data_out.append(
                [cls._voltage_from_voltage_map(cv, value) for value in data[cv]]
            )

        return data_out

    @classmethod
    def _read_voltage_map(cls, file_name):
        cls._voltage_map = []
        with open(file_name, "r") as f:
            for line in f:
                vals = line.rstrip("\n").rstrip("\r").rstrip(",").split(",")

                cls._voltage_map.append(
                    {
                        "voltage": float(vals[0].replace("V", "")),
                        "adc_vals": [float(a) for a in vals[1:]],
                    }
                )

    @classmethod
    def _voltage_from_voltage_map(cls, cv, value):
        lower_voltage_idx = 0
        upper_voltage_idx = -1
        for i, voltage in enumerate(cls._voltage_map):
            if (
                value >= cls._voltage_map[lower_voltage_idx]["adc_vals"][cv]
                and value < voltage["adc_vals"][cv]
            ):
                upper_voltage_idx = i
                break
            else:
                lower_voltage_idx = i

        upper_voltage_val = cls._voltage_map[upper_voltage_idx]["adc_vals"][cv]
        lower_voltage_val = cls._voltage_map[lower_voltage_idx]["adc_vals"][cv]
        upper_voltage = cls._voltage_map[upper_voltage_idx]["voltage"]
        lower_voltage = cls._voltage_map[lower_voltage_idx]["voltage"]

        s = "Value {} is between {} and {} and voltages {} and {}".format(
            value, lower_voltage_val, upper_voltage_val, lower_voltage, upper_voltage
        )

        value_voltage = lower_voltage + (
            (value - lower_voltage_val)
            * (upper_voltage - lower_voltage)
            / (upper_voltage_val - lower_voltage_val)
        )
        s = "Value {} is between {} and {} and voltages {} and {}, so {}".format(
            value,
            lower_voltage_val,
            upper_voltage_val,
            lower_voltage,
            upper_voltage,
            value_voltage,
        )
        # print(s)
        return value_voltage


if __name__ == "__main__":
    unittest.main()
