#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from gettext import gettext as _

from plugins.plugin import Plugin

import sys
sys.path.insert(0, os.path.abspath('./plugins/butia'))

from pybot import pybot_client

from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_blocks
from TurtleArt.talogo import logoerror
from TurtleArt.taprimitive import Primitive, ArgSlot
from TurtleArt.tatype import TYPE_INT, TYPE_NUMBER



#constants definitions
ERROR = -1   # default return value in case of error
MAX_SPEED = 1023   # max velocity for AX-12 - 10 bits -
MAX_SENSOR_PER_TYPE = 6
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"]
ERROR_DEG_ABS = _('ERROR: The degrees must be between 0 and 300')
ERROR_SPEED = _('ERROR: The speed must be a value between 0 and 1023')
ERROR_PIN_VALUE = _('ERROR: The value must be 0 or 1, LOW or HIGH')
ERROR_NO_CONECTADO = _('ERROR: The board is disconnected or the ID is out of range')
ERROR_ID_NO_VALIDO = _('ERROR: The specified ID is not available')


class Ax12(Plugin):

    def __init__(self,parent):
        Plugin.__init__(self)
        self.tw = parent
        self.butia = pybot_client.robot()

    def setup(self):
       
        palette = make_palette('ax12', COLOR_NOTPRESENT,_('AX-12 Motors functions'), translation=_('ax12'))

        palette.add_block('refresh Ax',
                     style='basic-style',
                     label=_('refresh AX12'),
                     prim_name='refresh Ax',
                     help_string=_('refresh the state of the Ax palette and blocks'))
        self.tw.lc.def_prim('refresh Ax', 0,
            Primitive(self.refreshAx))
        special_block_colors['refresh Ax'] = COLOR_PRESENT[:]

        palette.add_block('getID',
                     style='box-style',
                     label=_('getID'),
                     prim_name='getID',
                     help_string=_('return a random ID of the connected AX-motors'))
        self.tw.lc.def_prim('getID', 0,
            Primitive(self.getID))
        special_block_colors['getID'] = COLOR_NOTPRESENT[:]

        palette.add_block('stopAx',
            style='basic-style-1arg',
            label=[_('stop')],
            prim_name='stopAx',
            default=[1],
            help_string=_('stop the AX-12 motors '))
        self.tw.lc.def_prim('stopAx', 1,
            Primitive(self.stpSpeed, arg_descs=[ArgSlot(TYPE_NUMBER)]))
        special_block_colors['stopAx'] = COLOR_NOTPRESENT[:]

        palette.add_block('setAxPosition',
            style='basic-style-2arg',
            label=[_('set position'), _('idMotor'), _('degrees')],
            prim_name='setAxPosition',
            default=[1,0],
            help_string=_('set the position of the AX-12 motors'))
        self.tw.lc.def_prim('setAxPosition', 2,
            Primitive(self.sPosition, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['setAxPosition'] = COLOR_NOTPRESENT[:]

        palette.add_block('getAxPosition',
                style='number-style-1arg',
                label=[_('get position')],
                prim_name='getAxPosition',
                default=1,
                help_string=_('get the position of the AX-12 motors'))
        self.tw.lc.def_prim('getAxPosition', 1,
                Primitive(self.gPosition, TYPE_INT, [ArgSlot(TYPE_NUMBER)]))
        special_block_colors['getAxPosition'] = COLOR_NOTPRESENT[:]

        palette.add_block('setAxSpeed',
            style='basic-style-2arg',
            label=[_('set speed'), _('idMotor'), _('speed')],
            prim_name='setAxSpeed',
            default=[1,0],
            help_string=_('set the speed of the AX-12 motors'))
        self.tw.lc.def_prim('setAxSpeed', 2,
            Primitive(self.sSpeed, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['setAxSpeed'] = COLOR_NOTPRESENT[:]

        palette.add_block('getAxTemperature',
                style='number-style-1arg',
                label=[_('get temperature')],
                prim_name='getAxTemperature',
                default=1,
                help_string=_('get the temperature of the AX-12 motors'))
        self.tw.lc.def_prim('getAxTemperature', 1,
                Primitive(self.gTemp, TYPE_INT, [ArgSlot(TYPE_NUMBER)]))
        special_block_colors['getAxTemperature'] = COLOR_NOTPRESENT[:]

        palette.add_block('setAxLed',
            style='basic-style-2arg',
            label=[_('set led'), _('idMotor'), _('action')],
            prim_name='setAxLed',
            default=[1,0],
            help_string=_('turns the AX led motor with id idMotor when action = 1, turn off if action = 0'))
        self.tw.lc.def_prim('setAxLed', 2,
            Primitive(self.axLed,arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['setAxLed'] = COLOR_NOTPRESENT[:]

        palette.add_block('getAxVoltage',
                style='number-style-1arg',
                label=[_('get voltage')],
                prim_name='getAxVoltage',
                default=1,
                help_string=_('get the voltage of the AX-12 motors'))
        self.tw.lc.def_prim('getAxVoltage', 1,
                Primitive(self.gVolt, TYPE_INT, [ArgSlot(TYPE_NUMBER)]))
        special_block_colors['getAxVoltage'] = COLOR_NOTPRESENT[:]

    def gPosition(self, idMotor):
        idMotor = int(idMotor)
        a = self.butia.readInfo(str(idMotor),36,2)
        res = self.ajustarValor(a)
        res = (res * 300 / 1023)
        if (res == 19143):
            raise logoerror(ERROR_NO_CONECTADO)
        else:
            if (res == 19218):
                raise logoerror(ERROR_ID_NO_VALIDO)    
            return res
        
    def gTemp(self, idMotor):
        idMotor = int(idMotor)
        a = self.butia.readInfo(str(idMotor),43,2)
        res = self.ajustarValor(a)
        if (res == 65279):
            raise logoerror(ERROR_NO_CONECTADO)
        else:
            if (res == 65535):
                raise logoerror(ERROR_ID_NO_VALIDO)    
            return res
            

    def gVolt(self, idMotor):
        idMotor = int(idMotor)
        a = self.butia.readInfo(str(idMotor),42,2)
        volt = self.ajustarValor(a) 
        res = (float(volt)/1000)
        if (res == 65.279):
            raise logoerror(ERROR_NO_CONECTADO)
        else:
            if (res == 65.535):
                raise logoerror(ERROR_ID_NO_VALIDO)    
            return res
    
    def sPosition(self, idMotor, grados):
        grados = int(grados)
        if (grados < 0) or (grados > 300):
            raise logoerror(ERROR_DEG_ABS)
        else:   
            idMotor = int(idMotor)
            grados = (grados) * 1023 / 300
            self.butia.jointMode(str(idMotor))
            self.butia.setPosition(str(idMotor), str(abs(grados)))

    def refreshAx(self):
        i = self.getID()
        index = palette_name_to_index('ax12')
        if index is not None:
            ax12_blocks = palette_blocks[index]
            for block in self.tw.block_list.list:
                if block.name in ax12_blocks:
                    if (i != -1) or (block.name == 'refresh Ax'):
                        special_block_colors[block.name] = COLOR_PRESENT[:]
                    else:
                        special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                    block.refresh()
            self.tw.regenerate_palette(index)

    def sSpeed(self, idMotor, speed):
        idMotor = int(idMotor)
        speed= int(speed)
        if (speed < 0) or (speed > MAX_SPEED):
            raise logoerror(ERROR_SPEED)
        else:
            self.butia.wheelMode(str(idMotor))
            self.butia.setSpeed(str(idMotor), str(abs(speed)))

    def stpSpeed(self, idMotor):
        idMotor = int(idMotor)
        speed= 0
        self.butia.wheelMode(str(idMotor))
        self.butia.setSpeed(str(idMotor), str(abs(speed)))
      
    def getID(self):
        for id in range(253): 
            a = self.butia.readInfo(str(id), 3, 2)
            i = self.ajustarValor(a)
            if i == -1:
                return -1    
            else:
                if i < 65000:
                    return id
        return -1

    def axLed(self, idMotor, value):
        try:
            idMotor = int(idMotor)
            value = int(value)
        except:
            value = ERROR
        if (value < 0) or (value > 1):
            raise logoerror(ERROR_PIN_VALUE)
        else:
            if (value == 1):
                self.butia.writeInfo(str(idMotor), 25, 1)
            else:
                self.butia.writeInfo(str(idMotor), 25, 0)
                
    def ajustarValor(self, a):
        parte1 = a % 256
        parte2 = a / 256
        return (parte1 * 256 + parte2)

