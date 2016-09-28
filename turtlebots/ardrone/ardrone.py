#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Plugin Turtlebots para manejar el ArDrone Parrot.
# El plugin fue desarrollado por Antel.
# Se utilizo el proyecto python-ardrone:
# https://github.com/venthur/python-ardrone
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

import time
import threading
import re
import subprocess
import ardroneAPI

from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import logoerror
from TurtleArt.tautils import debug_output, power_manager_off
from TurtleArt.taconstants import CONSTANTS
from TurtleArt.tawindow import block_names
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_NUMBER

from plugins.plugin import Plugin

from gettext import gettext as _

COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"]

class Ardrone(Plugin):
    
    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        power_manager_off(True)
        
        self.apiArDrone = ardroneAPI.ardroneAPI()
        
    def setup(self):

        paletteardrone = make_palette('ardrone', COLOR_NOTPRESENT, _('ArDrone'), translation=_('ardrone'))

        paletteardrone.add_block('emergenciaDrone',
                    style='basic-style',
                    label=_('emergencia Drone'),
                    prim_name='emergenciaDrone',
                    help_string=_('intercambia estado de emergencia del drone'))
        self.tw.lc.def_prim('emergenciaDrone', 0, Primitive(self.emergenciaDrone))
        special_block_colors['emergenciaDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('calibrarDrone',
                    style='basic-style',
                    label=_('calibrar Drone'),
                    prim_name='calibrarDrone',
                    help_string=_('calibra el drone, tiene que estar en tierra'))
        self.tw.lc.def_prim('calibrarDrone', 0, Primitive(self.calibrarDrone))
        special_block_colors['calibrarDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('despegarDrone',
                    style='basic-style',
                    label=_('despegar Drone'),
                    prim_name='despegarDrone',
                    help_string=_('despega el drone'))
        self.tw.lc.def_prim('despegarDrone', 0, Primitive(self.despegarDrone))
        special_block_colors['despegarDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('aterrizarDrone',
                    style='basic-style',
                    label=_('aterrizar Drone'),
                    prim_name='aterrizarDrone',
                    help_string=_('aterrizar el drone'))
        self.tw.lc.def_prim('aterrizarDrone', 0, Primitive(self.aterrizarDrone))
        special_block_colors['aterrizarDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('flotarDrone',
                    style='basic-style',
                    label=_('flota Drone'),
                    prim_name='flotarDrone',
                    help_string=_('flota el drone'))
        self.tw.lc.def_prim('flotarDrone', 0, Primitive(self.flotarDrone))
        special_block_colors['flotarDrone'] = COLOR_PRESENT[:]
                
        paletteardrone.add_block('izquierdaDrone',
                    style='basic-style',
                    label=_('izquierda Drone'),
                    prim_name='izquierdaDrone',
                    help_string=_('izquierda el drone'))
        self.tw.lc.def_prim('izquierdaDrone', 0, Primitive(self.izquierdaDrone))
        special_block_colors['izquierdaDrone'] = COLOR_PRESENT[:]
                
        paletteardrone.add_block('derechaDrone',
                    style='basic-style',
                    label=_('derecha Drone'),
                    prim_name='derechaDrone',
                    help_string=_('derecha el drone'))
        self.tw.lc.def_prim('derechaDrone', 0, Primitive(self.derechaDrone))
        special_block_colors['derechaDrone'] = COLOR_PRESENT[:]
                
        paletteardrone.add_block('arribaDrone',
                    style='basic-style',
                    label=_('arriba Drone'),
                    prim_name='arribaDrone',
                    help_string=_('arriba el drone'))
        self.tw.lc.def_prim('arribaDrone', 0, Primitive(self.arribaDrone))
        special_block_colors['arribaDrone'] = COLOR_PRESENT[:]
                
        paletteardrone.add_block('abajoDrone',
                    style='basic-style',
                    label=_('abajo Drone'),
                    prim_name='abajoDrone',
                    help_string=_('abajo el drone'))
        self.tw.lc.def_prim('abajoDrone', 0, Primitive(self.abajoDrone))
        special_block_colors['abajoDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('adelanteDrone',
                    style='basic-style',
                    label=_('adelante Drone'),
                    prim_name='adelanteDrone',
                    help_string=_('adelante el drone'))
        self.tw.lc.def_prim('adelanteDrone', 0, Primitive(self.adelanteDrone))
        special_block_colors['adelanteDrone'] = COLOR_PRESENT[:]

        paletteardrone.add_block('atrasDrone',
                    style='basic-style',
                    label=_('atrás Drone'),
                    prim_name='atrasDrone',
                    help_string=_('atras el drone'))
        self.tw.lc.def_prim('atrasDrone', 0, Primitive(self.atrasDrone))
        special_block_colors['atrasDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('girarIzquierdaDrone',
                    style='basic-style',
                    label=_('girarIzquierda Drone'),
                    prim_name='girarIzquierdaDrone',
                    help_string=_('gira a la izquierda el drone'))
        self.tw.lc.def_prim('girarIzquierdaDrone', 0, Primitive(self.girarIzquierdaDrone))
        special_block_colors['girarIzquierdaDrone'] = COLOR_PRESENT[:]
                        
        paletteardrone.add_block('girarDerechaDrone',
                    style='basic-style',
                    label=_('girarDerecha Drone'),
                    prim_name='girarDerechaDrone',
                    help_string=_('gira a la derecha el drone'))
        self.tw.lc.def_prim('girarDerechaDrone', 0, Primitive(self.girarDerechaDrone))
        special_block_colors['girarDerechaDrone'] = COLOR_PRESENT[:]

        paletteardrone.add_block('bateriaDrone', 
                    style='box-style',
                    label=('batería Drone'),
                    prim_name='bateriaDrone',
                    help_string=_('retorna porcentaje de bateria del drone'))
        self.tw.lc.def_prim('bateriaDrone', 0, Primitive(self.bateriaDrone))
        special_block_colors['bateriaDrone'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('anguloTheta', 
                    style='box-style',
                    label=('ángulo Theta'),
                    prim_name='anguloTheta',
                    help_string=_('angulo theta del drone'))
        self.tw.lc.def_prim('anguloTheta', 0, Primitive(self.anguloTheta))
        special_block_colors['anguloTheta'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('anguloPhi', 
                    style='box-style',
                    label=('ángulo Phi'),
                    prim_name='anguloPhi',
                    help_string=_('retorna angulo Phi del drone'))
        self.tw.lc.def_prim('anguloPhi', 0, Primitive(self.anguloPhi))
        special_block_colors['anguloPhi'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('anguloPsi', 
                    style='box-style',
                    label=('ángulo Psi'),
                    prim_name='anguloPsi',
                    help_string=_('retorna angulo Psi del drone'))
        self.tw.lc.def_prim('anguloPsi', 0, Primitive(self.anguloPsi))
        special_block_colors['anguloPsi'] = COLOR_PRESENT[:]
        
        paletteardrone.add_block('alturaDrone', 
                    style='box-style',
                    label=('altura Drone'),
                    prim_name='alturaDrone',
                    help_string=_('altura del drone'))
        self.tw.lc.def_prim('alturaDrone', 0, Primitive(self.alturaDrone))
        special_block_colors['alturaDrone'] = COLOR_PRESENT[:]
        

    ############################### ArDrone calls ##############################
    
    def emergenciaDrone(self):
        self.apiArDrone.emergencia()
        
    def calibrarDrone(self):
        self.apiArDrone.calibrar()
        
    def despegarDrone(self):
        self.apiArDrone.despegar()
        
    def aterrizarDrone(self):
        self.apiArDrone.aterrizar()

    def flotarDrone(self):
        self.apiArDrone.flotar()

    def izquierdaDrone(self):
        self.apiArDrone.izquierda()

    def derechaDrone(self):
        self.apiArDrone.derecha()

    def arribaDrone(self):
        self.apiArDrone.arriba()       
        
    def abajoDrone(self):
        self.apiArDrone.abajo()  
    
    def adelanteDrone(self):
        self.apiArDrone.adelante()  
        
    def atrasDrone(self):
        self.apiArDrone.atras()  

    def girarIzquierdaDrone(self):
        self.apiArDrone.girarIzquierda()  

    def girarDerechaDrone(self):
        self.apiArDrone.girarDerecha()  
        
    def bateriaDrone(self):
        return self.apiArDrone.bateria()
    
    def anguloTheta(self):
        return self.apiArDrone.anguloTheta()

    def anguloPhi(self):
        return self.apiArDrone.anguloPhi()

    def anguloPsi(self):
        return self.apiArDrone.anguloPsi()
    
    def alturaDrone(self):
        return self.apiArDrone.altura()

    ############################### Turtle calls ###############################

    def stop(self):
        self.flotarDrone()
        
    def quit(self):
        self.apiArDrone.apagar()

