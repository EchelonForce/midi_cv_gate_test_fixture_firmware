import argparse
import matplotlib.pyplot as plt
import numpy as np

# Serial Port
ser = None


def main():
    parser = argparse.ArgumentParser(description="Plot data")
    parser.add_argument("filename")
    args = parser.parse_args()
    (data, max_cvs, max_notes) = read_from_file(args.filename)
    plot(data, max_cvs, max_notes)
    plot_against_avg(data, max_cvs, max_notes)

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


def plot(data, max_cvs, max_notes):
    import matplotlib.pyplot as plt

    cvs = list(range(0, max_cvs))
    notes = list(range(0, max_notes))

    fig, ax = plt.subplots()
    for cv in cvs:
        # print("cv[{}]={}".format(cv, data[cv]))
        ax.plot(notes, data[cv], label="cv[{}]".format(cv))
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

    s = "{"
    for cv in cvs:
        s += "{"
        for note in notes:
            if note == 0:
                s += "0,"
            else:
                s += "{},".format(int(diff_from_avg[cv][note] * 2.53 / 2.44))
        s += "}, \\\n"
    s += "}"

    print(s)

    fig, ax = plt.subplots()
    for cv in cvs:
        # print("cv[{}]={}".format(cv, data[cv]))
        ax.plot(notes, diff_from_avg[cv], label="cv[{}]".format(cv))
    ax.legend()


if __name__ == "__main__":
    main()
