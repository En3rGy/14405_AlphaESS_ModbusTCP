# coding: UTF-8
import json
import logging
import random
import socket
import threading
import struct
from datetime import datetime

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
        self.logger.setLevel(logging.INFO)
        self.transaction_id = 0
        self.g_msg = 0
        self.g_register = {}
        self.g_out = {}
        self.debug_only = False
        self.g_bigendian = False
        self.out_sbc = {}
        self.send_msg_pipe = []
        self.send_msg_intervall = 0.2
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timer = threading.Timer(15, self.collect_data)

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        if pin in self.out_sbc:
            if self.out_sbc[pin] == val:
                self.logger.debug("SBC: Pin {} <- data not send ({})".format(pin, str(val).decode("utf-8")))
                return

        self._set_output_value(pin, val)
        self.logger.debug("OUT: Pin {} <-\t{}".format(pin, str(val)))
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

    def get_msg(self, start_address, data, is_set=False):
        # self.logger.debug("Entering get_msg(start_address={}, data= {}, is_set={}".format(hex(start_address), data, is_set))
        transaction_id = self.get_transaction_id() | 0x0000  # 2 byte, Can be anything, just a unique ID
        protocol_id = 0x0000  # 2 byte, Modbus protocol ID is 0
        msg_length = 0x0006  # 2 byte, Number of bytes in the message (Unit ID + Function Code + Address + Data)
        unit_id = 0x55 # 1 byte = 85
        if is_set:
            function_code = 0x06  # 1 byte, Function code 6: Write Single Register
        else:
            function_code = 0x03  # 1 byte, Function code 3: Read Holding Registers

        start_address = start_address  # 2 byte

        data_s = int(data) # 2 byte; value to set for 0x06 or amount of registers to read for 0x03

        # Construct the Modbus request
        request = [
            transaction_id >> 8, transaction_id & 0xFF,
            protocol_id >> 8, protocol_id & 0xFF,
            msg_length >> 8, msg_length & 0xFF,
            unit_id,
            function_code,
            start_address >> 8, start_address & 0xFF,
            data_s >> 8, int(data) & 0xFF
        ]
        # self.logger.debug("get_msg | msg to return is {}".format(print_hex_values(request)))
        return transaction_id, bytearray(request)

    def get_time_period_control_data(self):
        self.add_to_get_pipe(0x084F, 19)

    def get_socket(self):
        self.logger.debug("Entering get_socket...")
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

    def collect_data(self):
        """
        Puts all messages relevant for cyclic status updated on the msg pipe via self.add_to_send_pipe(...).
        :return:
        """
        self.logger.debug("Entering collect_data()...")
        interval = self._get_input_value(self.PIN_I_INTERVAL_S)
        on = self._get_input_value(self.PIN_I_ON_OFF)
        if interval == 0 or not on:
            self.logger.debug("collect_data | interval == {}, on = {}, exiting.".format(interval, on))
            if self.check_socket():
                self.sock.close()
            return

        self.add_to_send_pipe(0x0012, 17, False)  # Grid, incl. # Monitor grid
        self.add_to_send_pipe(0x0090, 19, False)  # Meter/PV
        self.add_to_send_pipe(0x0102, 38, False)  # Battery
        self.add_to_send_pipe(0x041F, 6, False)   # PVx Power

        if interval > 0:
            if self.timer:
                if  self.timer.isAlive():
                    self.logger.debug("collect_data | Cancelling timer.")
                    self.timer.cancel()
            self.timer = threading.Timer(interval, self.collect_data).start()

    def process_send_msg_pipe(self):
        """
        Sends the oldest message in self.send_msg_pipe and restarts the timer to send the next msg.
        :return: None
        """
        self.logger.debug("### ### ### Entering process_send_msg_pipe() ### ### ### ")
        if self.send_msg_intervall == 0:
            self.logger.debug("process_send_msg_pipe | Msg intervall == 0. Leaving.")
            return

        if len(self.send_msg_pipe) == 0:
            threading.Timer(self.send_msg_intervall, self.process_send_msg_pipe).start()
            # self.logger.debug("process_send_msg_pipe | Msg pipe empty. Leaving.")
            return

        entry = self.send_msg_pipe[0]
        try:
            reply = self.send_msg(entry["addr"], entry["data"], entry["is_write"])
            self.parse_reply(entry["addr"], reply)
            self.send_msg_pipe.pop(0)

            self._set_output_value(self.PIN_O_HEARTBEAT, True)  # @todo heartbeat less frequent
        except Exception as e:
            self.log_msg("process_send_msg_pipe | Exception {}".format(e))

            if "repetition" in entry:
                entry["repetition"] = entry["repetition"] + 1
                self.send_msg_pipe[0] = entry
                if entry["repetition"] > 2:
                    self.log_msg("send_msg | Failed to send msg to {} for {} times. Removing it from pipe.".format(hex(entry["addr"]), entry["repetition"]))
                    self.send_msg_pipe.pop(0)
            else:
                entry["repetition"] = 0
            self.send_msg_pipe[0] = entry

        threading.Timer(self.send_msg_intervall, self.process_send_msg_pipe).start()

    def add_to_send_pipe(self, addr, data, is_write):
        self.logger.debug("Entering add_to_send_pipe(addr={}, data={}, is_write={})...".format(hex(addr), data, is_write))
        self.send_msg_pipe.append({"addr": addr, "data": data, "is_write": is_write})

    def send_msg(self, register, data, is_write=True):
        # type: (hex, int, bool) -> str
        """
        :param register:
        :param data: Amount of registers to read (quantity) or value to set
        :param is_write: write or read message
        :type: str
        """
        self.logger.debug("Entering send_msg(register={}, data={}, is_write={})".format(hex(register), data, is_write))
        if not self.check_socket():
            self.get_socket()
            host = str(self._get_input_value(self.PIN_I_IP))
            port = int(self._get_input_value(self.PIN_I_PORT))
            try:
                self.sock.connect((host, port))
            except Exception as e:
                raise Exception("send_msg | '{}' while connecting to {}:{}.".format(e, host, port))

        transaction_id, request = self.get_msg(register, data, is_write)

        try:
            self.sock.sendall(request)
            response = self.sock.recv(1024)
            # self.parse_reply(register, response)
        except Exception as e:
            if self.sock:
                self.sock.close()
            raise Exception("send_msg | Exception '{}' while sending/receiving".format(e))

        self.log_msg("send_msg | Message exchange successfully.")
        return response

    def parse_reply(self, start_addr, msg):
        # 0    1    2    3    4    5    6    7    8    9    10   11
        # 0x3a 0x3f 0x00 0x00 0x00 0x06 0x55 0x06 0x08 0x5f 0x00 0x00
        self.logger.debug("Entering parse_reply(start_addr={}, msg={})".format(hex(start_addr), str_as_hex(msg)))
        modbus_msg = ModbusMsg(start_addr, msg)

        # self.logger.debug("parse_reply | Processing {} value sets.".format(len(modbus_msg.values.keys())))
        # self.logger.debug("parse_reply | modbus_msg.values.keys()={}".format(modbus_msg.values.keys()))
        for addr in modbus_msg.values.keys():
            # self.logger.debug("parse_reply | Processing {}".format(hex(addr)))
            try:
                if 0x0741 == addr or 0x0742 == addr: continue # skipping other register of "system datetime"
                elif addr == 0x0740:  # system datetime
                    # self.logger.debug("parse_reply | Processing system datetime.")
                    idx = modbus_msg.indexes[addr]
                    response = modbus_msg.data[idx:idx+6]
                    date_time = str_to_hex_array(response)
                    year = int(date_time[0]) + 2000
                    month = int(date_time[1])
                    day = int(date_time[2])
                    hour = int(date_time[3])
                    minute = int(date_time[4])
                    second = int(date_time[5])

                    date_time = datetime(year=year, month=month, day=day, hour=hour, minute=minute,
                                         second=second).isoformat()
                    self.set_output_value_sbc(self.PIN_O_DATETIME, date_time)
                    continue

                elif 0x0015 == addr or 0x016 == addr: continue # skipping other register of "monitor grid"
                elif 0x0014 == addr:  # monitor grid
                    # self.logger.debug("parse_reply | Processing 'monitor grid'.")
                    min_voltage_threshold = 220 * 3  # Adjust this threshold based on your system's requirements

                    # 0014H Voltage of A Phase (Grid) RO 2-byte unsigned short 1 V/bit
                    # Read the voltage of the A phase in units of 1 V per bit
                    ret_a = modbus_msg.values[0x0014]
                    self.log_data("Grid Phase 1 [V]", ret_a)
                    ret_b = modbus_msg.values[0x0015]
                    self.log_data("Grid Phase 2 [V]", ret_b)
                    ret_c = modbus_msg.values[0x0016]
                    self.log_data("Grid Phase 3 [V]", ret_c)

                    grid_voltage = ret_a + ret_b + ret_c

                    # Check if the grid voltage is below the threshold
                    if grid_voltage < min_voltage_threshold:
                        # Grid is lost
                        self.set_output_value_sbc(self.PIN_O_GRID_LOST, True)
                    else:
                        # Grid is present
                        self.set_output_value_sbc(self.PIN_O_GRID_LOST, False)
                    continue

                elif addr == 0x084F:  # Time period control data
                    # self.logger.debug("parse_reply | Processing time period control data.")
                    idx = modbus_msg.indexes[addr]
                    response = modbus_msg.data[idx:idx+38]
                    data = str_to_hex_array(response)
                    result = convert_time_control_data(data)
                    self.set_output_value_sbc(self.PIN_O_TIME_PERIOD_CONTROL_JSON, json.dumps(result))
                    continue

                elif addr not in REGISTER:
                    # self.log_msg("parse_reply | Register {} not known.".format(hex(addr)))
                    continue
                else:
                    # self.log_msg("parse_reply | Process status register.")
                    pin = REGISTER[addr].PIN
                    value = modbus_msg.values[addr] # no additional parse_modbus_response required!
                    if not pin == -1:
                        self.set_output_value_sbc(pin, value * REGISTER[addr].scale)
                    else:
                        self.logger.debug("parse_reply | No output pin defined for message {}".format(hex(addr)))
            except Exception as e:
                self.log_data("parse_reply | Exception", "{}\n{}".format(datetime.now().isoformat(), e))

        # self.logger.debug("parse_reply | Leaving...")

    def write_time(self, hh_addr, mm_addr, time_str, pin):
        """
        Adds values to set a time to the msg pipe
        :type hh_addr: int
        :param mm_addr:
        :type mm_addr: int
        :param time_str: 'hh:mm' time representation
        :type time_str: str
        :type pin: int
        """
        try:
            hh, mm = get_time_data(time_str)
            self.add_to_send_pipe(hh_addr, hh, True)
            self.add_to_send_pipe(mm_addr, mm, True)
        except Exception as e:
            self.log_msg("write_time(pin={}) | Exception: {}".format(pin, e))

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        logging.basicConfig()

        self.g_msg = 0
        self.g_register = {}
        self.g_out = {}
        self.g_bigendian = False

        self.collect_data()
        threading.Timer(self.send_msg_intervall, self.process_send_msg_pipe).start()

    def on_input_value(self, index, value):
        self.logger.debug("Entering on_input_value({}, {})...".format(index, value))
        if index == self.PIN_I_ON_OFF:
            if self.timer:
                if self.timer.isAlive():
                    self.logger.debug("on_input_value | Stopping current collect_data timer.")
                    self.timer.cancel()
            if value:
                self.collect_data()
            else:
                if self.check_socket():
                    self.sock.close()

        elif index == self.PIN_I_INTERVAL_S:
            if self.timer:
                if self.timer.isAlive():
                    self.logger.debug("on_input_value | Stopping current collect_data timer.")
                    self.timer.cancel()
            if value > 0:
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
                self.add_to_send_pipe(0x084F, int(value), True)
            except Exception as e:
                self.log_msg("on_input_value | PIN_I_TIME_PERIOD_CONTROL_FLAG | Exception: {}".format(e))


def get_time_data(time):
    time_split = time.split(":")
    hh = int(time_split[0])
    mm = int(time_split[1])
    return hh, mm


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
    time_charge_stop_2_minutes = hex_to_int(data[36:38])

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
    # type: (str, str) -> int
    # logging.debug("Entering bytes_to_uint32({}, {})...".format(byte_data, byteorder))

    if len(byte_data) != 4:
        raise Exception("bytes_to_int32 | Input must be exactly 4 bytes for a signed int")

    if byteorder == 'big':
        res = struct.unpack('>i', byte_data)[0]  # Big-endian signed int
        return res
    elif byteorder == 'little':
        return struct.unpack('<i', byte_data)[0]  # Little-endian signed int
    else:
        raise Exception("bytes_to_int32 | Invalid byte order. Use 'big' or 'little'.")


def bytes_to_uint32(byte_data, byteorder='big'):
    if len(byte_data) != 4:
        raise ValueError("Input must be exactly 4 bytes for an unsigned int")

    if byteorder == 'big':
        return struct.unpack('>I', byte_data)[0]  # Big-endian unsigned int
    elif byteorder == 'little':
        return struct.unpack('<I', byte_data)[0]  # Little-endian unsigned int
    else:
        raise ValueError("Invalid byte order. Use 'big' or 'little'.")


def str_as_hex(input_string):
    # type: (str) -> str
    try:
        return " ".join("0x{:02x}".format(ord(c)) for c in input_string)
    except Exception as e:
        raise Exception("str_as_hex | {}".format(e))


def hex_to_int(hex_array):
    result = 0
    for byte in hex_array:
        result = (result << 8) | byte  # Shift left by 8 bits and add the next byte
    return result


def str_to_hex_array(data):
    # type: (str) -> [int]
    hex_vec = [ord(c) for c in data]
    return hex_vec


def print_hex_values(data):
    return ' '.join(['0x{:02X}'.format(num) for num in data])


def print_int_as_hex(data):
    return ' '.join(['0x{:02x}'.format(val) for val in data])


def parse_modbus_response(data, data_format):
    # type: (str, str) -> (int|str)
    """
    :param data: String
    :param data_format: String
    :return:
    """
    # logging.debug("Entering parse_modbus_register({}, {})...".format(str_as_hex(data), data_format))
    # logging.debug("parse_modbus_response | type of data is {}".format(type(data)))

    if data_format == "int32":
        return bytes_to_int32(data)
    elif data_format == "uint32":
        return bytes_to_uint32(data)
    elif data_format == "int16":
        return bytes_to_int16(data)
    elif data_format == "uint16":
        return bytes_to_uint16(data)
    else:
        return data


class Dataset:
    def __init__(self, pin, name, register, data_model, length, scale = 1.0):
        self.PIN = pin
        self.name = name
        self.register = register
        self.data_model = data_model
        self.length = length
        self.scale = scale


class ModbusMsg:
    def __init__(self, start_addr, msg):
        if len(msg) < 9:
            raise Exception("ModbusMsg | Invalid msg length")

        byte1 = (start_addr >> 8) & 0xFF
        byte2 = start_addr & 0xFF
        self.start_addr = chr(byte1) + chr(byte2)

        self.msg_id = struct.unpack('>H', msg[0:2])[0]  # e.g. 0x3a 0x3f
        self.proto = msg[2:4]  # 0x00 0x00
        self.length = struct.unpack('>H', msg[4:6])[0]  # 0x00 0x06
        self.device_addr = msg[6] # 0x55
        self.function = msg[7]  # 0x06
        self.data_length = ord(msg[8]) # length of data filed
        self.data = msg[9:]
        self.values = {}  # type: {int: any} # {hex_addr: value}
        self.indexes = {}

        self._register_values()

    def _register_values(self):
        """
        Parse and map Modbus register values from `self.data` starting at `self.start_addr`.

        Unpacks `self.start_addr` to get the starting register address. Iterates through `self.data` in 2-byte chunks,
        calculates the corresponding register address, and parses the data based on the `REGISTER` dictionary.
        Parsed values are stored in `self.values`.

        :type: None
        :returns: Updates `self.values` with the parsed register data.
        """
        start_addr_int = struct.unpack('>H', self.start_addr)[0]  # e.g. 0x3a 0x3f

        # Keep in mind: 1 Register = 2 Byte!
        for i in range(0, len(self.data), 2):
            curr_int_addr = start_addr_int + i / 2
            # logging.debug("_register_values | curr_int_addr={}".format(hex(curr_int_addr)))

            if curr_int_addr in REGISTER.keys():
                # logging.debug("_register_values | Register {} with data length={}".format(hex(curr_int_addr), REGISTER[curr_int_addr].length))
                data = self.data[i:i + 2 * REGISTER[curr_int_addr].length]
                value = parse_modbus_response(data, REGISTER[curr_int_addr].data_model)
                self.values[curr_int_addr] = value
                self.indexes[curr_int_addr] = i


REGISTER = {0x0012: Dataset(1, "GRID_TOTAL_ENERGY", 0x0012, "uint32", 2, 0.1),
            0x0014: Dataset(-1, "VOLTAGE_A_PHASE_GRID", 0x0014, "uint16", 1, 1),
            0x0015: Dataset(-1, "VOLTAGE_B_PHASE_GRID", 0x0015, "uint16", 1, 1),
            0x0016: Dataset(-1, "VOLTAGE_C_PHASE_GRID", 0x0016, "uint16", 1, 1),
            0x0021: Dataset(3, "GRID_TOTAL_ACTIVE_POWER", 0x0021, "int32",2, 1),
            0x0090: Dataset(2, "TOTAL_ENERGY_TO_GRID", 0x0090, "uint32", 2, 0.01),
            0x00A1: Dataset(4, "PV_TOTAL_ACTIVE_POWER", 0x00A1, "int32", 2,1),
            0x0102: Dataset(14, "BATTERY_SOC", 0x0102, "uint16", 1, 0.1),
            0x0110: Dataset(6, "MAX_CELL_TEMPERATURE", 0x0110, "int16", 1,0.1),
            0x0119: Dataset(7, "BATTERY_CAPACITY", 0x0119, "uint16", 1, 0.1),
            0x011C: Dataset(8, "BATTERY_WARNING", 0x011C, "uint32", 2, 1),
            0x011E: Dataset(9, "BATTERY_FAULT", 0x011E, "uint32", 2, 1),
            0x0120: Dataset(10, "BATTERY_CHARGE_ENERGY", 0x0120, "uint32", 2,0.1),
            0x0122: Dataset(11, "BATTERY_DISCHARGE_ENERGY", 0x0122,"uint32", 2, 0.1),
            0x0126: Dataset(12, "BATTERY_POWER", 0x0126, "int16", 1, 1),
            0x0127: Dataset(13, "BATTERY_REMAINING_TIME", 0x0127, "uint16",1, 1),
            0x041F: Dataset(15, "PV1_POWER", 0x041F, "uint32", 2, 1),
            0x0423: Dataset(16, "PV2_POWER", 0x0423, "uint32", 2, 1),
            0x0740: Dataset(-1, "SYSTEM_TIME_YYMM", 0x0740, "", 1, 1),
            0x0741: Dataset(-1, "SYSTEM_TIME_DDHH", 0x0741, "", 1, 1),
            0x0742: Dataset(-1, "SYSTEM_TIME_mmss", 0x0742, "", 1, 1),
            0x084F: Dataset(-1, "TIME_PERIOD_CONTROL_DATA", 0x084F, "", 19, 1)}
