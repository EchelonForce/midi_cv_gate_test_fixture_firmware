# Firmware for Eurorack MIDI to 16x16 CV Gate Module Test Fixture

This the firmware and test scripts for a test fixture for a Eurorack module with 16 CVs and 16 Gate outputs. It's meant to run on an Arduino Pro Mini.

Full writeup of the calibration fixture and procedure is here: https://www.robotdialogs.com/2023/03/test-fixture-and-calibration-eurorack.html

The module this is meant to calibrate is described here: https://www.robotdialogs.com/2022/09/eurorack-midi-to-16x16-cv-gate-module.html

# midi_cv_gate_test_fixture.ino
This is the Arduino pro mini firmware for the test fixture.

# test_dut_cv.py
This is a script that communicates with the test fixture and reads voltages from the DUT.

# convert_dut_cv_to_cal_table.py
This script reads the output of the test_dut_cv.py script and produces a calibration table for the DUT.

# plot_test_dut_cv_data.py
This script is used to examine the data gathered from the DUT by test_dut_cv.py

# .\calibration folder
This folder has scripts used to calibrate the test fixture's ADCs. It is used to create the cal_vals_converted.txt file that is used by convert_dut_cv_to_cal_table.py

# .\test_cases folder and run_all_test_cases.cmd
This folder has a set of python unit tests that interact with the test fixture and the connected DUT to check the behavior of each mode in the DUT firmware.
run_all_test_cases.cmd will run all the tests.
Individual tests can be run with standard python unit test commands:

> python -m unittest discover test_cases -k drone

# Other stuff
io_expander_test\midi_cv_gate_test_fixture_io_expander_test.ino - This was an intermediate test firmware to sort out the io expander on the test fixture.
adc_test\midi_cv_gate_test_fixture_adc_test.ino - This was an intermediate test firmware to sort out the ADCs on the test fixture.

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. https://creativecommons.org/licenses/by-nc-sa/4.0/