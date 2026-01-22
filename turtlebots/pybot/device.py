#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Device abstraction for USB4butia
#
# Copyright (c) 2012-2020 Alan Aguiar alanjas@hotmail.com
# Copyright (c) 2012-2020 Butiá Team butia@fing.edu.uy
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


NULL_BYTE = 0x00
OPEN_COMMAND = 0x00
CLOSE_COMMAND = 0x01
HEADER_PACKET_SIZE = 0x06
ADMIN_HANDLER = 0x00
PKT_OPEN = 0x05
PKT_CLOSE = 0x05
READ_HEADER_SIZE = 3
MAX_BYTES = 64

ERROR = -1

class Device():

    def __init__(self, baseboard, name, handler=None, func=None, openable=False):
        self.baseboard = baseboard
        self.name = name
        self.handler = handler
        self.shifted = None
        if not(self.handler == None):
            self.shifted = self.handler * 8
        self.functions = func
        self.openable = openable
        self.debug = False

    def _debug(self, message, err=''):
        if self.debug:
            print(message, err)

    def send(self, msg):
        """
        Send to the device the specifiy call and parameters
        """
        self.baseboard._send_command(self.shifted, msg[0], 0x03 + len(msg), msg[1:])

    def read(self, lenght):
        """
        Read the device data
        """
        raw = self.baseboard._send_command(self.shifted, read_size=0x03 + lenght)
        return raw[3:]

    def module_open(self):
        """
        Open this device. Return the handler
        """
        if self.openable:

            module_name = self._to_ord(self.name)
            module_name.append(NULL_BYTE)

            payload = [0x01, 0x01] + module_name

            raw = self.baseboard._send_command(ADMIN_HANDLER, OPEN_COMMAND, HEADER_PACKET_SIZE + len(module_name), payload, PKT_OPEN)

            self._debug('device:module_open', raw)

            if not(raw[4] == 255):
                self.handler = raw[4]
                self.shifted = self.handler * 8
                return self.handler
        self._debug('device:module_open:cannot open module:', self.name)
        return 255

    def module_close(self):
        if self.openable:
            raw = self.baseboard._send_command(ADMIN_HANDLER, CLOSE_COMMAND, 0x05, [self.handler], PKT_CLOSE)
            return raw[4]
        return ERROR

    def has_function(self, func):
        """
        Check if this device has func function
        """
        return hasattr(self.functions, func)

    def call_function(self, func, params):
        """
        Call specify func function with params parameters
        """
        f = getattr(self.functions, func)
        if func == 'send':
            return f(self, params)
        else:
            par = []
            for e in params:
                par.append(int(e))
            if func == 'sendPacket':
                return f(self, par)
            else:
                return f(self, *par)

    def _to_ord(self, string):
        """
        Useful function to convert characters into ordinal Unicode
        """
        s = []
        for l in string:
            o = ord(l)
            if not(o == 0):
                s.append(o)
        return s

    def _to_text(self, raw):
        """
        Useful function to convert ordinal Unicode into text
        """
        ret = ''
        for r in raw:
            if not(r == 0):
                ret = ret + chr(r)
        return ret

