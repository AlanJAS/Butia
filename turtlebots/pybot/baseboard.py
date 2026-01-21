#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Baseboard abstraction for USB4butia
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
ERROR = -1

# COMMANDS
ADMIN_HANDLER              = 0x00
CMD_GET_USER_MODULES_SIZE  = 0x05
CMD_GET_USER_MODULE_LINE   = 0x06
CMD_CLOSEALL               = 0x07
CMD_SWITCH_TO_BOOT         = 0x09
CMD_GET_HANDLER_SIZE       = 0x0A
CMD_GET_HANDLER_TYPE       = 0x0B
CMD_RESET                  = 0xFF

# PACKET SIZES
PKT_DEFAULT                = 0x04
PKT_GET_USER_LINE          = 0x05
PKT_GET_LINES_RESPONSE     = 0x05
PKT_GET_LINE_RESPONSE      = 0x0C
PKT_GET_HANDLER_TYPE       = 0x05
PKT_HANDLER_RESPONSE       = 0x05
PKT_CLOSEALL               = 0x05




class Baseboard():

    def __init__(self, dev):
        self.dev = dev
        self.listi = {}
        self.devices = {}
        self.openables_loaded = []
        self.hack_states = {}
        for i in range(1, 9):
            self.hack_states[i] = 1

    def _send_command(self, command, packet_size=PKT_DEFAULT, payload=None, read_size=None):
        packet = [ADMIN_HANDLER, packet_size, NULL_BYTE, command]
        if payload:
            packet.extend(payload)
        self.dev.write(packet)
        if read_size:
            response = self.dev.read(read_size)
            return response
        return None

    def open_baseboard(self):
        """
        Open the baseboard
        """
        self.dev.open_device()

    def close_baseboard(self):
        """
        Close the baseboard
        """
        self.dev.close_device()

    def get_info(self):
        """
        Get baseboard info: manufacture..
        """
        return self.dev.get_info()

    def add_device(self, handler, device):
        """
        Add a device with handler of the dictionary
        """
        self.devices[handler] = device
        if device.openable:
            if not(device.name in self.openables_loaded):
                self.openables_loaded.append(device.name)

    def remove_device(self, handler):
        """
        Remove a device with handler of the dictionary
        """
        if handler in self.devices:
            dev = self.devices.pop(handler)
            if dev.openable:
                if dev.name in self.openables_loaded:
                    self.openables_loaded.remove(dev.name)

    def reset_device_list(self):
        """
        Cleans the device dictionary
        """
        self.devices = {}

    def get_openables_loaded(self):
        """
        Get the list of modules that was openened (no pnp)
        """
        return self.openables_loaded

    def reset_openables_loaded(self):
        """
        Reset the list of openables modules
        """
        self.openables_loaded = []

    def get_listi(self, force=False):
        """
        Get the listi: the list of modules present in the board that can be
        opened (or pnp module opens)
        """
        if not self.listi or force:
            self.listi = {}
            size = self.get_user_modules_size()
            for i in range(size):
                self.listi[i] = self.get_user_module_line(i)
        return self.listi

    def set_hack_state(self, hack, state):
        if hack in self.hack_states:
            self.hack_states[hack] = state

    def get_hack_state(self, hack):
        if hack in self.hack_states:
            return self.hack_states[hack]

    def get_device_handler(self, name):
        """
        Get the handler of device with name: name
        """
        for e in self.devices:
            if self.devices[e].name == name:
                return e
        return ERROR

    def get_device_name(self, handler):
        """
        Get the name of device with handler: handler
        """
        if handler in self.devices:
            return self.devices[handler].name
        else:
            return ''

    def get_user_modules_size(self):
        """
        Get the size of the list of user modules (listi)
        """
        w = [ADMIN_HANDLER, PKT_DEFAULT, NULL_BYTE]
        w.append(CMD_GET_USER_MODULES_SIZE)
        self.dev.write(w)
        raw = self.dev.read(PKT_GET_USER_LINE )
        return raw[4]

    def get_user_module_line(self, index):
        """
        Get the name of device with index: index (listi)
        """
        w = [ADMIN_HANDLER, PKT_GET_USER_LINE , NULL_BYTE]
        w.append(CMD_GET_USER_MODULE_LINE)
        w.append(index)
        self.dev.write(w)
        raw = self.dev.read(PKT_GET_LINE_RESPONSE)
        c = raw[4:len(raw)]
        t = ''
        for e in c:
            if not(e == NULL_BYTE):
                t = t + chr(e)
        return t

    def get_handler_size(self):
        """
        Get the number of handlers opened
        """
        w = [ADMIN_HANDLER, PKT_DEFAULT, NULL_BYTE]
        w.append(CMD_GET_HANDLER_SIZE)
        self.dev.write(w)
        raw = self.dev.read(PKT_HANDLER_RESPONSE)
        return raw[4]

    def get_handler_type(self, index):
        """
        Get the type of the handler: index (return listi index)
        """
        w = [ADMIN_HANDLER, PKT_GET_HANDLER_TYPE, NULL_BYTE]
        w.append(CMD_GET_HANDLER_TYPE)
        w.append(index)
        self.dev.write(w)
        raw = self.dev.read(PKT_HANDLER_RESPONSE)
        return raw[4]

    def switch_to_bootloader(self):
        """
        Admin module command to switch to bootloader
        """
        w = [ADMIN_HANDLER, PKT_DEFAULT, NULL_BYTE]
        w.append(CMD_SWITCH_TO_BOOT)
        self.dev.write(w)

    def reset(self):
        """
        Admin module command to reset the board
        """
        w = [ADMIN_HANDLER, PKT_DEFAULT, NULL_BYTE]
        w.append(CMD_RESET)
        self.dev.write(w)

    def force_close_all(self):
        """
        Admin module command to force close all opened modules
        """
        w = [ADMIN_HANDLER, PKT_DEFAULT, NULL_BYTE]
        w.append(CMD_CLOSEALL )
        self.dev.write(w)
        raw = self.dev.read(PKT_CLOSEALL)
        return raw[4]

