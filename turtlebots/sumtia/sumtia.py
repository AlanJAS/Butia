#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Butiá Team butia@fing.edu.uy 
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

sys.path.insert(0, os.path.abspath('./plugins/sumtia'))

import apiSumoUY
import math

from TurtleArt.tapalette import make_palette
from TurtleArt.taprimitive import Primitive, ArgSlot
from TurtleArt.tatype import TYPE_INT, TYPE_NUMBER

from gettext import gettext as _

from plugins.plugin import Plugin
   
class Sumtia(Plugin):
    
    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        self.vel = 10
        self._inited = False
        self.api = apiSumoUY.apiSumoUY()

    def setup(self):

        palette = make_palette('sumtia', ["#00FF00","#008000"], _('SumBot'), translation=_('sumtia'))

        palette.add_block('updateState',
                style='basic-style',
                label=_('update information'),
                prim_name='updateState',
                help_string=_('update information from the server'))
        self.tw.lc.def_prim('updateState', 0,
            Primitive(self.updateState))

        palette.add_block('sendVelocities',
                style='basic-style-2arg',
                label=_('speed SumBot'),
                prim_name='sendVelocities',
                default=[10,10],
                help_string=_('submit the speed to the SumBot'))
        self.tw.lc.def_prim('sendVelocities', 2,
            Primitive(self.sendVelocities, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))

        palette.add_block('setVel',
                style='basic-style-1arg',
                label=_('speed SumBot'),
                prim_name='setVel',
                default=[10],
                help_string=_('set the default speed for the movement commands'))
        self.tw.lc.def_prim('setVel', 1,
            Primitive(self.setVel, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('forwardSumtia',
                style='basic-style',
                label=_('forward SumBot'),
                prim_name='forwardSumtia',
                help_string=_('move SumBot forward'))
        self.tw.lc.def_prim('forwardSumtia', 0,
            Primitive(self.forward))

        palette.add_block('backwardSumtia',
                style='basic-style',
                label=_('backward SumBot'),
                prim_name='backwardSumtia',
                help_string=_('move SumBot backward'))
        self.tw.lc.def_prim('backwardSumtia', 0,
            Primitive(self.backward))
        
        palette.add_block('stopSumtia',
                style='basic-style',
                label=_('stop SumBot'),
                prim_name='stopSumtia',
                help_string=_('stop the SumBot'))
        self.tw.lc.def_prim('stopSumtia', 0,
            Primitive(self.stop))

        palette.add_block('leftSumtia',
                style='basic-style',
                label=_('left SumBot'),
                prim_name='leftSumtia',
                help_string=_('turn left the SumBot'))
        self.tw.lc.def_prim('leftSumtia', 0,
            Primitive(self.left))

        palette.add_block('rightSumtia',
                style='basic-style',
                label=_('right SumBot'),
                prim_name='rightSumtia',
                help_string=_('turn right the SumBot'))
        self.tw.lc.def_prim('rightSumtia', 0,
            Primitive(self.right))

        palette.add_block('angleToCenter',
                style='box-style',
                label=_('angle to center'),
                prim_name='angleToCenter',
                help_string=_('get the angle to the center of the dohyo'))
        self.tw.lc.def_prim('angleToCenter', 0,
            Primitive(self.angleToCenter, TYPE_INT))

        palette.add_block('angleToOpponent',
                style='box-style',
                label=_('angle to Enemy'),
                prim_name='angleToOpponent',
                help_string=_('get the angle to the Enemy'))
        self.tw.lc.def_prim('angleToOpponent', 0,
            Primitive(self.angleToOpponent, TYPE_INT))
        
        palette.add_block('getX',
                style='box-style',
                label=_('x coor. SumBot'),
                prim_name='getX',
                help_string=_('get the x coordinate of the SumBot'))
        self.tw.lc.def_prim('getX', 0,
            Primitive(self.getX, TYPE_INT))
        
        palette.add_block('getY',
                style='box-style',
                label=_('y coor. SumBot'),
                prim_name='getY',
                help_string=_('get the y coordinate of the SumBot'))
        self.tw.lc.def_prim('getY', 0,
            Primitive(self.getY, TYPE_INT))
        
        palette.add_block('getOpX',
                style='box-style',
                label=_('x coor. Enemy'),
                prim_name='getOpX',
                help_string=_('get the x coordinate of the Enemy'))
        self.tw.lc.def_prim('getOpX', 0,
            Primitive(self.getOpX, TYPE_INT))
        
        palette.add_block('getOpY',
                style='box-style',
                label=_('y coor. Enemy'),
                prim_name='getOpY',
                help_string=_('get the y coordinate of the Enemy'))
        self.tw.lc.def_prim('getOpY', 0,
            Primitive(self.getOpY, TYPE_INT))
        
        palette.add_block('getRot',
                style='box-style',
                label=_('rotation SumBot'),
                prim_name='getRot',
                help_string=_('get the rotation of the Sumbot'))
        self.tw.lc.def_prim('getRot', 0,
            Primitive(self.getRot, TYPE_INT))
        
        palette.add_block('getOpRot',
                style='box-style',
                label=_('rotation Enemy'),
                prim_name='getOpRot',
                help_string=_('get the rotation of the Enemy'))
        self.tw.lc.def_prim('getOpRot', 0,
            Primitive(self.getOpRot, TYPE_INT))
        
        palette.add_block('getDistCenter',
                style='box-style',
                label=_('distance to center'),
                prim_name='getDistCenter',
                help_string=_('get the distance to the center of the dohyo'))
        self.tw.lc.def_prim('getDistCenter', 0,
            Primitive(self.getDistCenter, TYPE_INT))
        
        palette.add_block('getDistOp',
                style='box-style',
                label=_('distance to Enemy'),
                prim_name='getDistOp',
                help_string=_('get the distance to the Enemy'))
        self.tw.lc.def_prim('getDistOp', 0,
            Primitive(self.getDistOp, TYPE_INT))

    ############################### Turtle signals ############################

    def stop(self):
        if self._inited:
            self.api.enviarVelocidades(0,0)

    def quit(self):
        if self._inited:
            self.api.liberarRecursos()

    ###########################################################################

    # Sumtia helper functions for apiSumoUY.py interaction

    def sendVelocities(self,vel_izq = 0, vel_der = 0):
        self.api.enviarVelocidades(vel_izq, vel_der)
        
    def setVel(self,vel = 0):
        self.vel = int(vel)

    def forward(self):
        self.api.enviarVelocidades(self.vel, self.vel)

    def backward(self):
        self.api.enviarVelocidades(-self.vel, -self.vel)

    def left(self):
        self.api.enviarVelocidades(-self.vel, self.vel)

    def right(self):
        self.api.enviarVelocidades(self.vel, -self.vel)
        
    def getX(self):
        return self.api.getCoorX()
    
    def getY(self):
        return self.api.getCoorY()
    
    def getOpX(self):
        return self.api.getCoorXOp()
    
    def getOpY(self):
        return self.api.getCoorYOp()
    
    def getRot(self):
        return self.api.getRot()
    
    def getOpRot(self):
        return self.api.getRotOp()

    def angleToCenter(self):
        rot = math.degrees(math.atan2(self.api.getCoorY(), self.api.getCoorX())) + (180 - self.getRot())
        return (rot - 360) if abs(rot) > 180 else rot 

    def angleToOpponent(self):
        x = self.getX() - self.getOpX()
        y = self.getY() - self.getOpY()
        rot = math.degrees(math.atan2(y, x)) + (180 - self.getRot())
        return (rot - 360) if abs(rot) > 180 else rot 
    
    def getDistCenter(self):
        return math.sqrt(math.pow(self.getX(), 2) + math.pow(self.getY(), 2))
    
    def getDistOp(self):
        return math.sqrt(math.pow(self.getX() - self.getOpX(), 2) +
                        math.pow(self.getY() - self.getOpY(), 2))
    
    def updateState(self):
        if not(self._inited):
            self.api.setPuertos()
            self.api.conectarse()
            self._inited = True
        self.api.getInformacion()

