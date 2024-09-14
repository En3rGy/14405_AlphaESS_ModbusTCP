# coding: UTF-8
import time
import unittest
import json
from operator import contains
from time import sleep

################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/14405_AlphaESS Modbus (14405).py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)


################################################################################

class TestSequenceFunctions(unittest.TestCase):
    cred = 0
    tst = 0

    def setUp(self):
        print("\n###setUp")
        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.tst = AlphaESSModbus_14405_14405(0)
        self.tst.debug_only = True
        self.tst.debug_input_value[self.tst.PIN_I_IP] = self.cred["PIN_I_IP"]
        self.tst.debug_input_value[self.tst.PIN_I_PORT] = self.cred["PIN_I_PORT"]
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 15

        self.tst.on_init()

    def test_build_modbus_request(self):
        print ("\n### test_build_modbus_request")
        result = self.tst.build_modbus_request(0x00A1, 4)
        # result = self.tst.build_modbus_request(0, 4)
        self.assertEqual(result, "")

    def test_datetime(self):
        result = self.tst.get_system_datetime()
        print(result)

    def test_connection(self):
        result = self.tst.read_register(0x0703, 1)
        result = self.tst.read_register(0x0704, 1)

        # 001AH Frequent(Grid) (2 byte, 0.01Hz)
        # ret = self.tst.read_register(0x001A, 1)
        # self.assertTrue(49.0 < ret/100.0 < 51.0)

        # 0021H 0022H Total Active power(Grid Meter) (4 byte, 1W/bit)
        # ret = self.tst.read_register(0x0021, 2)
        # self.assertTrue(ret > 0)

        # 0090H 0091H Total energy feed to Grid(PV)

        # 0010H 0011H Total energy feed to grid(Grid) (4 byte, 0.01kWh/bit)

        # 0012H 0013H Total energy consume from grid(Grid) (4 byte, 0.1 kWh/Bit)
        # ret = self.tst.read_register(0x0012, 2)
        # self.assertTrue(ret > 3000)
        # self.tst.read_register(0x0013, 2)

    def test_collect_data(self):
        # 001AH Frequent(Grid) (2 byte, 0.01Hz)
        # ret = self.tst.read_register(0x001A, 1)
        # self.assertTrue(49.0 < ret/100.0 < 51.0)

        # 0021H 0022H Total Active power(Grid Meter) (4 byte, 1W/bit)
        self.tst.collect_data()
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        self.assertTrue(self.tst.PIN_O_GRID_TOTAL_ENERGY in self.tst.out_sbc)
        self.assertTrue(self.tst.out_sbc[self.tst.PIN_O_GRID_TOTAL_ENERGY] > 300)

    def test_type(self):
        none_t = None
        print("Type: {}\n{}\nint: {}\nstr: {}".format(type(none_t), none_t, int(none_t), str(none_t)))

    def test_full(self):
        self.tst = AlphaESSModbus_14405_14405(0)
        self.tst.debug_only = False
        self.tst.debug_input_value[self.tst.PIN_I_IP] = self.cred["PIN_I_IP"]
        self.tst.debug_input_value[self.tst.PIN_I_PORT] = self.cred["PIN_I_PORT"]
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 15
        self.tst.on_init()

        sleep(120)
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0

    def test_grid_lost(self):
        self.tst.monitor_grid()

    def tearDown(self):
        print("\n### tearDown")
        print("DEBUG | tearDown | Finished.")


if __name__ == '__main__':
    unittest.main()
