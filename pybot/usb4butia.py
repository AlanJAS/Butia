
# Constantes

USB4ALL_VENDOR        = 0x04d8
USB4ALL_PRODUCT       = 0x000c
USB4ALL_CONFIGURATION = 1
USB4ALL_INTERFACE     = 0

READ_HEADER_SIZE      = 3

# Otras

#CONSTANTS

NULL_BYTE = 0x00
DEFAULT_PACKET_SIZE = 0x04
GET_USER_MODULES_SIZE_COMMAND = 0x05
GET_USER_MODULE_LINE_COMMAND = 0x06
GET_HANDLER_SIZE_COMMAND = 0x0A
GET_HANDLER_TYPE_COMMAND = 0x0B
ADMIN_HANDLER_SEND_COMMAND = 0x00
CLOSEALL_BASE_BOARD_COMMAND = 0x07

ADMIN_MODULE_IN_ENDPOINT = 0x01
ADMIN_MODULE_OUT_ENDPOINT = 0x81
GET_USER_MODULE_LINE_PACKET_SIZE = 0x05

GET_LINES_RESPONSE_PACKET_SIZE = 5
GET_LINE_RESPONSE_PACKET_SIZE = 12
GET_HANDLER_TYPE_PACKET_SIZE = 5
GET_HANDLER_RESPONSE_PACKET_SIZE = 5
CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE = 5
TIMEOUT = 250
MAX_RETRY = 5

#################################################

class USB4butia():

    def __init__(self, dev):
        self.device = dev
        self.handle = None
        
    def open_device(self):
        if not self.device:
            print "Unable to find device!"
            return None
        try:
            self.handle = self.device.open()
            self.handle.setConfiguration(USB4ALL_CONFIGURATION)
            self.handle.claimInterface(USB4ALL_INTERFACE)
        except usb.USBError, err:
            print err
            self.handle = None
        return self.handle

    def close_device(self):
        try:
            self.handle.releaseInterface()
        except Exception, err:
            print err
        self.handle = None
        self.device = None

    def read(self, length, timeout = 0):
        return self.handle.bulkRead(ADMIN_MODULE_IN_ENDPOINT, length, timeout)
 
    def write(self, buffer, timeout = 0):
        return self.handle.bulkWrite(ADMIN_MODULE_OUT_ENDPOINT, buffer, timeout)



def find_usb4butia():
    # Get busses
    for bus in usb.busses():
        for dev in bus.devices:
            if dev.idVendor == USB4ALL_VENDOR and dev.idProduct == USB4ALL_PRODUCT:
                return USB4butia(dev)


















