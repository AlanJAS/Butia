#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# USB comunication with Fischer
# Copyright (c) 2014 Andrés Aguirre <aaguirre@fing.edu.uy>
# Copyright (c) 2014 Mercedes Marzoa <mmarzoa@fing.edu.uy>
# Copyright (C) 2014 Alan Aguiar <alanjas@hotmail.com>
# Copyright (c) 2014 Butiá Team butia@fing.edu.uy 
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import usb

FISCHER_LT_VENDOR  = 0x146a
FISCHER_LT_PRODUCT = 0x000a

OUT_ENDPOINT =  0X01
IN_ENDPOINT  =  0X81

FISCHER_LT_CONFIGURATION = 1
FISCHER_LT_INTERFACE     = 0

TIMEOUT = 0
ERROR = -1

class usb_device():

    def __init__(self, dev):
        self.dev = dev
        self.debug = False

    def _debug(self, message, err=''):
        if self.debug:
            print(message, err)

    def open_device(self):
        """
        Open the comunication, configure the interface
        """
        try:
            if self.dev.is_kernel_driver_active(FISCHER_LT_INTERFACE):
                self.dev.detach_kernel_driver(FISCHER_LT_INTERFACE)
            self.dev.set_configuration(FISCHER_LT_CONFIGURATION)
        except usb.USBError as err:
            self._debug('ERROR:com_usb:open_device', err)

    def close_device(self):
        """
        Close the comunication with the baseboard
        """
        try:
            self.dev.__del__()
        except Exception as err:
            self._debug('ERROR:com_usb:close_device', err)
        self.dev = None

    def read(self, size):
        """
        Read from the device length bytes
        """
        try:
            return self.dev.read(IN_ENDPOINT, size, TIMEOUT)
        except Exception as err:
            self._debug('ERROR:com_usb:read', err)
 
    def write(self, data):
        """
        Write in the device: data
        """
        try:
            return self.dev.write(OUT_ENDPOINT, data, TIMEOUT)
        except Exception as err:
            self._debug('ERROR:com_usb:write', err)

    def get_address(self):
        """
        Get unique address for the usb
        """
        if self.dev is not None:
            return self.dev.address
        else:
            return None

    def get_info(self):
        """
        Get the device info such as manufacturer, etc
        """
        try:
            names = usb.util.get_string(self.dev, 1).encode('ascii')
            copy = usb.util.get_string(self.dev, 2).encode('ascii')
            sn = usb.util.get_string(self.dev, 3).encode('ascii')
            return [names, copy, sn]
        except Exception as err:
            self._debug('ERROR:com_usb:get_info', err)

def find():
    """
    List all busses and returns a list of baseboards detected
    """
    l = []
    try:
        for b in usb.core.find(find_all=True, idVendor=FISCHER_LT_VENDOR, idProduct=FISCHER_LT_PRODUCT):
            l.append(usb_device(b))
    except:
        pass
    return l

