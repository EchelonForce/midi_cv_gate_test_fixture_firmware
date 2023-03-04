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
    ser.port = "COM8"
    ser.timeout = 1
    ser.open()
    time.sleep(1.5)  # some time need (by windows?) to get a messages out correctly

    send_command_return_response(ser, command="read_analog")
    send_command_return_response(ser, command="read_analog")
    send_command_return_response(ser, command="read_analog")
    send_command_return_response(ser, command="read_analog")
    send_command_return_response(ser, command="read_analog")

    # send_command_return_response(ser, command="switch_on")
    # time.sleep(0.3)
    # send_command_return_response(ser, command="switch_off")
    # send_command_return_response(ser, command="read_digital")
    # send_command_return_response(ser, command="read_analog")
    # for i in range(45, 45 + 9):
    #     send_command_return_response(ser, command="midi_note_on={}".format(i))
    # send_command_return_response(ser, command="read_analog")
    # send_command_return_response(ser, command="read_digital")
    # send_command_return_response(ser, command="read_digital")
    # time.sleep(5.0)
    # for i in range(45, 45 + 9):
    #     send_command_return_response(ser, command="midi_note_off={}".format(i))
    # send_command_return_response(ser, command="read_analog")
    # send_command_return_response(ser, command="read_digital")

    # send_command_return_response(ser, command="switch_on")
    # time.sleep(0.3)
    # send_command_return_response(ser, command="switch_off")
    # send_command_return_response(ser, command="read_analog")

    # send_command_return_response(ser, command="write_digital=0000")
    # send_command_return_response(ser, command="write_digital=3333")
    # send_command_return_response(ser, command="write_digital=cccc")
    # send_command_return_response(ser, command="write_digital=ffff")

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
