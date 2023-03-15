import serial
import time
import datetime

"""
This is a test script that sends commands to the midi_cv_gate test fixture.
Commands are sent on the serial port below and then the test fixture can send midi messages to the DUT and measure the DUTs outputs.

test_collect_data() sends note on/off to the DUT, measures the CV and saves the result.
The data is written to a timestamped file and plotted.

The data from a DUT can then be converted (using the
"""

# Serial Port
serial_port_id = "COM10"
ser = None


def main():
    setup()
    reset_dut()

    max_cvs = 16
    max_notes = 128
    start = datetime.datetime.now()
    print("Start Time: " + start.strftime("%Y-%m-%d-%H-%M-%S"))
    data = test_collect_data(max_cvs, max_notes)
    print("Start Time: " + start.strftime("%Y-%m-%d-%H-%M-%S"))
    print("End Time: " + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    print(
        "Total Time: {} sec".format((datetime.datetime.now() - start).total_seconds())
    )
    log_to_file(data, max_cvs, max_notes)
    plot(data, max_cvs, max_notes)

    teardown()


def log_to_file(data, max_cvs, max_notes):
    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))

    filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "data.csv"

    with open(filename, "w") as f:

        s = "CV,"
        for note in notes:
            s += "{},".format(note)
        f.write(s + "\n")

        for cv in cvs:
            s = "{},".format(cv)
            for val in data[cv]:
                s += "{},".format(val)
            f.write(s + "\n")


def plot(data, max_cvs, max_notes):
    import matplotlib.pyplot as plt

    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))

    fig, ax = plt.subplots()
    for cv in cvs:
        # print("cv[{}]={}".format(cv, data[cv]))
        ax.plot(notes, data[cv], label="cv[{}]".format(cv))
    ax.legend()

    plt.show()


def test_collect_data(max_cvs, max_notes):
    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))
    current_notes = list(range(0, max_cvs))
    data = []
    for cv in cvs:
        note_vals = []
        for note in notes:
            note_vals.append(-1)
        data.append(note_vals)

    for note in notes:
        for cv in cvs:
            note_on(current_notes[cv])

        vals = read_and_convert_analog()
        for (cv, cn) in zip(cvs, current_notes):
            data[cv][cn] = vals[cv]

        for cv in cvs:
            note_off(current_notes[cv])
            # print("cv[{}]={}".format(cv, current_note))
            current_notes[cv] = (current_notes[cv] + 1) % max_notes

    for cv in cvs:
        print("cv[{}]={}".format(cv, data[cv]))

    return data
    # read_and_convert_analog()
    # for i in range(45, 45 + 16):
    #     send_command_return_response(ser, command="midi_note_off={}".format(i))


def note_on(note=0):
    send_command_return_response(
        ser, command="midi_note_on={}".format(note), delay=0.05
    )


def note_off(note=0):
    send_command_return_response(
        ser, command="midi_note_off={}".format(note), delay=0.05
    )


def read_and_convert_analog():
    result = send_command_return_response(ser, command="read_analog")
    result = result.replace("analog_values=", "").rstrip(",")
    vals = [int(a, 16) for a in result.split(",")]
    print(vals)
    return vals


def setup():
    global ser
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = serial_port_id
    ser.timeout = 1
    ser.open()
    time.sleep(1.5)  # some time need (by windows?) to get a messages out correctly


def teardown():
    ser.close()


def reset_dut():
    """Emulate a (short) button press which cancels all notes."""
    # send_command_return_response(ser, command="switch_on")
    # time.sleep(0.3)  # >200ms needed
    # send_command_return_response(ser, command="switch_off")
    send_command_return_response(ser, command="midi_all_notes_off")
    send_command_return_response(ser, command="midi_change_mode=0")
    time.sleep(0.3)


def send_command_return_response(ser, command="read_digital", delay=0.2):
    ser.write(bytearray("{}\n".format(command), "ascii"))
    # ser.flush()
    time.sleep(delay)
    # read the echo'd command
    result = ser.read_until().decode("ascii").rstrip("\n").rstrip("\r")
    print(result)
    # read the response
    result = ser.read_until().decode("ascii").rstrip("\n").rstrip("\r")
    print(result)
    return result


if __name__ == "__main__":
    main()
