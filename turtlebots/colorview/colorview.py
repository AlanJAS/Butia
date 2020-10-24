#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import gtk
import logging
import numpy

from math import sqrt 
from math import fabs
from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_blocks
from TurtleArt.talogo import logoerror
from TurtleArt.tawindow import block_names
from TurtleArt.taconstants import CONSTANTS, Color
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg, or_
from TurtleArt.tatype import TYPE_INT, TYPE_STRING, TYPE_NUMBER, TYPE_BOOL, TYPE_COLOR

pygame = None
try:
    import pygame
    import pygame.camera
except ImportError:
    pygame = None

COLOR_PRESENT = ["#00FF00","#008000"]
COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
_logger = logging.getLogger('turtleart-activity colorview plugin')

d = {
'black'  : (0, 0, 0),
'white'  : (255, 255, 255),
'red'    : (255,0,0),
'orange' : (255,165,0),
'lime'   : (0,255,0),
'blue'   : (0,0,255),
'yellow' : (255,255,0),
'cyan'   : (0,255,255),
'magenta': (255,0,255),
'silver' : (192,192,192),
'gray'   : (128,128,128),
'maroon' : (128,0,0),
'olive'  : (128,128,0),
'green'  : (0,128,0),
'purple' : (128,0,128),
'teal'   : (0,128,128),
'navy'   : (0,0,128)
}


class Colorview(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        self.cam_on = False
        self.cam_present = False
        self.cam_init = False
        self.tamanioc = (320, 240)
        self.colorc = (255, 255, 255)
        self.threshold = (25, 25, 25)
        self.pixels_min = 10
        self.pixels = 0
        self.brightness = 128
        self.color_dist = 9000
        self.tolerance = 800
        self.use_average = True
        self.calibrations = {}
        self.mode = 'RGB'
        self.cam = None
        self.mask = None
        self.connected = None
        self.capture = None
        self.lcamaras = []
        
    def camera_init(self):
        if pygame is not None:
            pygame.camera.init()
            self.get_camera(self.mode)

    def get_camera(self, mode):
        self.stop_camera()
        self.cam_present = False
        self.lcamaras = pygame.camera.list_cameras()
        if self.lcamaras:
            self.cam = pygame.camera.Camera(self.lcamaras[0], self.tamanioc, mode)
            try:
                self.cam.start()
                self.set_camera_flags()
                self.cam.stop()
                self.capture = pygame.surface.Surface(self.tamanioc)
                self.capture_aux = pygame.surface.Surface(self.tamanioc)
                self.cam_present = True
                self.cam_init = True
            except:
                print(_('Error on initialization of the camera'))
        else:
            print(_('No camera was found'))

    def set_camera_flags(self):
        if self.cam_present:
            if (self.brightness == -1):
                self.cam.set_controls(True, False)
            else:
                self.cam.set_controls(True, False, self.brightness)
            res = self.cam.get_controls()
            self.flip = res[0]
            self.tamanioc = self.cam.get_size()
            self.x_offset = int(self.tamanioc[0] / 2.0 - 5)
            self.y_offset = int(self.tamanioc[1] / 2.0 - 5)
            self.x_m = int(self.tamanioc[0] / 2.0)
            self.y_m = int(self.tamanioc[1] / 2.0)

    def stop_camera(self):
        if (self.cam_present and self.cam_on):
            try:
                self.cam.stop()
                self.cam_on = False
            except:
                print(_('Error stopping camera'))

    def start_camera(self):
        if not(self.cam_init and self.cam_present):
            self.camera_init()
            self.change_color_blocks()
        if (self.cam_present and not(self.cam_on)):
            try:
                self.cam.start()
                self.set_camera_flags()
                self.cam_on = True
            except:
                print(_('Error starting camera'))

    def setup(self):

        palette = make_palette('colorview', COLOR_NOTPRESENT, _('colorview'), translation=_('color detector'))

        palette.add_block('color_compare',
                style='boolean-1arg-block-style',
                label=_('color compare'),
                prim_name='color_compare',
                help_string=_('compares a color with the palette'))
        self.tw.lc.def_prim('color_compare', 1, 
            Primitive(self.color_compare, TYPE_BOOL, arg_descs=[ArgSlot(TYPE_COLOR)]))

        palette.add_block('set_tolerance',
                style='basic-style-1arg',
                label=_('set tolerance'),
                default='8',
                prim_name='set_tolerance',
                help_string=_('sets the tolerance between colors'))
        self.tw.lc.def_prim('set_tolerance', 1,
             Primitive(self.set_tolerance, arg_descs=[ArgSlot(TYPE_STRING)]))

        palette.add_block('set_brightness',
                style='basic-style-1arg',
                label=_('set brightness'),
                default='128',
                prim_name='set_brightness',
                help_string=_('sets the brightness of the camera'))
        self.tw.lc.def_prim('set_brightness', 1,
             Primitive(self.set_brightness, arg_descs=[ArgSlot(TYPE_STRING)]))

        palette.add_block('view_camera',
                style='basic-style',
                label=_('view camera'), 
                prim_name='view_camera',
                help_string=_('shows the camera'))
        self.tw.lc.def_prim('view_camera', 0, Primitive(self.view_camera))
    
        #special_block_colors['comparar_color'] = COLOR_PRESENT[:]

    ############################### Turtle signals ############################

    def stop(self):
        self.stop_camera()

    def quit(self):
        self.stop_camera()

    ###########################################################################
            
    def refresh(self):
        self.camera_init()
        self.change_color_blocks()

    def change_color_blocks(self):
        index = palette_name_to_index('colorview')
        if index is not None:
            colorview_blocks = palette_blocks[index]
            for block in self.tw.block_list.list:
                if block.type in ['proto', 'block']:
                    if block.name in colorview_blocks:
                        if self.cam_present:
                            special_block_colors[block.name] = COLOR_PRESENT[:]
                        else:
                            special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                        block.refresh()
            self.tw.regenerate_palette(index)

    def ColorDistance(self,rgb1,rgb2):
        rm = 0.5*(rgb1[0]+rgb2[0])

        ex1 = numpy.array((2+rm,4,3-rm))
        ext2 = pow((rgb1-rgb2),2)

        distance = sqrt(fabs(sum(ex1*ext2)))
        return distance

    def color_compare(self,color):
        x = int((self.tamanioc[0] - 50) / 2.0)
        y = int((self.tamanioc[1] - 50) / 2.0)

        if not(self.cam_on):
            self.start_camera()

        if self.cam_on:
            self.capture = self.cam.get_image(self.capture)
            rect = pygame.Rect(x,y,50,50)
            self.colorc = pygame.transform.average_color(self.capture, rect)
            rgb1 = numpy.array((self.colorc[0],self.colorc[1],self.colorc[2]))            
            rgb2 = numpy.array(d[color.name])
            distancia = self.ColorDistance(rgb1,rgb2)
        
            #print 'RGB1 (Color que estoy viendo) = ' + str(rgb1)
            #print 'RGB2 (Color que quiero ver) = ' + str(rgb2)
            #print 'DISTANCIA = ' + str(distancia) + ' ||  TOLERANCIA = ' + str(self.tolerance)
            #self.stop_camera()

            if (distancia < self.tolerance):
                return True
            else:
                return False

    def get_color(self):

        if not(self.cam_on):
            self.start_camera()

        x = int((self.tamanioc[0] - 50) / 2.0)
        y = int((self.tamanioc[1] - 50) / 2.0)
        if self.cam_on:
            self.capture = self.cam.get_image(self.capture)
            rect = pygame.Rect(x,y,50,50)
            color = pygame.transform.average_color(self.capture, rect)
            return str(color[0]) + ','+ str(color[1]) + ','+ str(color[2])
        return -1

    def set_tolerance(self,valor):
        self.tolerance = (int(valor) * 100)

    def set_brightness(self,valor):
        self.brightness = int(valor)

    def view_camera(self):
        self.colorc = (255, 255, 255)
        if not(self.cam_on):
            self.start_camera()
        x = int((self.tamanioc[0] - 50) / 2.0)
        y = int((self.tamanioc[1] - 50) / 2.0)
        if self.cam_on:
            self.screen = pygame.display.set_mode((1200,900))
            self.run = True
            while self.run:
                while gtk.events_pending():
                    gtk.main_iteration()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run = False
                self.capture = self.cam.get_image(self.capture)
                if not(self.flip):
                    self.capture = pygame.transform.flip(self.capture, True, False)
                self.screen.blit(self.capture, (0,0))
                rect = pygame.draw.rect(self.screen, (255,0,0), (x,y,50,50), 4)
                if self.use_average:
                    self.colorc = pygame.transform.average_color(self.capture, rect)
                else:
                    self.colorc = self.capture.get_at((self.x_m, self.y_m))
                self.screen.fill(self.colorc, (self.tamanioc[0],self.tamanioc[1],100,100))
                pygame.display.flip()
            self.screen = pygame.display.quit()
        self.stop_camera()

