from unittest import TestCase

from code.prosessor import curve_data_process


class TestProcess(TestCase):
    def setUp(self) -> None:
        pass

    def test_curve_data_process(self):
        # st BLA1 data
        std_data = {
            "conc": [10, 10, 1, 1, 1 / 10, 1 / 10, 1 / 100, 1 / 100, 1e-03, 1e-03, 1e-04, 1e-04, 1e-05, 1e-05, 1e-06,
                     1e-06],
            "cts": [12.707, 12.928, 15.401, 15.854, 19.434, 19.443, 23.635, 23.632, 26.985, 26.949, 31.618, 31.57,
                    32.797,
                    34.331, 34.953, 34.009]
        }
        curve_data_process(std_data, "conc")
