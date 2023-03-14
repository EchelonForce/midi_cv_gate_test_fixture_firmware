import test


class test_interface(test.Midi_CV_Gate_Test):
    def setUp(self):
        super().setUp()
        self.all_notes_off()

    def test_change_dut_mode(self):
        self.change_dut_mode(test.System_Mode.DEFAULT)

    def test_read_digital(self):
        self.check_digital_values("0000")

    def test_read_analog(self):
        self.check_all_off()
