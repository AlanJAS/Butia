#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# Client for pybot_server
#
# Copyright (c) 2012-2020 Alan Aguiar alanjas@hotmail.com
# Copyright (c) 2009-2020 Butiá Team butia@fing.edu.uy
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
#
# Implements abstractions for the comunications with the bobot-server
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

import sys
import socket
import threading
import errno


ERROR = -1

PYBOT_HOST = 'localhost'
PYBOT_PORT = 2009

class robot():
    
    def __init__(self, host=PYBOT_HOST, port=PYBOT_PORT, auto_connect=True):
        """
        init the robot class
        """
        self._lock = threading.Lock()
        self._host = host
        self._port = port
        self._client = None
        if auto_connect:
            self.reconnect()
       
    def _doCommand(self, msg):
        """
        Executes a command in butia.
        @param msg message to be executed
        """
        msg = msg + '\n'
        msg = msg.encode()
        ret = ERROR
        self._lock.acquire()
        try:
            self._client.send(msg)
            ret = self._client.recv(1024)
            ret = ret.decode()
            ret = ret[:-1]
        except Exception as e:
            self._process_error(e)
        try:
            ret = int(ret)
        except:
            pass
        self._lock.release()
        return ret

    def _process_error(self, e):
        if hasattr(e, 'errno'):
            if e.errno == errno.EPIPE:
                self.reconnect()

    def reconnect(self):
        """
        connect o reconnect the bobot
        """
        self.close()
        try:
            self._client = socket.socket()
            self._client.connect((self._host, self._port))
        except:
            return ERROR
        return 0

    def refresh(self):
        """
        ask bobot for refresh is state of devices connected
        """
        self._doCommand('REFRESH')

    def close(self):
        """
        close the comunication with pybot
        """
        ret = 0
        try:
            self._client.close()
        except:
            ret = ERROR
        self._client = None
        return ret

    def callModule(self, modulename, board_number, number, function, params = []):
        """
        call the module 'modulename'
        """
        msg = 'CALL ' + modulename + '@' + str(board_number) + ':' + str(number) + ' ' + function
        if not(params == []):
            msg = msg + ' ' + ' '.join(params)
        return self._doCommand(msg)

    def closeService(self):
        """
        Close bobot service
        """
        return self._doCommand('QUIT')

    def getButiaCount(self):
        """
        Gets the number of boards detected
        """
        return self._doCommand('BUTIA_COUNT')

    def getModulesList(self):
        """
        returns a list of modules
        """
        ret = self._doCommand('LIST')
        if (ret == ERROR) or (ret == ''):
            return []
        else:
            return ret.split(',')

    def getListi(self, board_number=0):
        """
        returns a list of instanciables modules
        """
        ret = self._doCommand('LISTI ' + str(board_number))
        if (ret == ERROR) or (ret == ''):
            return []
        else:
            return ret.split(',')

    def describe(self, mod):
        """
        Describe the functions of a modulename
        """
        split = self._split_module(mod)
        mod = split[1]
        ret = self._doCommand('DESCRIBE ' + mod)
        return ret

    def moduleOpen(self, mod):
        """
        Open the module mod
        """
        return self._doCommand('OPEN ' + mod)

    def moduleClose(self, mod):
        """
        Close the module mod
        """
        return self._doCommand('CLOSE ' + mod)

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


def show_help():
    print("Open PyBot client in HOST and PORT.")
    print("")
    print("Usage:")
    print(" pybot_client.py")
    print(" pybot_client.py [HOST]")
    print(" pybot_client.py [HOST] [PORT]")
    print("")
    print("Default values:")
    print(" HOST                      localhost")
    print(" PORT                      2009")
    print("")

if __name__ == "__main__":
    argv = sys.argv[:]
    if ("-h" in argv) or ("--help" in argv):
        show_help()
    else:
        server_host = PYBOT_HOST
        server_port = PYBOT_PORT
        if len(argv) > 1:
            server_host = argv[1]
        if len(argv) > 2:
            server_port = int(argv[2])
        c = robot(server_host, server_port)
        run = True
        while run:
            m = input("> ")
            ret = c._doCommand(m)
            print(ret)
            if m == "QUIT":  
                run = False
        c.close()

