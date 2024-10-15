# coding: UTF-8
import json
import logging
import random
import socket
import threading
import struct
from stringold import split


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class AlphaESSModbus_14405_14405(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "14405_AlphaESS_Modbus")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_IP=1
        self.PIN_I_PORT=2
        self.PIN_I_INTERVAL_S=3
        self.PIN_I_ON_OFF=4
        self.PIN_I_DISCHARGE_START_TIME_1=5
        self.PIN_I_DISCHARGE_STOP_TIME_1=6
        self.PIN_I_DISCHARGE_START_TIME_2=7
        self.PIN_I_DISCHARGE_STOP_TIME_2=8
        self.PIN_I_CHARGE_START_TIME_1=9
        self.PIN_I_CHARGE_STOP_TIME_1=10
        self.PIN_I_CHARGE_START_TIME_2=11
        self.PIN_I_CHARGE_STOP_TIME_2=12
        self.PIN_I_TIME_PERIOD_CONTROL_FLAG=13
        self.PIN_O_GRID_TOTAL_ENERGY=1
        self.PIN_O_TOTAL_ENERGY_TO_GRID=2
        self.PIN_O_GRID_TOTAL_ACTIVE_POWER=3
        self.PIN_O_PV_TOTAL_ACTIVE_POWER=4
        self.PIN_O_BATTERY_STATUS=5
        self.PIN_O_MAX_CELL_TEMPERATURE=6
        self.PIN_O_BATTERY_CAPACITY=7
        self.PIN_O_BATTERY_WARNING=8
        self.PIN_O_BATTERY_FAULT=9
        self.PIN_O_BATTERY_CHARGE_ENERGY=10
        self.PIN_O_BATTERY_DISCHARGE_ENERGY=11
        self.PIN_O_BATTERY_POWER=12
        self.PIN_O_BATTERY_REMAINING_TIME=13
        self.PIN_O_BATTERY_SOC=14
        self.PIN_O_PV1_POWER=15
        self.PIN_O_PV2_POWER=16
        self.PIN_O_GRID_LOST=17
        self.PIN_O_DATETIME=18
        self.PIN_O_TIME_PERIOD_CONTROL_JSON=19
        self.PIN_O_HEARTBEAT=20

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.logger = logging.getLogger("{}".format(random.randint(0, 9999999)))
        self.transaction_id = 0
        self.g_msg = 0
        self.g_register = {}
        self.g_out = {}
        self.debug_only = False
        self.g_bigendian = False
        self.out_sbc = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timer = threading.Timer(15, self.collect_data)
        self.dataset = [ Dataset(self.PIN_O_GRID_TOTAL_ENERGY, "GRID_TOTAL_ENERGY", 0x0012, "uint32", 2, 0.1),
                Dataset(self.PIN_O_TOTAL_ENERGY_TO_GRID, "TOTAL_ENERGY_TO_GRID", 0x0090, "uint32", 2, 0.01),
                Dataset(self.PIN_O_GRID_TOTAL_ACTIVE_POWER, "GRID_TOTAL_ACTIVE_POWER", 0x0021, "int32", 2, 1),
                Dataset(self.PIN_O_PV_TOTAL_ACTIVE_POWER, "PV_TOTAL_ACTIVE_POWER", 0x00A1, "int32", 2, 1),
                Dataset(self.PIN_O_BATTERY_SOC, "BATTERY_SOC", 0x0102, "uint16", 1, 0.1),
                Dataset(self.PIN_O_MAX_CELL_TEMPERATURE, "MAX_CELL_TEMPERATURE", 0x0110, "int16",1, 0.1),
                Dataset(self.PIN_O_BATTERY_CAPACITY, "BATTERY_CAPACITY", 0x0119, "uint16",1, 0.1),
                Dataset(self.PIN_O_BATTERY_WARNING, "BATTERY_WARNING", 0x011C, "uint32",2, 1),
                Dataset(self.PIN_O_BATTERY_FAULT, "BATTERY_FAULT", 0x011E, "uint32",2, 1),
                Dataset(self.PIN_O_BATTERY_CHARGE_ENERGY, "BATTERY_CHARGE_ENERGY", 0x0120, "uint32",2, 0.1),
                Dataset(self.PIN_O_BATTERY_DISCHARGE_ENERGY, "BATTERY_DISCHARGE_ENERGY", 0x0122, "uint32",2, 0.1),
                Dataset(self.PIN_O_BATTERY_POWER, "BATTERY_POWER", 0x0126, "int16",1, 1),
                Dataset(self.PIN_O_BATTERY_REMAINING_TIME, "BATTERY_REMAINING_TIME", 0x0127, "uint16",1, 1),
                Dataset(self.PIN_O_PV1_POWER, "PV1_POWER", 0x041F, "uint32",2, 1),
                Dataset(self.PIN_O_PV2_POWER, "PV2_POWER", 0x0423, "uint32",2, 1)]

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        if pin in self.out_sbc:
            if self.out_sbc[pin] == val:
                self.logger.debug("SBC: Pin {} <- data not send ({})".format(pin, str(val).decode("utf-8")))
                return

        self._set_output_value(pin, val)
        self.logger.debug("OUT: Pin {} <-\t{}".format(pin, val))
        self.out_sbc[pin] = val

    def log_msg(self, text):
        self.DEBUG.add_message("14405 ({}): {}".format(self._get_module_id(), text))

    def log_data(self, key, value):
        self.DEBUG.set_value("14405 ({}) {}".format(self._get_module_id(), key), str(value))

    def get_transaction_id(self):
        self.transaction_id = self.transaction_id + 1
        if self.transaction_id > 65535:
            self.transaction_id = 1

        return self.transaction_id

    def write_register_request_1_byte(self, start_address, data):
        # Modbus TCP request format:
        # Transaction ID (2 bytes) + Protocol ID (2 bytes) + Length (2 bytes) + Unit ID (1 byte) + Function Code (1 byte) + Start Address (2 bytes) + Data (2 bytes)
        # Example usage:
        # > start_address = 0  # The starting register address
        # > quantity = 10  # Number of registers to read
        # > request = self.build_modbus_request(start_address, quantity)

        transaction_id = self.get_transaction_id() | 0x0000  # 2 byte, Can be anything, just a unique ID
        protocol_id = 0x0000  # 2 byte, Modbus protocol ID is 0
        length = 0x0006  # 2 byte, Number of bytes in the message (Unit ID + Function Code + Address + Data)
        unit_id = 0x55 # 1 byte = 85
        function_code = 0x06  # 1 byte, Function code 6: Write Single Register

        # data
        start_address = start_address  # 2 byte
        data_s = int(data) # 1 byte

        # Construct the Modbus request
        request = [
            transaction_id >> 8, transaction_id & 0xFF,
            protocol_id >> 8, protocol_id & 0xFF,
            length >> 8, length & 0xFF,
            unit_id,
            function_code,
            start_address >> 8, start_address & 0xFF,
            data_s >> 8, int(data) & 0xFF
        ]

        print(' '.join(['0x{:02X}'.format(num) for num in request]))

        return transaction_id, bytearray(request)

    def read_holding_register_request(self, start_address, quantity):
        # Modbus TCP request format:
        # Transaction ID (2 bytes) + Protocol ID (2 bytes) + Length (2 bytes) + Unit ID (1 byte) + Function Code (1 byte) + Start Address (2 bytes) + Quantity of Registers (2 bytes)
        # Example usage:
        # > start_address = 0  # The starting register address
        # > quantity = 10  # Number of registers to read
        # > request = self.build_modbus_request(start_address, quantity)

        transaction_id = self.get_transaction_id() | 0x0000  # 2 byte, Can be anything, just a unique ID
        protocol_id = 0x0000  # 2 byte, Modbus protocol ID is 0
        length = 0x0006  # 2 byte, Number of bytes in the message (Unit ID + Function Code + Address + Quantity)
        unit_id = 0x55 # 1 byte = 85
        function_code = 0x03  # 1 byte, Function code 3: Read Holding Registers

        # data
        start_address = start_address  # 2 byte
        register_no = quantity # 2 byte

        # Construct the Modbus request
        request = [
            transaction_id >> 8, transaction_id & 0xFF,
            protocol_id >> 8, protocol_id & 0xFF,
            length >> 8, length & 0xFF,
            unit_id,
            function_code,
            start_address >> 8, start_address & 0xFF,
            register_no >> 8, quantity & 0xFF
        ]

        return transaction_id, bytearray(request)

    def get_time_period_control_data(self):
        response = self.read_register(0x084F, 19)
        data = str_to_hex_array(response)
        result = convert_time_control_data(data)

        self.set_output_value_sbc(self.PIN_O_TIME_PERIOD_CONTROL_JSON, json.dumps(result))

    def get_system_datetime(self):
        response = self.read_register(0x0740, 3)
        date_time = str_to_hex_array(response)

        year = int(date_time[0]) + 2000
        month = int(date_time[1])
        day = int(date_time[2])
        hour = int(date_time[3])
        minute = int(date_time[4])
        second = int(date_time[5])

        date_time = "{}-{}-{} {}:{}:{}".format(str(year).zfill(2), str(month).zfill(2), str(day).zfill(2),
                                               str(hour).zfill(2), str(minute).zfill(2), str(second).zfill(2))
        return date_time

    def get_socket(self):
        print("Entering get_socket...")
        host = str(self._get_input_value(self.PIN_I_IP))
        port = int(self._get_input_value(self.PIN_I_PORT))

        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        self.sock.bind(('', 0)) # use a free port
        s_ip, s_port = self.sock.getsockname()
        self.log_data("Send from/to", "{}:{} / {}:{}".format(s_ip, s_port, host, port))
        self.log_msg("Socket (re-) opened.")

    def check_socket(self):
        try:
            s_ip, s_port = self.sock.getsockname()
            if not s_port or s_port is 0:
                return False
        except socket.error:
            return False
        return True

    def read_register(self, start_register, quantity):
        # type: (hex, int) -> object
        """
        :param start_register:
        :param quantity: Amount of registers to read
        :type: string
        :return: Data fields of modbus reply as string.
        """

        if not self.check_socket():
            self.get_socket()
            host = str(self._get_input_value(self.PIN_I_IP))
            port = int(self._get_input_value(self.PIN_I_PORT))
            try:
                self.sock.connect((host, port))
            except Exception as e:
                raise Exception("read_register | '{}' while connecting to {}:{}.".format(e, host, port))

        transaction_id, request = self.read_holding_register_request(start_register, quantity)

        try:
            self.sock.sendall(request)
            response = self.sock.recv(1024)
            if self.debug_only: print("DEBUG |read_register | {}".format(hex(start_register)), str_as_hex(response))
        except Exception as e:
            if self.sock:
                self.sock.close()
            raise Exception("read_register | '{}' while sending/receiving".format(e))

        return extract_data(response)

    def monitor_grid(self):
        # Constants for minimum voltage threshold to detect grid loss
        min_voltage_threshold = 220 * 3  # Adjust this threshold based on your system's requirements

        # 0014H Voltage of A Phase (Grid) RO 2-byte unsigned short 1 V/bit
        # Read the voltage of the A phase in units of 1 V per bit

        response = self.read_register(0x0014, 3)
        ret_a = parse_modbus_response(response[0:2], "uint16")
        self.log_data("Grid Phase 1 [V]", ret_a)
        ret_b = parse_modbus_response(response[2:4], "uint16")
        self.log_data("Grid Phase 2 [V]", ret_b)
        ret_c = parse_modbus_response(response[4:6], "uint16")
        self.log_data("Grid Phase 3 [V]", ret_c)

        grid_voltage = ret_a + ret_b + ret_c

        # Check if the grid voltage is below the threshold
        if grid_voltage < min_voltage_threshold:
            # Grid is lost
            self.set_output_value_sbc(self.PIN_O_GRID_LOST, True)
        else:
            # Grid is present
            self.set_output_value_sbc(self.PIN_O_GRID_LOST, False)

    def collect_data(self):
        print("Entering collect_data()...")
        interval = self._get_input_value(self.PIN_I_INTERVAL_S)
        on = self._get_input_value(self.PIN_I_ON_OFF)
        success = False
        if interval == 0 or not on:
            print("collect_data | interval == {}, on = {}, exiting.".format(interval, on))
            if self.check_socket():
                self.sock.close()
            return

        try:
            self.monitor_grid()
            success = True
        except Exception as e:
            self.log_msg("collect_data | monitor_grid() | Exception: {}".format(e))

        for register in self.dataset:
            if register.PIN == -1:
                continue
            try:
                reply = self.read_register(register.register, register.length)
                ret = parse_modbus_response(reply, register.data_model)
                self.set_output_value_sbc( register.PIN, ret * register.scale)
                success = True
            except Exception as e:
                self.log_msg("collect_data | {} | Exception: {}".format(register.name, e))

        try:
            date_time = self.get_system_datetime()
            self.set_output_value_sbc(self.PIN_O_DATETIME, date_time)
            success = True
        except Exception as e:
            self.log_msg("collect_data | get_system_datetime() | Exception: {}".format(e))

        try:
            self.get_time_period_control_data()
            success = True
        except Exception as e:
            self.log_msg("collect_data | get_time_period_control_data() | Exception: {}".format(e))

        if success:
            self._set_output_value(self.PIN_O_HEARTBEAT, True)

        if interval > 0:
            if self.timer:
                if  self.timer.isAlive():
                    print("collect_data | Cancelling timer.")
                    self.timer.cancel()
            self.timer = threading.Timer(interval, self.collect_data).start()

    def set_register(self, addr, data):
        self.log_msg("set_register(addr={}, ...)".format(hex(addr)))
        if not self.check_socket():
            self.get_socket()
            host = str(self._get_input_value(self.PIN_I_IP))
            port = int(self._get_input_value(self.PIN_I_PORT))
            try:
                self.sock.connect((host, port))
            except Exception as e:
                raise Exception("set_register | '{}' while connecting to {}:{}.".format(e, host, port))

        transaction_id, request = self.write_register_request_1_byte(addr, data)

        try:
            self.sock.sendall(request)
            response = self.sock.recv(1024)
            self.log_data("set_register(addr={}, ...) | Reply".format(hex(addr)), str_as_hex(response))
        except Exception as e:
            if self.sock:
                self.sock.close()
            raise Exception("set_register | '{}' while sending/receiving".format(e))

        return response

    def write_time(self, hh_addr, mm_addr, time_str, pin):
        try:
            hh, mm = get_time_data(time_str)
            self.set_register(hh_addr, hh)
            self.set_register(mm_addr, mm)
        except Exception as e:
            self.log_msg("write_time(pin={}) | Exception: {}".format(pin, e))

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        logging.basicConfig()

        self.g_msg = 0
        self.g_register = {}
        self.g_out = {}
        self.g_bigendian = False

        if not self.debug_only:
            self.collect_data()
        else:
            print("Debug | on_init | Finished here, debugging only.")

    def on_input_value(self, index, value):
        print("Entering on_input_value({},{})...".format(index, value))
        if index == self.PIN_I_ON_OFF:
            if value:
                self.collect_data()
            else:
                if self.check_socket():
                    self.sock.close()

        elif index == self.PIN_I_INTERVAL_S:
            if value > 0:
                if self.timer.isAlive():
                    self.timer.cancel()
                self.collect_data()

        elif index == self.PIN_I_DISCHARGE_START_TIME_1:
            self.write_time(0x0851, 0x085A, value, index)
        elif index == self.PIN_I_DISCHARGE_STOP_TIME_1:
            self.write_time(0x0852, 0x085B, value, index)
        elif index == self.PIN_I_DISCHARGE_START_TIME_2:
            self.write_time(0x0853, 0x085C, value, index)
        elif index == self.PIN_I_DISCHARGE_STOP_TIME_2:
            self.write_time(0x0854, 0x085D, value, index)

        elif index == self.PIN_I_CHARGE_START_TIME_1:
            self.write_time(0x0856, 0x085E, value, index)
        elif index == self.PIN_I_CHARGE_STOP_TIME_1:
            self.write_time(0x0857, 0x085F, value, index)
        elif index == self.PIN_I_CHARGE_START_TIME_2:
            self.write_time(0x0858, 0x0860, value, index)
        elif index == self.PIN_I_CHARGE_STOP_TIME_2:
            self.write_time(0x0859, 0x0861, value, index)

        elif index == self.PIN_I_TIME_PERIOD_CONTROL_FLAG:
            try:
                self.set_register(0x084F, int(value))
            except Exception as e:
                self.log_msg("on_input_value | PIN_I_TIME_PERIOD_CONTROL_FLAG | Exception: {}".format(e))


def get_time_data(time):
    time_split = time.split(":")
    hh = int(time_split[0])
    mm = int(time_split[1])
    return hh, mm


def str_as_hex(input_string):
    # type: (str) -> str
    try:
        return " ".join("0x{:02x}".format(ord(c)) for c in input_string)
    except Exception as e:
        raise Exception("print_str_to_hex | {}".format(e))


def convert_time_control_data(data):

    # 0 1 | 2 3 | 4 5 | 6 7 | 8 9 | 10 11 | 12 13 | 14 15 | 16 17 | 18 19 | 20 21 | 22 23 |
    # 24 25 | 26 27 | 28 29 | 30 31 | 32 33 | 34 35 | 36 37

    time_period_control_flag = hex_to_int(data[0:2])
    ups_reserve_soc = hex_to_int(data[2:4])
    time_discharge_start_1_hours = hex_to_int(data[4:6])
    time_discharge_stop_1_hours = hex_to_int(data[6:8])
    time_discharge_start_2_hours = hex_to_int(data[8:10])
    time_discharge_stop_2_hours = hex_to_int(data[10:12])
    charge_cut_soc = hex_to_int(data[12:14])
    time_charge_start_1_hours = hex_to_int(data[14:16])
    time_charge_stop_1_hours = hex_to_int(data[16:18])
    time_charge_start_2_hours = hex_to_int(data[18:20])
    time_charge_stop_2_hours = hex_to_int(data[20:22])

    time_discharge_start_1_minutes = hex_to_int(data[22:24])
    time_discharge_stop_1_minutes = hex_to_int(data[24:26])
    time_discharge_start_2_minutes = hex_to_int(data[26:28])
    time_discharge_stop_2_minutes = hex_to_int(data[28:30])

    time_charge_start_1_minutes = hex_to_int(data[30:32])
    time_charge_stop_1_minutes = hex_to_int(data[32:34])
    time_charge_start_2_minutes = hex_to_int(data[34:36])
    time_charge_stop_2_minutes = hex_to_int(data[36:])

    result = {"control_flag": time_period_control_flag,
              "discharge_1_start": "{:02d}:{:02d}".format(time_discharge_start_1_hours, time_discharge_start_1_minutes),
              "discharge_1_stop": "{:02d}:{:02d}".format(time_discharge_stop_1_hours, time_discharge_stop_1_minutes),
              "discharge_2_start": "{:02d}:{:02d}".format(time_discharge_start_2_hours, time_discharge_start_2_minutes),
              "discharge_2_stop": "{:02d}:{:02d}".format(time_discharge_stop_2_hours, time_discharge_stop_2_minutes),
              "charge_1_start": "{:02d}:{:02d}".format(time_charge_start_1_hours, time_charge_start_1_minutes),
              "charge_1_stop": "{:02d}:{:02d}".format(time_charge_stop_1_hours, time_charge_stop_1_minutes),
              "charge_2_start": "{:02d}:{:02d}".format(time_charge_start_2_hours, time_charge_start_2_minutes),
              "charge_2_stop": "{:02d}:{:02d}".format(time_charge_stop_2_hours, time_charge_stop_2_minutes),
              "ups_reserve_soc": ups_reserve_soc,
              "charge_cut_soc": charge_cut_soc
              }

    return result


def bytes_to_uint16(byte_data, byteorder='big'):
    if len(byte_data) != 2:
        raise ValueError("Input must be exactly 2 bytes for an unsigned short but was {}".format(len(byte_data)))

    if byteorder == 'big':
        return struct.unpack('>H', byte_data)[0]  # Big-endian unsigned short
    elif byteorder == 'little':
        return struct.unpack('<H', byte_data)[0]  # Little-endian unsigned short
    else:
        raise ValueError("Invalid byte order. Use 'big' or 'little'.")


def hex_to_int(hex_array):
    result = 0
    for byte in hex_array:
        result = (result << 8) | byte  # Shift left by 8 bits and add the next byte
    return result


def bytes_to_int16(byte_data, byteorder='big'):
    if len(byte_data) != 2:
        raise ValueError("Input must be exactly 2 bytes for a signed short")

    if byteorder == 'big':
        return struct.unpack('>h', byte_data)[0]  # Big-endian signed short
    elif byteorder == 'little':
        return struct.unpack('<h', byte_data)[0]  # Little-endian signed short
    else:
        raise ValueError("Invalid byte order. Use 'big' or 'little'.")


def bytes_to_int32(byte_data, byteorder='big'):
    # type: ([int], str) -> int
    if len(byte_data) != 4:
        raise ValueError("Input must be exactly 4 bytes for a signed int")

    if byteorder == 'big':
        return struct.unpack('>i', byte_data)[0]  # Big-endian signed int
    elif byteorder == 'little':
        return struct.unpack('<i', byte_data)[0]  # Little-endian signed int
    else:
        raise ValueError("Invalid byte order. Use 'big' or 'little'.")


def bytes_to_uint32(byte_data, byteorder='big'):
    print("Entering bytes_to_uint32({}, {})...".format(str_as_hex(byte_data), byteorder))
    if len(byte_data) != 4:
        raise ValueError("Input must be exactly 4 bytes for an unsigned int")

    if byteorder == 'big':
        return struct.unpack('>I', byte_data)[0]  # Big-endian unsigned int
    elif byteorder == 'little':
        return struct.unpack('<I', byte_data)[0]  # Little-endian unsigned int
    else:
        raise ValueError("Invalid byte order. Use 'big' or 'little'.")


def str_to_hex_array(data):
    # type: (str) -> [int]
    hex_vec = [ord(c) for c in data]
    return hex_vec


def parse_modbus_response(data, data_format):
    # type: (str, str) -> int
    """
    :param data: String
    :param data_format: String
    :return:
    """
    print("Entering parse_modbus_register({}, {})...".format(str_as_hex(data), data_format))

    if data_format == "int32":
        return bytes_to_int32(data)
    elif data_format == "uint32":
        return bytes_to_uint32(data)
    elif data_format == "int16":
        return bytes_to_int16(data)
    elif data_format == "uint16":
        return bytes_to_uint16(data)
    else:
        raise Exception("parse_modbus_response | {} ist not a valid data format.".format(data_format))


def extract_data(response):
    # type: (str) -> str
    if len(response) < 9:
        raise Exception("read_register | Invalid response length")

    # Extract the data (response[9:] will contain the register values)
    data = response[9:]
    length = ord(response[8])

    if len(data) != length:
        raise Exception("read_register | Expected length {} but message was {}".format(str_as_hex(response[8]), len(data)))

    return data


class Dataset:
    def __init__(self, pin, name, register, data_model, length, scale = 1.0):
        self.PIN = pin
        self.name = name
        self.register = register
        self.data_model = data_model
        self.length = length
        self.scale = scale
