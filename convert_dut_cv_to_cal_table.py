import argparse
import matplotlib.pyplot as plt
import numpy as np

"""
This script takes a file from the DUT (generated by test_dut_cv.py) and
the test fixture's calibration data (calibration/cal_vals_converted.txt) and
produces a table of values that can be used to offset the CVs of the
DUT for each note tested.
"""


def main():
    parser = argparse.ArgumentParser(description="Plot data")
    parser.add_argument("filename")
    args = parser.parse_args()
    (data, max_cvs, max_notes) = read_from_file(args.filename)

    data = convert_data_to_voltage(data, max_cvs, max_notes)

    plot(data, max_cvs, max_notes)
    plot_against_avg(data, max_cvs, max_notes)
    plot_against_ideal(data, max_cvs, max_notes)

    plt.show()


def read_from_file(file_name):

    hdr_line = ""
    data_lines = []
    with open(file_name, "r") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r").rstrip(",")
            line = line.split(",")
            if hdr_line == "":
                hdr_line = line
                continue
            else:
                data_lines.append(line)
    # print(hdr_line)
    # print(data_lines[0])
    max_notes = max([int(a) for a in hdr_line[1:]])
    max_cvs = len(data_lines)
    data = []
    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))
    for cv in cvs:
        vals = [int(a) for a in data_lines[cv][1:]]
        data.append(vals)
    return (data, max_cvs, max_notes + 1)


def convert_data_to_voltage(data, max_cvs, max_notes):
    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))
    voltage_map = read_voltage_map("calibration/cal_vals_converted.txt")

    data_out = []

    for cv in cvs:
        data_out.append(
            [voltage_from_voltage_map(voltage_map, cv, value) for value in data[cv]]
        )

    return data_out


def read_voltage_map(file_name):
    voltage_map = []
    with open(file_name, "r") as f:
        for line in f:
            vals = line.rstrip("\n").rstrip("\r").rstrip(",").split(",")

            voltage_map.append(
                {
                    "voltage": float(vals[0].replace("V", "")),
                    "adc_vals": [float(a) for a in vals[1:]],
                }
            )
    return voltage_map


def voltage_from_voltage_map(voltage_map, cv, value):
    lower_voltage_idx = 0
    upper_voltage_idx = -1
    for i, voltage in enumerate(voltage_map):
        if (
            value >= voltage_map[lower_voltage_idx]["adc_vals"][cv]
            and value < voltage["adc_vals"][cv]
        ):
            upper_voltage_idx = i
            break
        else:
            lower_voltage_idx = i

    upper_voltage_val = voltage_map[upper_voltage_idx]["adc_vals"][cv]
    lower_voltage_val = voltage_map[lower_voltage_idx]["adc_vals"][cv]
    upper_voltage = voltage_map[upper_voltage_idx]["voltage"]
    lower_voltage = voltage_map[lower_voltage_idx]["voltage"]

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


def plot(data, max_cvs, max_notes):
    import matplotlib.pyplot as plt

    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))

    fig, ax = plt.subplots()
    for cv in cvs:
        # print("cv[{}]={}".format(cv, data[cv]))
        ax.plot(notes, data[cv], label="cv[{}]".format(cv))

    ideal_vals = [(1 / 12) * note for note in notes]
    ax.plot(notes, ideal_vals, label="ideal")
    fig.suptitle("Note vs CV [V]")
    ax.legend()


def plot_against_avg(data, max_cvs, max_notes):
    import matplotlib.pyplot as plt

    avg_vals = []

    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))

    note_avgs = []
    for note in notes:
        same_notes = []
        for cv in cvs:
            same_notes.append(data[cv][note])
        note_avgs.append(np.mean(same_notes))

    diff_from_avg = []
    for cv in cvs:
        diffs = np.subtract(note_avgs, data[cv])
        diff_from_avg.append(diffs)

    s = "offset_from_avg={"
    for cv in cvs:
        s += "{"
        for note in notes:
            if note == 0:
                s += "0,"
            else:
                diff_in_dac_lsbs = int(diff_from_avg[cv][note] / 0.00253)
                diff_in_dac_lsbs = min(max(-127, diff_in_dac_lsbs), 127)
                s += "{},".format(diff_in_dac_lsbs)
        s += "}, \\\n"
    s += "}\n"

    print(s)

    fig, ax = plt.subplots()
    for cv in cvs:
        # print("cv[{}]={}".format(cv, data[cv]))
        ax.plot(notes, diff_from_avg[cv], label="cv[{}]".format(cv))
    ax.legend()

    fig.suptitle("Note vs diff from avg. CV [V]")


def plot_against_ideal(data, max_cvs, max_notes):
    import matplotlib.pyplot as plt

    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))
    ideal_vals = [note / 12 for note in notes]

    diff_from_ideal = []
    for cv in cvs:
        diffs = list(np.subtract(ideal_vals, data[cv]))
        diff_from_ideal.append(diffs)

    s = "offset_from_ideal={"
    for cv in cvs:
        s += "{"
        for note in notes:
            if note == 0:
                s += "0,"
            else:
                diff_in_dac_lsbs = int(diff_from_ideal[cv][note] / 0.00253)
                diff_in_dac_lsbs = min(max(-127, diff_in_dac_lsbs), 127)
                s += "{},".format(diff_in_dac_lsbs)
        s += "}, \\\n"
    s += "}\n"

    print(s)

    fig, ax = plt.subplots()
    for cv in cvs:
        # print("cv[{}]={}".format(cv, data[cv]))
        ax.plot(notes, diff_from_ideal[cv], label="cv[{}]".format(cv))
    ax.legend()
    fig.suptitle("Note vs diff from Ideal CV [V]")


if __name__ == "__main__":
    main()
