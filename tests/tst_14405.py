# coding: UTF-8
import struct
import unittest
import json
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
        self.tst.debug_input_value[self.tst.PIN_I_ON_OFF] = True

        self.tst.on_init()

    def test_build_modbus_request(self):
        print ("\n### test_build_modbus_request")
        result = self.tst.read_holding_register_request(0x00A1, 4)
        # result = self.tst.build_modbus_request(0, 4)
        self.assertEqual(result, "")

    def test_set_battery_mode(self):
        print ("\n### test_set_battery_mode")
        number = 2
        hex_representation = struct.pack('>H', number)
        result = self.tst.set_battery_mode(hex_representation) # 0 Auto, 1 Charge, 2 Discharge, 3 Stand-by
        # self.assertEqual(result, "")

    def test_build_modbus_write_request(self):
        print ("\n### test_build_modbus_write_request")
        id, result = self.tst.write_register_request_1_byte(0x072D, 1) # 0 Auto, 1 Charge, 2 Discharge, 3 Stand-by
        # result = self.tst.build_modbus_request(0, 4)
        self.assertEqual(result, "")

    def test_datetime(self):
        result = self.tst.get_system_datetime()
        print(result)

    def test_print_byte(self):
        res = str_as_hex("ABC")
        print(res)

    def test_conversion(self):
        num = 0x1234
        print("0x%X" % num)

    def test_extract_data(self):
        hex_values = [0x00, 0x15, 0x00, 0x00, 0x00, 0x07, 0x55, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00]
        reply = ''.join(chr(x) for x in hex_values)
        solution = ''.join(chr(x) for x in hex_values[9:])
        data = self.tst.extract_data(reply)
        self.assertEqual(data, solution)

    def test_read_int16(self):
        hex_values = [0xFF, 0xFF]
        reply = ''.join(chr(x) for x in hex_values)
        ret = parse_modbus_response(reply, "int16")
        self.assertEqual(-1, ret)

        hex_values = [0x00, 0x01]
        reply = ''.join(chr(x) for x in hex_values)
        ret = parse_modbus_response(reply, "int16")
        self.assertEqual(1, ret)

    def test_read_uint16(self):
        print("### test_read_uint16")
        hex_values = [0x00, 0xe6, 0x00, 0xe6, 0x00, 0xe9]
        reply = ''.join(chr(x) for x in hex_values[0:2])
        ret = parse_modbus_response(reply, "uint16")
        self.assertEqual(230, ret)

    def test_2(self):
        hex_values = [0x00, 0xe7, 0x00, 0xe4, 0x00, 0xe9]
        reply = ''.join(chr(x) for x in hex_values)
        print(len(reply))
        print("{}, {}".format(len(reply[0:2]), str_as_hex(reply[0:2])))
        print("{}, {}".format(len(reply[2:4]), str_as_hex(reply[2:4])))
        print("{}, {}".format(len(reply[2:4]), str_as_hex(reply[4:6])))

    def test_read_uint32(self):
        data_set = Dataset(self.tst.PIN_O_GRID_TOTAL_ENERGY, "GRID_TOTAL_ENERGY", 0x0012, "uint32", 2, 0.1)
        hex_values = [0x00, 0x00, 0x46, 0xc1]
        reply = ''.join(chr(x) for x in hex_values)
        ret = parse_modbus_response(reply, data_set.data_model)
        print(ret * data_set.scale)

    def test_connection(self):
        # result = self.tst.read_register(0x0703, 1)
        # result = self.tst.read_register(0x0704, 1)

        result = self.tst.read_register(0x041D, 18, True)
        pv1 = result[2]
        pv2 = result[5]
        pv3 = result[8]
        pv4 = result[11]
        pv5 = result[14]
        pv6 = result[17]

        print("1:{} 2:{} 3:{} 4:{} 5:{} 6:{}".format(int(pv1), int(pv2), int(pv3), int(pv4), int(pv5), int(pv6), ))

        # 001AH Frequent(Grid) (2 byte, 0.01Hz)
        # ret = self.tst.read_register(0x001A, 1)
        # self.assertTrue(49.0 < ret/100.0 < 51.0)

    def test_collect_data(self):
        # 001AH Frequent(Grid) (2 byte, 0.01Hz)
        # ret = self.tst.read_register(0x001A, 1)
        # self.assertTrue(49.0 < ret/100.0 < 51.0)

        # 0021H 0022H Total Active power(Grid Meter) (4 byte, 1W/bit)
        self.tst.collect_data()
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        self.assertTrue(self.tst.PIN_O_GRID_TOTAL_ENERGY in self.tst.out_sbc)
        self.assertTrue(self.tst.out_sbc[self.tst.PIN_O_GRID_TOTAL_ENERGY] > 300)

    def test_write_time(self):
        # self.tst.on_input_value(self.tst.PIN_I_DISCHARGE_START_TIME_1, "09:00")
        self.tst.on_input_value(self.tst.PIN_I_TIME_PERIOD_CONTROL_FLAG, 3)

    def test_hex_to_int(self):
        res = self.tst.hex_to_int([0x01, 0x00])
        print(res)
        res = self.tst.hex_to_int([0x00, 0x0A])
        print(res)

    def test_write_request(self):
        id, request = self.tst.write_register_request_1_byte(0x0851, 256)
        print("id: {}".format(id))
        print(request)

    def test_as(self):
        data = [#0x00, 0x8c, 0x00, 0x00, 0x00, 0x29, 0x55,
                #0x03, 0x26,
                0x00, 0x03, 0x00, 0x0a, 0x00,
                0x05, 0x00, 0x0b, 0x00, 0x11, 0x00, 0x16,
                0x00, 0x5a, 0x00, 0x04, 0x00, 0x05, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x1e, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x1e, 0x00, 0x00, 0x00,
                0x1e, 0x00, 0x00, 0x00, 0x00]

        result = convert_time_control_data(data)
        print(result)

    def test_monitor_grid(self):
        # 001AH Frequent(Grid) (2 byte, 0.01Hz)
        # ret = self.tst.read_register(0x001A, 1)
        # self.assertTrue(49.0 < ret/100.0 < 51.0)

        # 0021H 0022H Total Active power(Grid Meter) (4 byte, 1W/bit)
        self.tst.monitor_grid()
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        self.assertTrue(self.tst.PIN_O_GRID_LOST in self.tst.out_sbc)
        self.assertTrue(self.tst.out_sbc[self.tst.PIN_O_GRID_LOST])

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

        sleep(30)
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0

    def test_grid_lost(self):
        self.tst.monitor_grid()

    def tearDown(self):
        print("\n### tearDown")
        print("DEBUG | tearDown | Finished.")


if __name__ == '__main__':
    unittest.main()
