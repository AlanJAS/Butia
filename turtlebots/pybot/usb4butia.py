#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# USB4Butia main
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


import os
import importlib.util
import inspect
import com_usb
from baseboard import Baseboard
from device import Device


ERROR = -1

class USB4Butia():

    def __init__(self, debug=False, get_modules=True):
        self._debug_flag = debug
        self._hotplug = []
        self._openables = []
        self._drivers_loaded = {}
        self._bb = []
        self._b_ports = []
        self._get_all_drivers()
        self.refresh()
        if get_modules:
            self.getModulesList(refresh=False)

    def _debug(self, message, err=''):
        if self._debug_flag:
            print(message, err)

    def closeService(self):
        """
        Close bobot service
        """
        return 0

    def getButiaCount(self):
        """
        Gets the number of boards detected
        """
        return len(self._bb)

    def getModulesList(self, refresh=True):
        """
        Get the list of modules loaded in the board
        """
        self._debug('=Listing Devices')
        modules = []
        if refresh:
            self.refresh()
        n_boards = self.getButiaCount()
        for i, b in enumerate(self._bb):
            try:
                listi = b.get_listi()
                s = b.get_handler_size()
                self._debug('===board', i)
                for m in range(0, s + 1):
                    t = b.get_handler_type(m)
                    if not (t == 255):
                        module_name = listi[t]
                        if n_boards > 1:
                            complete_name = module_name + '@' + str(i) + ':' +  str(m)
                        else:
                            complete_name = module_name + ':' +  str(m)
                        self._debug('=====module ' + module_name + (9 - len(module_name)) * ' ' + complete_name)
                        if not(module_name == 'port'):
                            modules.append(complete_name)
                            if not(m in b.devices and (b.devices[m].name == module_name)):
                                d = Device(b, module_name, m, self._drivers_loaded[module_name], module_name in self._openables)
                                b.add_device(m, d)
                        else:
                            b.remove_device(m)
            except Exception as err:
                self._debug('ERROR:usb4butia:get_modules_list', err)
        return modules

    def _get_all_drivers(self):
        """
        Load the drivers for the differents devices
        """
        # current folder
        path_drivers = os.path.join(os.path.dirname(__file__), 'drivers')
        self._debug('Searching drivers in: ', str(path_drivers))
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
        self._debug('Loading driver %s...' % driver)
        abs_path = os.path.abspath(os.path.join(path, driver + '.py'))
        try:
            spec = importlib.util.spec_from_file_location(driver, abs_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._drivers_loaded[driver] = module
        except Exception:
            self._debug('ERROR:usb4butia:_get_driver cannot load %s' % driver, abs_path)
        
    def callModule(self, modulename, board_number, number, function, params = []):
        """
        Call one function: function for module: modulename in board: board_name
        with handler: number (only if the module is pnp, else, the parameter is
        None) with parameteres: params
        """
        try:
            number = int(number)
            board_number = int(board_number)
            if len(self._bb) < (board_number + 1):
                return ERROR
            board = self._bb[board_number]
            if number in board.devices and (board.devices[number].name == modulename):
                return board.devices[number].call_function(function, params)
            else:
                number = self._open_or_validate(modulename, board)
                if number == ERROR:
                    return ERROR
                return board.devices[number].call_function(function, params)
        except Exception as err:
            if hasattr(err, 'errno'):
                if (err.errno == 5) or (err.errno == 19):
                    self.closeB(board)
            self._debug('ERROR:usb4butia:callModule', err)
            return ERROR

    def refresh(self):
        """
        Search for connected USB4Butia boards and open it
        """
        devices_ports = []
        devices = com_usb.find()
        for dev in devices:
            n = dev.get_address()
            if not(n == None):
                devices_ports.append(n)
                if not(n in self._b_ports):
                    b = Baseboard(dev)
                    try:
                        b.open_baseboard()
                        self._bb.append(b)
                        self._b_ports.append(n)
                    except Exception as err:
                        self._debug('ERROR:usb4butia:refresh', err)

        for b in self._bb:
            n = b.dev.get_address()
            if not(n in devices_ports):
                self.closeB(b)

    def closeB(self, b):
        try:
            n = b.dev.get_address()
            self._bb.remove(b)
            b.close_baseboard()
            if n in self._b_ports:
                self._b_ports.remove(n)
        except:
            pass

    def close(self):
        """
        Closes all open baseboards
        """
        for b in self._bb:
            self.closeB(b)
        self._bb = []
        self._b_ports = []

    def moduleOpen(self, mod):
        """
        Open the module mod
        """
        split = self._split_module(mod)
        modulename = split[1]
        b = int(split[2])
        if len(self._bb) < (b + 1):
            return ERROR
        board = self._bb[b]
        return self._open_or_validate(modulename, board)

    def _open_or_validate(self, modulename, board):
        """
        Open o check if modulename module is open in board: board
        """
        if modulename in self._openables:
            if modulename in board.get_openables_loaded():
                return board.get_device_handler(modulename)
            else:
                dev = Device(board, modulename, None, self._drivers_loaded[modulename], True)
                number = dev.module_open()
                if number == 255:
                    self._debug('cannot open module', modulename)
                    return ERROR
                else:
                    board.add_device(number, dev)
                    return number
        return ERROR

    def moduleClose(self, mod):
        """
        Close the module mod
        """
        split = self._split_module(mod)
        modulename = split[1]
        if modulename in self._openables:
            b = int(split[2])
            if len(self._bb) < (b + 1):
                return ERROR
            board = self._bb[b]
            if modulename in board.get_openables_loaded():
                number = board.get_device_handler(modulename)
                try:
                    res = board.devices[number].module_close()
                    if res == 1:
                        board.remove_device(number)
                        return res
                except Exception as err:
                    self._debug('ERROR:usb4butia:moduleClose', err)
                    return ERROR
            else:
                self._debug('cannot close no opened module')
                return ERROR
        else:
            self._debug('cannot close no openable module')
        return ERROR

    def getListi(self, board_number=0):
        """
        returns a list of instanciables modules
        """
        board_number = int(board_number)
        if len(self._bb) < (board_number + 1):
            return []
        board = self._bb[board_number]
        listi = board.get_listi()
        return listi.values()

    def describe(self, mod):
        """
        Describe the functions of a modulename
        """
        split = self._split_module(mod)
        mod = split[1]
        d = {}
        if mod in self._drivers_loaded:
            driver = self._drivers_loaded[mod]
            funcs = dir(driver)
            if '__spec__' in funcs:
                index = funcs.index('__spec__')
                funcs = funcs[index:]
            for f in funcs:
                h = getattr(driver, f)
                try:
                    i = inspect.getfullargspec(h)
                    parameters = i[0]
                    if 'dev' in parameters:
                        parameters.remove('dev')
                    d[f] = parameters
                except:
                    pass
        return d

    def isPresent(self, module_name):
        """
        Check if module: module_name is present
        """
        module_list = self.getModulesList()
        return (module_name in module_list)

    ############################## Movement calls ##############################

    def set2MotorSpeed(self, leftSense='0', leftSpeed='0', rightSense='0', rightSpeed='0', board='0'):
        """
        Set the speed of 2 motors. The sense is 0 or 1, and the speed is
        between 0 and 1023
        """
        msg = [str(leftSense), str(leftSpeed), str(rightSense), str(rightSpeed)]
        return self.callModule('motors', str(board), '0', 'setvel2mtr', msg)

    def setMotorSpeed(self, idMotor='0', sense='0', speed='0', board='0'):
        """
        Set the speed of one motor. idMotor = 0 for left motor and 1 for the
        right motor. The sense is 0 or 1, and the speed is between 0 and 1023
        """
        msg = [str(idMotor), str(sense), str(speed)]
        return self.callModule('motors', str(board), '0', 'setvelmtr', msg)

    def getMotorType(self, board='0'):
        """
        If AX-12 motors present returns 1. If there are a shield "cc" returns 2
        """
        return self.callModule('motors', str(board), '0', 'getType')

    ##################### Operations for ax.lua driver #########################

    def writeInfo(self, idMotor, regstart, value, board='0'):
        """
        Writes the motor: idMotor in the registry: regstart with value: value
        """
        msg = [str(idMotor), str(regstart), str(value)]
        return self.callModule('ax', str(board), '0', 'writeInfo', msg)

    def readInfo(self, idMotor, regstart, length='1', board='0'):
        """
        Reads the motor: idMotor in the registry: regstart
        """
        msg = [str(idMotor), str(regstart), str(length)]
        return self.callModule('ax', str(board), '0', 'readInfo', msg)

    def sendPacket(self, msg, board='0'):
        """
        Send a raw packet to ax module
        """
        msg_s = [str(i) for i in msg]
        return self.callModule('ax', str(board), '0', 'sendPacket', msg_s)

    def wheelMode(self, idMotor='0', board='0'):
        """
        Sets the motor: idMotor in wheel mode (continuos rotation)
        """
        msg = [str(idMotor)]
        return self.callModule('ax', str(board), '0', 'wheelMode', msg)
     
    def jointMode(self, idMotor='0', _min='0', _max='1023', board='0'):
        """
        Sets the motor: idMotor in servo mode
        """
        msg = [str(idMotor), str(_min), str(_max)]
        return self.callModule('ax', str(board), '0', 'jointMode', msg)

    def setPosition(self, idMotor='0', pos='0', board='0'):
        """
        Sets the position: pos of the motor: idMotor
        """
        msg = [str(idMotor), str(pos)]
        return self.callModule('ax', str(board), '0', 'setPosition', msg)

    def getPosition(self, idMotor='0', board='0'):
        """
        Gets the position of motor: idMotor
        """
        msg = [str(idMotor)]
        return self.callModule('ax', str(board), '0', 'getPosition', msg)

    def setSpeed(self, idMotor='0', speed='0', board='0'):
        """
        Set the speed: speed to the motor: idMotor
        """
        msg = [str(idMotor), str(speed)]
        return self.callModule('ax', str(board), '0', 'setSpeed', msg)

    ############################### General calls ##############################
     
    def getBatteryCharge(self, board='0'):
        """
        Gets the battery level charge
        """
        return self.callModule('butia', str(board), '0', 'getVolt')

    def getVersion(self, board='0'):
        """
        Gets the version of Butiá module. 22 for new version
        """
        return self.callModule('butia', str(board), '0', 'getVersion')

    def getFirmwareVersion(self, board='0'):
        """
        Gets the version of the Firmware
        """
        return self.callModule('admin', str(board), '0', 'getVersion')

    ############################### Sensors calls ###############################

    def getButton(self, port, board='0'):
        """
        Gets the value of the button connected in port
        """
        return self.callModule('button', str(board), str(port), 'getValue')
    
    def getLight(self, port, board='0'):
        """
        Gets the value of the light sensor connected in port
        """
        return self.callModule('light', str(board), str(port), 'getValue')

    def getDistance(self, port, board='0'):
        """
        Gets the value of the distance sensor connected in port
        """
        return self.callModule('distanc', str(board), str(port), 'getValue')

    def getGray(self, port, board='0'):
        """
        Gets the value of the gray sensor connected in port
        """
        return self.callModule('grey', str(board), str(port), 'getValue')

    def getResistance(self, port, board='0'):
        """
        Gets the value of the resistance sensor connected in port
        """
        return self.callModule('res', str(board), str(port), 'getValue')

    def getVoltage(self, port, board='0'):
        """
        Gets the value of the voltage sensor connected in port
        """
        return self.callModule('volt', str(board), str(port), 'getValue')

    def getTemperature(self, port, board='0'):
        """
        Gets the value of the temperature sensor connected in port
        """
        return self.callModule('temp', str(board), str(port), 'getValue')

    ############################### Actuators calls ###############################

    def setLed(self, port, on_off, board='0'):
        """
        Sets on or off the LED connected in port (0 is off, 1 is on)
        """
        return self.callModule('led', str(board), str(port), 'turn', [str(on_off)])

    def setRelay(self, port, on_off, board='0'):
        """
        Sets on or off the Relay connected in port (0 is off, 1 is on)
        """
        return self.callModule('relay', str(board), str(port), 'turn', [str(on_off)])

    ################################ Extras ################################

    def setModeHack(self, pin, mode, board='0'):
        """
        Sets the mode of hack pin. If mode 0 = output, mode 1 = input
        """
        msg = [str(pin), str(mode)]
        return self.callModule('hackp', str(board), '0', 'setMode', msg)

    def getModeHack(self, pin, board='0'):
        """
        Get the mode of hack pin. If mode 0 = output, mode 1 = input
        """
        return self.callModule('hackp', str(board), '0', 'getMode', [str(pin)])

    def setHack(self, pin, value, board='0'):
        """
        Sets the value of hack pin configured as output. Value is 0 or 1
        """
        msg = [str(pin), str(value)]
        return self.callModule('hackp', str(board), '0', 'write', msg)

    def getHack(self, pin, board='0'):
        """
        Gets the value of hack pin configured as input. Returns 0 or 1
        """
        return self.callModule('hackp', str(board), '0', 'read', [str(pin)])

    ############################# Generic modules #############################

    def getModuleA(self, port, board='0'):
        """
        Gets the value of the generic sensor A connected in port
        """
        return self.callModule('modSenA', str(board), str(port), 'getValue')

    def getModuleB(self, port, board='0'):
        """
        Gets the value of the generic sensor B connected in port
        """
        return self.callModule('modSenB', str(board), str(port), 'getValue')

    def getModuleC(self, port, board='0'):
        """
        Gets the value of the generic sensor C connected in port
        """
        return self.callModule('modSenC', str(board), str(port), 'getValue')

    def setModuleA(self, port, on_off, board='0'):
        """
        Sets on or off the generic actuator module A
        """
        return self.callModule('modActA', str(board), str(port), 'turn', [str(on_off)])

    def setModuleB(self, port, on_off, board='0'):
        """
        Sets on or off the generic actuator module B
        """
        return self.callModule('modActB', str(board), str(port), 'turn', [str(on_off)])

    def setModuleC(self, port, on_off, board='0'):
        """
        Sets on or off the generic actuator module C
        """
        return self.callModule('modActC', str(board), str(port), 'turn', [str(on_off)])

    ############################# Useful functions #############################

    def _split_module(self, mbn):
        """
        Split a modulename: module@board:port to (number, modulename, board)
        """
        board, number = '0', '0'
        modulename = mbn
        if '@' in mbn:
            modulename, rest = mbn.split('@')
            if ':' in rest:
                board, number = rest.split(':')
            else:
                board = rest
        elif ':' in mbn:
            modulename, number = mbn.split(':')

        return (number, modulename, board)

    def _get_pybot_version(self):
        try:
            import __init__
            return __init__.__version__
        except:
            return 'Unknow'

