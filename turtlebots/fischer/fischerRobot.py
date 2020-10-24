#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Fischer abstraction
#
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

import threading
from time import sleep, time

ACTUADOR_M1 = 1
ACTUADOR_M2 = 2
ACTUADOR_MB = 3

BAS_MSG = [0xa5, 0x01, 0x00]
MID_MSG = [0x0f, 0x00, 0x00, 0x00, 0x00]
END_MSG = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

ACT_1_MSG = BAS_MSG + [0x01, 0x3f, 0x00, 0x00] + MID_MSG * 4 + END_MSG
ACT_2_MSG = BAS_MSG + [0x04, 0xc0, 0x0f, 0x00] + MID_MSG * 4 + END_MSG
ACT_B_MSG = BAS_MSG + [0x05, 0xff, 0x0f, 0x00] + MID_MSG * 4 + END_MSG


class FischerRobot():

    def __init__(self, dev, debug=False):
        self.dev = dev
        self.debug = debug
        self.sensors = [0, 0, 0]
        self.actuators = [0, 0]
        self.pollSensor = [time(),time(),time()]
        self.both = False
        self.msg_to_send = []
        self.lock = threading.Lock()
        self.threadOff = True

    def _debug(self, message, err=''):
        if self.debug:
            print(message, err)

    def open_ft(self):
        """
        Open the comunication
        """
        self.dev.open_device()
        msg = self._createActuatorMsg(1, 0)
        self.dev.write(msg)
        msg[3]=0x00
        self.dev.write(msg)

    def close_ft(self):
        """
        Close the comunication
        """
        self.dev.close_device()

    def get_info(self):
        """
        Get Fischer info: manufacture..
        """
        return self.dev.get_info()

    def getSensor(self, idSensor):
        now = time()
        if (self.pollSensor[idSensor] + 0.50) < now:
            ret = self.dev.read(98)
            ret = self.dev.read(98)
            self._conectSensor(ret)
            self.pollSensor[idSensor] = now
        return self.sensors[idSensor]

    def getActuator(self, idActuator):
        return self.actuators[idActuator - 1]

    def turnActuator(self, idActuator, power):
        if self.threadOff:
            self.threadOff = False
            t = threading.Thread(target=self._sendMsg)
            t.start()

        idActuator = idActuator - 1

        if self.actuators[idActuator] == power:
            return

        self.actuators[idActuator] = power

        if power != 0:
            if self.both == False: 
                if (self.actuators[0] == 0) or (self.actuators[1] == 0):
                    msg = self._createActuatorMsg(idActuator + 1, power)
                else:
                    self.both = True
                    msg = self._createActuatorMsg(ACTUADOR_MB, power)
                self._actuatorOn(msg)
            else:
                msg = self._createActuatorMsg(ACTUADOR_MB, power)
                self._actuatorOn(msg)
        else:
            self._actuatorOff(idActuator)

    def quit(self):
        self.lock.acquire()
        self.threadOff = True
        self.lock.release()

    def _actuatorOn(self, msg):
        self.lock.acquire()
        self.msg_to_send = msg
        self.lock.release()

    def _actuatorOff(self, idActuator):
        power = 0
        if self.both:
            
            msg = self._createActuatorMsg(ACTUADOR_MB, power)
            self._actuatorOn(msg)
            self.both = False

            if  idActuator != (ACTUADOR_M1-1):
                idActuator = ACTUADOR_M1
            else:
                idActuator = ACTUADOR_M2

            power = self.actuators[idActuator-1]
            msg = self._createActuatorMsg(idActuator, power)
            self._actuatorOn(msg)
        else:
            msg = self._createActuatorMsg(idActuator+1, power)
            self._actuatorOn(msg)
            sleep(0.1)
            self.quit()
            
    def _createActuatorMsg(self, num, power):
        if num == ACTUADOR_M1:
            msg = ACT_1_MSG[:]
        elif num == ACTUADOR_M2:
            msg = ACT_2_MSG[:]
        else:
            msg = ACT_B_MSG[:]

        if power == 0:
            msg[3]=0x00
            return msg

        msg = self._modifyPower(num, msg, power)
        msg = self._modifyReverse(msg)

        return msg

    def _modifyReverse(self, msg):
        a1_reverse = self.actuators[0] < 0
        a2_reverse = self.actuators[1] < 0

        if self.both:
            if a1_reverse:
                if a2_reverse:
                    msg[3] = 0x0a
                else:
                    msg[3] = 0x06
            else:
                if a2_reverse:
                    msg[3] = 0x09
        else:
            if a1_reverse:
                msg[3] = 0x02
            if a2_reverse:
                msg[3] = 0x08

        return msg

    def _modifyPower(self, num, msg, power):
        power = abs(power)
        if power == 40 or power == 70:
            power = power - 10
        
        if self.both:
            power = self._calculatePower(11, power) + self._calculatePower(100, power)
            msg[5] = self._byteFive(power)
        else:
            if num == ACTUADOR_M1:
                power = self._calculatePower(11, power)
            elif num == ACTUADOR_M2:
                power = self._calculatePower(100, power)
                msg[5] = self._byteFive(power)

        ret = hex(int(str(power),8))
        msg[4] = int(ret, 0) % 256

        return msg

    def _sendMsg(self):
        while self.threadOff == False:
            self.dev.write(self.msg_to_send)

    def _byteFive(self, power):
        if power == 10:
            b = 0x00
        elif power == 20:
            b = 0x02
        elif power == 30 or power == 40:
            b = 0x04
        elif power == 50:
            b = 0x06
        elif power == 60 or power == 70:
            b = 0x09
        elif power == 80:
            b = 0x0b
        elif power == 90:
            b = 0x0d
        else:
            b = 0x0f 
        return b

    def _calculatePower(self, x, power):
        if power <= 10:
            p = 0
        elif power > 10 and power <= 20:
            p = 1
        elif power > 20 and power <= 30:
            p = 2
        elif power > 30 and power <= 40:
            p = 2
        elif power > 40 and power <= 50:
            p = 3
        elif power > 50 and power <= 60:
            p = 4
        elif power > 60 and power <= 70:
            p = 4
        elif power > 70 and power <= 80:
            p = 5
        elif power > 80 and power <= 90:
            p = 6
        elif power > 90:
            p = 7

        return x * p

    def _conectSensor(self, msg):
        self.sensors[0] = 0
        self.sensors[1] = 0
        self.sensors[2] = 0
        if msg[3]==2:#I2
            self.sensors[1] = 1 
        elif msg[3]==1:#I1
            self.sensors[0] = 1
        elif msg[3]==4:#I3
            self.sensors[2] = 1
        elif msg[3]==3:#I1 e I2
            self.sensors[0] = 1
            self.sensors[1] = 1
        elif msg[3]==6:#I2 e I3
            self.sensors[1] = 1
            self.sensors[2] = 1
        elif msg[3]==5:#I1 e I3
            self.sensors[0] = 1
            self.sensors[2] = 1
        elif msg[3]==7:#all
            self.sensors[0] = 1
            self.sensors[1] = 1
            self.sensors[2] = 1

