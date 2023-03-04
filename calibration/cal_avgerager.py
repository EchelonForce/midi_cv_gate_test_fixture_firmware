import numpy as np


def average_vals(vals):
    # print(vals)
    if len(vals) > 0:
        avgs = []
        cvs = list(range(0, 16))
        for cv in cvs:
            cv_vals = []
            for v in vals:
                cv_vals.append(v[cv])
            avgs.append(np.mean(cv_vals))

        s = ""
        for avg in avgs:
            s += "{:.2f},".format(avg)
        print(s)


with open("cal_vals.txt", "r") as f:
    vals = []
    for line in f:
        a = line.rstrip("\n").rstrip("\r")
        if "analog_values=" in a:
            a = a.replace("analog_values=", "")
            a = a.rstrip(",")
            a = a.split(",")
            # print(a)
            vs = [int(b, 16) for b in a]
            # print(vs)
            vals.append(vs)
            # print(line)
        elif "V" in a:
            average_vals(vals)

            print(a)
            vals = []
        else:
            print(a)
    average_vals(vals)
