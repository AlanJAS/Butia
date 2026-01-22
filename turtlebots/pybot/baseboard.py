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

    def _send_command(self, handler, command=None, packet_size=PKT_DEFAULT, payload=None, read_size=None):
        if command:
            packet = [handler, packet_size, NULL_BYTE, command]
            if payload:
                packet.extend(payload)
            self.dev.write(packet)
        if read_size:
            response = self.dev.read(read_size)
            return response[4]
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
        return self._send_command(ADMIN_HANDLER, CMD_GET_USER_MODULES_SIZE, read_size=PKT_GET_USER_LINE)

    def get_user_module_line(self, index):
        """
        Get the name of device with index: index (listi)
        """
        raw = self._send_command(ADMIN_HANDLER, CMD_GET_USER_MODULE_LINE, PKT_GET_USER_LINE, [index], PKT_GET_LINE_RESPONSE)
        t = ''
        for e in raw[4:]:
            if not(e == NULL_BYTE):
                t = t + chr(e)
        return t

    def get_handler_size(self):
        """
        Get the number of handlers opened
        """
        return self._send_command(ADMIN_HANDLER, CMD_GET_HANDLER_SIZE, read_size=PKT_HANDLER_RESPONSE)

    def get_handler_type(self, index):
        """
        Get the type of the handler: index (return listi index)
        """
        return self._send_command(ADMIN_HANDLER, CMD_GET_HANDLER_TYPE, PKT_GET_HANDLER_TYPE, [index], PKT_HANDLER_RESPONSE)

    def switch_to_bootloader(self):
        """
        Admin module command to switch to bootloader
        """
        self._send_command(ADMIN_HANDLER, CMD_SWITCH_TO_BOOT)

    def reset(self):
        """
        Admin module command to reset the board
        """
        self._send_command(ADMIN_HANDLER, CMD_RESET)

    def force_close_all(self):
        """
        Admin module command to force close all opened modules
        """
        return self._send_command(ADMIN_HANDLER, CMD_CLOSEALL, read_size=PKT_CLOSEALL)
