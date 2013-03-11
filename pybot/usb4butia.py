#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# USB4Butia main
#
# Copyright (c) 2012-2013 Butiá Team butia@fing.edu.uy 
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


import os
import imp
import com_usb
from baseboard import Baseboard
from device import Device
from butia_functions import functions

ERROR = -1

class USB4Butia(functions):

    def __init__(self, debug=False, get_modules=True):
        functions.__init__(self)
        self._debug = debug
        self._hotplug = []
        self._openables = []
        self._drivers_loaded = {}
        self._bb = []
        self._b_ports = []
        self._modules = []
        self._get_all_drivers()
        self.find_butias(get_modules)

    def get_butia_count(self):
        """
        Gets the number of boards detected
        """
        return len(self._bb)

    def find_butias(self, get_modules=True):
        """
        Search for connected USB4Butia boards and open it
        """
        devices_ports = []
        devices = com_usb.find()
        for dev in devices:
            n = dev.device.dev.address
            devices_ports.append(n)
            if not(n in self._b_ports):
                b = Baseboard(dev)
                try:
                    b.open_baseboard()
                    self._bb.append(b)
                    self._b_ports.append(n)
                except:
                    if self._debug:
                        print 'error open baseboard'

        for b in self._bb:
            n = b.dev.device.dev.address
            if not(n in devices_ports):
                self._bb.remove(b)
                self._b_ports.remove(n)
                try:
                    b.close_baseboard()
                except:
                    pass

        if get_modules:
            self.get_modules_list()

    def get_modules_list(self, normal=True):
        """
        Get the list of modules loaded in the board
        """
        self._modules = []
        n_boards = self.get_butia_count()

        if self._debug:
            print '=Listing Devices'

        for i, b in enumerate(self._bb):
            try:
                listi = b.get_listi()
                s = b.get_handler_size()

                if self._debug:
                    print '===board', i

                for m in range(0, s + 1):
                    module_name = listi[b.get_handler_type(m)]
                    if n_boards > 1:
                        complete_name = module_name + '@' + str(i) + ':' +  str(m)
                    else:
                        complete_name = module_name + ':' +  str(m)

                    if self._debug:
                        print '=====module', module_name, (8 - len(module_name)) * ' ', complete_name

                    if not(module_name == 'port'):

                        if normal:
                            self._modules.append(complete_name)
                        else:
                            self._modules.append((str(m), module_name, str(i)))

                        if not(b.devices.has_key(m) and (b.devices[m].name == module_name)):
                            d = Device(b, module_name, m, self._drivers_loaded[module_name])
                            b.add_device(m, d)
                            if module_name in self._openables:
                                b.add_openable_loaded(module_name)
                    else:
                        if b.devices.has_key(m):
                            b.devices.pop(m)

            except Exception, err:
                if self._debug:
                    print 'error module list', err

        return self._modules

    def _get_all_drivers(self):
        """
        Load the drivers for the differents devices
        """
        # current folder
        path_drivers = os.path.join(os.path.dirname(__file__), 'drivers')
        if self._debug:
            print 'Searching drivers in: ', path_drivers
        # normal drivers
        tmp = os.listdir(path_drivers)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py'):
                name = d.replace('.py', '')
                self._openables.append(name)
                self._get_driver(path_drivers, name)
        # hotplug drivers
        path = os.path.join(path_drivers, 'hotplug')
        tmp = os.listdir(path)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py'):
                name = d.replace('.py', '')
                self._hotplug.append(name)
                self._get_driver(path, name)

    def _get_driver(self, path, driver):
        """
        Get a specify driver
        """
        if self._debug:
            print 'Loading driver %s...' % driver
        abs_path = os.path.abspath(os.path.join(path, driver + '.py'))
        f = None
        try:
            f = imp.load_source(driver, abs_path)
            self._drivers_loaded[driver] = f
        except:
            if self._debug:
                print 'Cannot load %s' % driver, abs_path
        
    def callModule(self, modulename, board_number, number, function, params = ''):
        """
        Call one function: function for module: modulename in board: board_name
        with handler: number (only if the module is pnp, else, the parameter is
        None) with parameteres: params
        """
        if number == '':
            number = 0
        else:
            number = int(number)
        board_number = int(board_number)
        try:
            board = self._bb[board_number]
            if board.devices.has_key(number) and (board.devices[number].name == modulename):
                return board.devices[number].call_function(function, params)
            else:
                if modulename in self._openables:
                    if modulename in board.get_openables_loaded():
                        number = board.get_device_handler(modulename)
                    else:
                        board.add_openable_loaded(modulename)
                        dev = Device(board, modulename, func=self._drivers_loaded[modulename])
                        number = dev.module_open()
                        board.add_device(number, dev)
                    return board.devices[number].call_function(function, params)
                else:
                    if self._debug:
                        print 'no open and no openable'
                    return ERROR
        except Exception, err:
            if self._debug:
                print 'error call module', err
            return ERROR

    def reconnect(self):
        """
        Not implemented
        """
        pass

    def refresh(self):
        """
        Refresh: if no boards presents, search for them.. else, check if 
        the boards continues present
        """
        self.find_butias(False)

    def close(self):
        """
        Closes all open baseboards
        """
        for b in self._bb:
            try:
                b.close_baseboard()
            except:
                if self._debug:
                    print 'error in close baseboard'
        self._bb = []

 
