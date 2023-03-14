import test


class test_mode_drone(test.Midi_CV_Gate_Test):
    def setUp(self):
        super().setUp()
        self.change_dut_mode(test.System_Mode.DRONE)

    def help_test_drone_single_note(self, note_val=1):
        note_ideal_voltages = [note_val / 12] * 16
        v_str = ",".join([str(a) for a in note_ideal_voltages])
        expected_voltages = f"voltages={v_str}"

        self.send_command_return_response(command=f"midi_note_on={note_val}")
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response, tolerance=0.015
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("FFFF")

        self.send_command_return_response(command=f"midi_note_off={note_val}")

        # CVs should still be at the same voltage to allow ADSR release to work.
        actual_response = self.send_command_return_response(command="read_analog")
        comparison_result, msg = self.compare_analog_values_to_voltages(
            expected_voltages, actual_response, tolerance=0.015
        )
        self.assertTrue(comparison_result, msg)
        self.check_digital_values("0000")

    def test_drone_several_note(self):
        self.help_test_drone_single_note()
        self.help_test_drone_single_note(12)
        self.help_test_drone_single_note(24)
        self.help_test_drone_single_note(36)
        self.help_test_drone_single_note(48)
        self.help_test_drone_single_note(60)
        self.help_test_drone_single_note(72)
        self.help_test_drone_single_note(84)
        self.help_test_drone_single_note(96)
