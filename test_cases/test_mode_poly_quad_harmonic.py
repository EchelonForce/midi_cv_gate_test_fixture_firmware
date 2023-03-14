import test


class test_mode_poly_quad_harmonic(test.Midi_CV_Gate_Test):
    def setUp(self):
        super().setUp()
        self.change_dut_mode(test.System_Mode.FIRST_PRIO_POLY_QUAD_HARMONIC)

    def test_1_note(self):
        note_val = 1
        note_ideal_voltage = note_val / 12
        v_str = f"{note_ideal_voltage},{note_ideal_voltage+1},{note_ideal_voltage+1.585},{note_ideal_voltage+2},0,0,0,0,0,0,0,0,0,0,0,0"
        expected_voltages = f"voltages={v_str}"
        self.send_command_return_response(command=f"midi_note_on={note_val}")
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("000F")

        self.send_command_return_response(command=f"midi_note_off={note_val}")
        # CVs should still be at the same voltage to allow ADSR release to work.
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("0000")

    def test_4_notes(self):
        note_vals = range(1, 5)

        note_ideal_voltages = []
        for n in note_vals:
            note_ideal_voltages.append(n / 12)
            note_ideal_voltages.append(1 + (n / 12))
            note_ideal_voltages.append(1.585 + (n / 12))
            note_ideal_voltages.append(2 + (n / 12))
        v_str = ",".join([str(a) for a in note_ideal_voltages])

        expected_voltages = f"voltages={v_str}"
        for note_val in note_vals:
            self.send_command_return_response(command=f"midi_note_on={note_val}")
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)

        self.check_digital_values("FFFF")

        for note_val in note_vals:
            self.send_command_return_response(command=f"midi_note_off={note_val}")

        # CVs should still be at the same voltage to allow ADSR release to work.
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("0000")

    def test_first_note_prio(self):
        note_vals = range(1, 5)
        note_ideal_voltages = []
        for n in note_vals:
            note_ideal_voltages.append(n / 12)
            note_ideal_voltages.append(1 + (n / 12))
            note_ideal_voltages.append(1.585 + (n / 12))
            note_ideal_voltages.append(2 + (n / 12))
        v_str = ",".join([str(a) for a in note_ideal_voltages])

        expected_voltages = f"voltages={v_str}"
        for note_val in note_vals:
            self.send_command_return_response(command=f"midi_note_on={note_val}")
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("FFFF")

        # send another note that should get ignored.
        self.send_command_return_response(command="midi_note_on=7")

        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("FFFF")

        for note_val in note_vals:
            self.send_command_return_response(command=f"midi_note_off={note_val}")

        # CVs should still be at the same voltage to allow ADSR release to work.
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("0000")
