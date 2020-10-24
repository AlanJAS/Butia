#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Andrés Aguirre <aaguirre@fing.edu.uy>
# Copyright (c) 2014 Mercedes Marzoa <mmarzoa@fing.edu.uy>
# Copyright (C) 2014 Alan Aguiar <alanjas@hotmail.com>
# Copyright (C) 2014 Butiá Team butia@fing.edu.uy 
# Butia is a free open plataform for robotics projects
# www.fing.edu.uy/inco/proyectos/butia
# Universidad de la República del Uruguay
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
import sys

from gettext import gettext as _

from plugins.plugin import Plugin

from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_blocks
from TurtleArt.talogo import logoerror
from TurtleArt.taconstants import CONSTANTS
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_INT, TYPE_STRING, TYPE_NUMBER

sys.path.insert(0, os.path.abspath('./plugins/fischer'))
import usb
import com_usb
from fischerRobot import FischerRobot


COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
COLOR_PRESENT = ["#FF6060", "#A06060"]

ERROR_BRICK = _('Please check the connection with the fischer')
ERROR_PORT_M = _("Invalid port '%s'. Port must be: PORT 1 or 2")
ERROR_PORT_S = _("Invalid port '%s'. Port must be: PORT 1, 2 or 3")
ERROR_POWER = _('The value of power must be an integer between -100 to 100')
ERROR_NO_NUMBER = _("The parameter must be a integer, not '%s'")
ERROR_UNKNOW_SENSOR = ("Unknow '%s' sensor")
ERROR_GENERIC = _('An error has occurred: check all connections and try to reconnect')
ERROR = -1
BRICK_FOUND = _('Found %s Fischers')
BRICK_NOT_FOUND = _('Fischer not found')
BRICK_INDEX_NOT_FOUND = _('Fischer number %s was not found')


FT_SENSOR_PORTS = [1, 2, 3]
FT_ACTUATOR_PORTS = [1, 2]


class Fischer(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        self._fischers = []
        self.active_fischer = 0

    def setup(self):

        # Palette of Motors
        palette = make_palette('fischer', COLOR_NOTPRESENT,
                            _('Palette of Fischertechnik robot'),
                            translation=_('fischer'))

        palette.add_block('ftrefresh',
                    style='basic-style',
                    label=_('refresh Fischer'),
                    prim_name='ftrefresh',
                    help_string=_('Search for a connected Fischer brick.'))
        self.tw.lc.def_prim('ftrefresh', 0,
            Primitive(self.refresh))
        special_block_colors['ftrefresh'] = COLOR_PRESENT[:]

        palette.add_block('ftselect',
                    style='basic-style-1arg',
                    default = 1,
                    label=_('Fischer'),
                    help_string=_('set current Fischer device'),
                    prim_name = 'ftselect')
        self.tw.lc.def_prim('ftselect', 1,
            Primitive(self.select, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('ftcount',
                    style='box-style',
                    label=_('number of Fischers'),
                    help_string=_('number of Fischer devices'),
                    prim_name = 'ftcount')
        self.tw.lc.def_prim('ftcount', 0,
            Primitive(self.count, TYPE_INT))

        palette.add_block('ftlight',
                    style='number-style-1arg',
                    label=_('light'),
                    default=[1],
                    help_string=_('light sensor'),
                    prim_name='ftlight')
        self.tw.lc.def_prim('ftlight', 1,
            Primitive(self.getLight, TYPE_INT, [ArgSlot(TYPE_INT)]))

        palette.add_block('ftbutton',
                  style='number-style-1arg',
                  label=_('button'),
                  default=[1],
                  help_string=_('button sensor'),
                  prim_name='ftbutton')
        self.tw.lc.def_prim('ftbutton', 1,
            Primitive(self.getButton, TYPE_INT, [ArgSlot(TYPE_INT)]))

        palette.add_block('ftturnactuator',
                    style='basic-style-2arg',
                    label=[_('actuator'), _('port'), _('power')],
                    default=[1, 100],
                    help_string=_('turn an actuator'),
                    prim_name='ftturnactuator')
        self.tw.lc.def_prim('ftturnactuator', 2,
            Primitive(self.turnactuator, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))


    ############################### Turtle signals ############################

    def stop(self):
        self._stopActuators()

    def quit(self):
        self._close_fischers()

    ################################# Primitives ##############################

    def turnactuator(self, port, power):
        if self._fischers:
            try:
                port = int(port)
            except:
                pass
            try:
                power = int(power)
            except:
                pass
            if (port in FT_ACTUATOR_PORTS):
                if (power >= -100) and (power <= 100):
                    try:
                        f = self._fischers[self.active_fischer]
                        f.turnActuator(port, power)
                    except:
                        raise logoerror(ERROR_GENERIC)
                else:
                    raise logoerror(ERROR_POWER)
            else:
                raise logoerror(ERROR_PORT_M % port)
        else:
            raise logoerror(ERROR_BRICK)

    def getLight(self, port):
        if self._fischers:
            try:
                port = int(port)
            except:
                pass
            if (port in FT_SENSOR_PORTS):
                res = ERROR
                try:
                    f = self._fischers[self.active_fischer]
                    res = f.getSensor(port-1)
                except:
                    pass
                return res
            else:
                raise logoerror(ERROR_PORT_S % port)
        else:
            raise logoerror(ERROR_BRICK)

    def getButton(self, port):
        if self._fischers:
            try:
                port = int(port)
            except:
                pass
            if (port in FT_SENSOR_PORTS):
                res = ERROR
                try:
                    f = self._fischers[self.active_fischer]
                    res = f.getSensor(port-1)
                except:
                    pass
                return res
            else:
                raise logoerror(ERROR_PORT_S % port)
        else:
            raise logoerror(ERROR_BRICK)

    def refresh(self):
        self.ft_find()
        self.change_color_blocks()
        if self._fischers:
            n = len(self._fischers)
            self.tw.showlabel('print', BRICK_FOUND % int(n))
        else:
            self.tw.showlabel('print', BRICK_NOT_FOUND)

    def select(self, i):
        # The list index begin in 0
        try:
            i = int(i)
            i = i - 1
        except:
            raise logoerror(ERROR_NO_NUMBER % str(i))
        if (i < len(self._fischers)) and (i >= 0):
            self.active_fischer = i
        else:
            raise logoerror(BRICK_INDEX_NOT_FOUND % int(i + 1))

    def count(self):
        return len(self._fischers)

    ############################### Useful functions ##########################

    def change_color_blocks(self):
        index = palette_name_to_index('fischer')
        if (index is not None):
            ft_palette_blocks = palette_blocks[index]
            for block in self.tw.block_list.list:
                if block.type in ['proto', 'block']:
                    if block.name in ft_palette_blocks:
                        if (self._fischers) or (block.name == 'ftrefresh'):
                            special_block_colors[block.name] = COLOR_PRESENT[:]
                        else:
                            special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                        block.refresh()
            self.tw.regenerate_palette(index)

    def _stopActuators(self):
        for f in self._fischers:
            f.turnActuator(1, 0)
            f.turnActuator(2, 0)

    def _close_fischers(self):
        self._stopActuators()
        for f in self._fischers:
            f.quit()
            f.close_ft()
        self._fischers = []
        self.active_fischer = 0

    def ft_find(self):
        self._close_fischers()
        for dev in com_usb.find():
            b = FischerRobot(dev)
            try:
                b.open_ft()
                self._fischers.append(b)
            except:
                pass

