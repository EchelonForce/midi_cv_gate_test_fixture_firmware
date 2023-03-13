import serial
import time

"""
This script is used to calibrate the test fixture's ADCs.
One must supply all the ADCs with a voltage and then call this to take five readings.
The result can be averaged and fed back to the test fixture scripts to make sure
the ADCs are giving accurate readings of the DUT.
"""


def main():
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = "COM10"
    ser.timeout = 1
    ser.open()
    time.sleep(1.5)  # some time need (by windows?) to get a messages out correctly

    with open("test_fixture_cal_output.txt", "a") as out_file:

        inp = input("Measure and enter 5VA ref voltage: ")
        ref_volt = float(inp)
        print(f"Ref Volt: {ref_volt} V")
        out_file.write(f"Ref Volt: {ref_volt} V\n")
        for voltage_ideal in [i * 0.5 for i in range(0, 22, 1)]:
            print(f"Input Voltage (ideal): {voltage_ideal} V")
            inp = input("Measure and enter actual input voltage: ")
            actual_volt = float(inp)
            print(f"Actual Volt: {actual_volt} V")
            out_file.write(f"Actual Volt: {actual_volt} V\n")

            for num_readings in range(0, 6):
                readings = send_command_return_response(ser, command="read_analog")
                out_file.write(f"{readings}\n")
            out_file.flush()

    ser.close()


def send_command_return_response(ser, command="read_digital"):
    ser.write(bytearray("{}\n".format(command), "ascii"))
    # ser.flush()
    time.sleep(0.2)
    # read the echo'd command
    result = ser.read_until().decode("ascii").rstrip("\n")
    print(result)
    # read the response
    result = ser.read_until().decode("ascii").rstrip("\n")
    print(result)
    return result


if __name__ == "__main__":
    main()
