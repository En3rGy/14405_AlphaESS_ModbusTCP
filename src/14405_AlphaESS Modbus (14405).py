# coding: UTF-8
import logging
import random
import socket
import threading
from cookielib import logger
from re import DEBUG


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
        self.PIN_O_PV1_POWER=14
        self.PIN_O_PV2_POWER=15
        self.PIN_O_GRID_LOST=16
        self.PIN_O_HEARTBEAT=17

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
        self.dataset = [ Dataset(self.PIN_O_GRID_TOTAL_ENERGY, "GRID_TOTAL_ENERGY", 0x0012, 2, 0.1 ),
                Dataset(self.PIN_O_TOTAL_ENERGY_TO_GRID, "TOTAL_ENERGY_TO_GRID", 0x0090, 2, 0.01),
                Dataset(self.PIN_O_GRID_TOTAL_ACTIVE_POWER, "GRID_TOTAL_ACTIVE_POWER", 0x0021, 2, 1),
                Dataset(self.PIN_O_PV_TOTAL_ACTIVE_POWER, "PV_TOTAL_ACTIVE_POWER", 0x00A1, 2, 1),
                Dataset(self.PIN_O_BATTERY_STATUS, "BATTERY_STATUS", 0x0103, 1, 1),
                Dataset(self.PIN_O_MAX_CELL_TEMPERATURE, "MAX_CELL_TEMPERATURE", 0x0110, 1, 0.1),
                Dataset(self.PIN_O_BATTERY_CAPACITY, "BATTERY_CAPACITY", 0x0119, 1, 0.1),
                Dataset(self.PIN_O_BATTERY_WARNING, "BATTERY_WARNING", 0x011C, 2, 1),
                Dataset(self.PIN_O_BATTERY_FAULT, "BATTERY_FAULT", 0x011E, 2, 1),
                Dataset(self.PIN_O_BATTERY_CHARGE_ENERGY, "BATTERY_CHARGE_ENERGY", 0x0120, 2, 0.1),
                Dataset(self.PIN_O_BATTERY_DISCHARGE_ENERGY, "BATTERY_DISCHARGE_ENERGY", 0x0122, 2, 0.1),
                Dataset(self.PIN_O_BATTERY_POWER, "BATTERY_POWER", 0x0126, 1, 1),
                Dataset(self.PIN_O_BATTERY_REMAINING_TIME, "BATTERY_REMAINING_TIME", 0x0127, 1, 1),
                Dataset(self.PIN_O_PV1_POWER, "PV1_POWER", 0x041F, 2, 1),
                Dataset(self.PIN_O_PV2_POWER, "PV1_POWER", 0x0423, 2, 1)]

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

    def build_modbus_request(self, start_address, quantity):
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

        return bytearray(request)

    def parse_modbus_response(self, response, return_hex_array=False):
        # The response contains:
        # - Transaction ID (2 bytes)
        # - Protocol ID (2 bytes)
        # - Length (2 bytes)
        # - Unit ID (1 byte)
        # - Function Code (1 byte)
        # - Byte Count (1 byte)
        # - Data (N bytes, depending on byte count)
        # Example usage:
        # > register_values = parse_modbus_response(response)
        # > print("Register Values:", register_values)

        if len(response) < 9:
            print("Invalid response length")
            return None

        # Extract the data (response[9:] will contain the register values)
        data = response[9:]
        # length = response[9]
        register_values = []

        hex_vec = [ord(c) for c in data]
        if return_hex_array:
            return hex_vec

        # print("parse_modbus_response | val: {}".format(hex_vec))
        for i in range(0, len(hex_vec), 2):
            register = (hex_vec[i] << 8) | hex_vec[i + 1]
            register_values.append(register)

        result = 0
        for number in register_values:
            result = (result << 16) | number

        # print("parse_modbus_response | val: {}".format(int(result)))
        return int(result)

    def get_system_datetime(self):
        datetime = self.read_register(0x0703, 3, True)

        year = int(datetime[0]) + 2000
        month = int(datetime[1])
        day = int(datetime[2])
        hour = int(datetime[3])
        minute = int(datetime[4])
        second = int(datetime[5])

        datetime = "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)
        return datetime

    def read_register(self, register, quantity, return_hex_array=False):

        host = str(self._get_input_value(self.PIN_I_IP))
        port = int(self._get_input_value(self.PIN_I_PORT))
        request = self.build_modbus_request(register, quantity)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)

        try:
            # Connect the socket to the server
            sock.connect((host, port))
            # print("Sending:  {}".format(self.print_byte_array(request)))
            sock.sendall(request)
            response = sock.recv(1024)
            # print("Received: {}".format(''.join('0x{:02X} '.format(ord(c)) for c in response)))
            return self.parse_modbus_response(response, return_hex_array)
        except Exception as e:
            self.log_msg("read_register | Exception reading register {}: {}".format(print_byte_array([register]), e))
        finally:
            sock.close()
            # print("Connection closed.")

    def hex2int(self, msg):
        if not self.g_bigendian:
            msg = shift_bytes(msg)

        val = 0
        val = val | msg[0]
        for byte in msg[1:]:
            val = val << 8
            val = val | byte

        return int(val)

    def monitor_grid(self):
        # Constants for minimum voltage threshold to detect grid loss
        min_voltage_threshold = 220 * 3  # Adjust this threshold based on your system's requirements

        # 0014H Voltage of A Phase (Grid) RO 2-byte unsigned short 1 V/bit
        # Read the voltage of the A phase in units of 1 V per bit
        ret_a = self.read_register(0x0014, 1)
        ret_b = self.read_register(0x0015, 1)
        ret_c = self.read_register(0x0016, 1)
        if not ret_a or not ret_b or not ret_c:
            self.log_msg("monitor_grid | At least one of the return values is None. Aborting.")
            return

        # Convert the register value to volts
        grid_voltage = ret_a + ret_b + ret_c

        self.log_data("Grid Phase 1 [V]", ret_a)
        self.log_data("Grid Phase 2 [V]", ret_b)
        self.log_data("Grid Phase 3 [V]", ret_b)

        # Check if the grid voltage is below the threshold
        if grid_voltage < min_voltage_threshold:
            # Grid is lost
            self.set_output_value_sbc(self.PIN_O_GRID_LOST, True)
        else:
            # Grid is present
            self.set_output_value_sbc(self.PIN_O_GRID_LOST, False)


    def collect_data(self):
        if self.debug_only: print("DEUBG | Entering collect_data.")
        interval = self._get_input_value(self.PIN_I_INTERVAL_S)
        if interval == 0:
            return

        try:
            self.monitor_grid()
        except Exception as e:
            self.log_msg("collect_data | monitor_grid() | {}".format(e))

        for register in self.dataset:
            try:
                ret = self.read_register( register.register, register.length)
                self.set_output_value_sbc( register.PIN, ret * register.scale)
            except Exception as e:
                self.log_msg("collect_data | {} | {}".format(register.name, e))

        self._set_output_value(self.PIN_O_HEARTBEAT, True)

        if interval > 0:
            threading.Timer(interval, self.collect_data).start()

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
        pass


# Re-ordering / inverting the byte order
def shift_bytes(msg):
    res = []
    for x in msg[::-1]:
        res.append(x)
    return res


def print_byte_array(hex_array):
    return ' '.join('0x{:02X}'.format(num) for num in hex_array)


class Dataset:
    def __init__(self, pin, name, register, length, scale = 1.0):
        self.PIN = pin
        self.name = name
        self.register = register
        self.length = length
        self.scale = scale

