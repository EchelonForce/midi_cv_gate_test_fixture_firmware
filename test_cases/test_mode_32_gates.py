import test


class test_mode_poly(test.Midi_CV_Gate_Test):
    def setUp(self):
        super().setUp()
        self.change_dut_mode(test.System_Mode.MODE_32_GATES)

    def test_first_gate(self):
        note_val = 0
        self.send_command_return_response(command=f"midi_note_on={note_val}")
        self.check_digital_values("0001")
        self.check_cvs_are_off()
        self.send_command_return_response(command=f"midi_note_off={note_val}")
        self.check_all_off()
