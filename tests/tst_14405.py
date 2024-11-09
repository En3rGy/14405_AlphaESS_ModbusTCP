# coding: UTF-8
import struct
import unittest
import json
import logging
from cookielib import logger
from datetime import datetime
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
        logging.basicConfig(level=logging.DEBUG,  # Set the logging level to DEBUG
                            format='%(asctime)s - %(levelname)s - %(message)s')

        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.tst = AlphaESSModbus_14405_14405(0)
        self.tst.logger.setLevel(logging.DEBUG)
        self.tst.debug_only = True
        self.tst.debug_input_value[self.tst.PIN_I_IP] = self.cred["PIN_I_IP"]
        self.tst.debug_input_value[self.tst.PIN_I_PORT] = self.cred["PIN_I_PORT"]
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        self.tst.debug_input_value[self.tst.PIN_I_ON_OFF] = True

        self.tst.on_init()

    def test_hex_work(self):
        print(datetime.now().isoformat())
        start = "\x00\x01"
        print("start={}".format(start))
        # print(hex(start))

        int_val = struct.unpack('>H', start)[0]
        print("int_val={}".format(int_val))
        print("int_val + 3={}".format(int_val + 3))# 0x00 0x06

        hex_number = 0x0001
        number_str = hex(hex_number)
        print("hex_number={}".format(hex_number))
        print("number_str={}".format(number_str))
        print("number_str=='\\x00\\x01'={}".format(number_str=="\x00\x01"))

        byte1 = (hex_number >> 8) & 0xFF  # 0x27
        byte2 = hex_number & 0xFF  # 0x34

        # Convert the bytes to characters
        char_string = chr(byte1) + chr(byte2)
        print(char_string)
        int_val = struct.unpack('>H', char_string)[0]
        print(int_val)

    def test_ModbusMsg(self):
        #                                          len 0x0119  0x011A  0x011B  0x011C  0x011D  0x011E  0x011F
        hex_msg = "\x03\x3f\x00\x00\x00\x06\x55\x06\x0E\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D"
        self.tst.send_msg_intervall = 0
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        start_addr = 0x0119
        msg = ModbusMsg(start_addr, hex_msg)

        # 0x011C: Dataset(8, "BATTERY_WARNING", 0x011C, "uint32", 2, 1),
        # 0x011E: Dataset(9, "BATTERY_FAULT", 0x011E, "uint32", 2, 1),
        # 0x0120: Dataset(10, "BATTERY_CHARGE_ENERGY", 0x0120, "uint32", 2, 0.1),

        res = {0x0119: 0x0001, 0x011C: 0x06070809, 0x011E: 0x0A0B0C0D}
        print("Solution:\t{}".format(res))
        print("Result:\t{}".format(msg.values))

        self.assertEqual(res, msg.values)

    def test_collect_data(self):
        self.tst.send_msg_intervall = 0
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        self.tst.on_input_value(self.tst.PIN_I_INTERVAL_S, 0)

        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 1
        self.tst.collect_data()
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        print("# send_msg_pipe={}".format(json.dumps(self.tst.send_msg_pipe)))

        solution1={"addr": 0x0012, "is_write": False, "data": 2 }
        solution2={"addr": 0x0740, "data": 3, "is_write": False}
        solution3= {"addr": 0x0126, "data": 1, "is_write": 1}

        self.assertTrue(solution1 in self.tst.send_msg_pipe, "sol1")
        self.assertTrue(solution2 in self.tst.send_msg_pipe, "sol2")
        self.assertTrue(solution3 in self.tst.send_msg_pipe, "sol3")

    def test_get_msg(self):
        print ("\n### write request")
        id, result = self.tst.get_msg(0x072D, 300, True) # 0 Auto, 1 Charge, 2 Discharge, 3 Stand-by

        logging.debug("TEST |id={}, result={}".format(id, print_int_as_hex(result)))
        self.assertEqual(result, bytearray([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x55, 0x06, 0x07, 0x2d, 0x01, 0x2C]))

        print ("\n### read request")
        id, result = self.tst.get_msg(0x00A1, 4, False)
        logging.debug("TEST |id={}, result={}".format(id, print_int_as_hex(result)))
        self.assertEqual(result, bytearray([0x00, 0x02, 0x00, 0x00, 0x00, 0x06, 0x55, 0x03, 0x00, 0xa1, 0x00, 0x04]))

    def test_bytes_to_int32(self):
        val = bytes_to_int32("\x00\x00\x00A")
        self.assertEqual(ord("A"), val)

    def test_parse_reply(self):
        response = "\x00\x15\x00\x00\x00\x07\x55\x03\x04\x01\x02\x03\x04"
        register= 0x00A1
        self.tst.parse_reply(register, response)
        self.assertEqual(self.tst.debug_output_value[4], 16909060)

        print("SYSTEM_TIME_YYMM")
        response = "\x00\x02\x00\x00\x00\x09\x55\x03\x06\x18\x0a\x17\x0b\x22\x0f"
        register= 0x0740
        self.tst.parse_reply(register, response)
        self.assertEqual(self.tst.debug_output_value[4], 16909060)

        print("Monitor Grid")

        response = "\x00\x01\x00\x00\x00\x09\x55\x03\x06\x00\xe4\x00\xe4\x00\xe3"
        register= 0x0014
        self.tst.parse_reply(register, response)
        self.assertFalse(self.tst.debug_output_value[17])

    def test_process_send_msg_pipe(self):
        self.tst.send_msg_pipe = [{"addr": 0x0012, "data": 2, "is_write": False},
                                  {"addr": 0x0740, "data": 3, "is_write": False},
                                  {"addr": 0x0126, "data": 1, "is_write": False}]

        self.tst.send_msg_intervall = 1

        sleep(10)

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

    def test_read_uint32(self):
        data_set = Dataset(self.tst.PIN_O_GRID_TOTAL_ENERGY, "GRID_TOTAL_ENERGY", 0x0012, "uint32", 2, 0.1)
        hex_values = [0x00, 0x00, 0x46, 0xc1]
        reply = ''.join(chr(x) for x in hex_values)
        ret = parse_modbus_response(reply, data_set.data_model)
        print(ret * data_set.scale)

    def test_collect_data2(self):
        # 001AH Frequent(Grid) (2 byte, 0.01Hz)
        # ret = self.tst.read_register(0x001A, 1)
        # self.assertTrue(49.0 < ret/100.0 < 51.0)

        # 0021H 0022H Total Active power(Grid Meter) (4 byte, 1W/bit)
        self.tst.send_msg_intervall = 0.2
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 5

        self.tst.collect_data()
        sleep(10)

        self.tst.send_msg_intervall = 0
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0

        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        self.assertTrue(self.tst.PIN_O_GRID_TOTAL_ENERGY in self.tst.out_sbc)
        self.assertTrue(self.tst.out_sbc[self.tst.PIN_O_GRID_TOTAL_ENERGY] > 300)

    def test_calc(self):
        print("0x0127 - 0x0102 + 1 = {}".format(0x0127 - 0x0102 + 1))
        print("0x0090  + 19 - 0x0012 + 1 = {}".format(0x0090 + 19 - 0x0012 + 1))
        print("0x041F - 0x0090 + 1 = {}".format(0x041F - 0x0090 + 1))
        print("0x0740 - 0x041F + 1 = {}".format(0x0740 - 0x041F + 1))

    # @todo continue here downwards

    def test_write_time(self):
        self.tst.send_msg_intervall = 0.2
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0

        self.tst.on_input_value(self.tst.PIN_I_DISCHARGE_START_TIME_1, "09:00")
        self.tst.on_input_value(self.tst.PIN_I_TIME_PERIOD_CONTROL_FLAG, 3)

        sleep(2)
        self.tst.send_msg_intervall = 0

    def test_hex_to_int(self):
        res = self.tst.hex_to_int([0x01, 0x00])
        print(res)
        res = self.tst.hex_to_int([0x00, 0x0A])
        print(res)

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
        self.tst.send_msg_intervall = 0
        self.tst.debug_input_value[self.tst.PIN_I_INTERVAL_S] = 0
        logging.debug("tearDown | Finished.")


if __name__ == '__main__':
    unittest.main()
