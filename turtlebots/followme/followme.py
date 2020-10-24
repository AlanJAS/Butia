#!/usr/bin/env python3
#
# Copyright (c) 2011 Alan Aguiar, <alanjas@hotmail.com>
# Copyright (c) 2011 Aylen Ricca, <ar18_90@hotmail.com>
# Copyright (c) 2011 Rodrigo Dearmas, <piegrande46@hotmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import logging
from .color_name import get_color_name
from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_blocks
from TurtleArt.talogo import logoerror
from TurtleArt.tawindow import block_names
from TurtleArt.taconstants import CONSTANTS, MACROS
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg, or_
from TurtleArt.tatype import TYPE_INT, TYPE_STRING, TYPE_NUMBER

pygame = None
try:
    import pygame
    import pygame.camera
except ImportError:
    pygame = None

COLOR_PRESENT = ["#00FF00","#008000"]
COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
_logger = logging.getLogger('turtleart-activity followme plugin')


class Followme(Plugin):

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
                print (('Error stopping camera'))

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

    def get_mask(self):
        try:
            self.capture = self.cam.get_image(self.capture)
            pygame.transform.threshold(self.capture_aux, self.capture, self.colorc, 
                        (self.threshold[0],self.threshold[1], self.threshold[2]), (0,0,0), 2)
            self.mask = pygame.mask.from_threshold(self.capture_aux, self.colorc, self.threshold)
        except:
            print(_('Error in get mask'))

    def luminance(self):
        self.start_camera()
        if self.cam_on:
            self.capture = self.cam.get_image(self.capture)
            # Average the 100 pixels in the center of the screen
            r, g, b = 0, 0, 0
            for y in range(10):
                s = self.y_offset + y
                for x in range(10):
                    color = self.capture.get_at((self.x_offset + x, s))
                    r += color[0]
                    g += color[1]
                    b += color[2]
            return int((r * 0.3 + g * 0.6 + b * 0.1) / 100)
        else:
            return -1

    def setup(self):

        palette = make_palette('followme', COLOR_NOTPRESENT, _('FollowMe'), translation=_('followme'))

        palette.add_block('followmerefresh',
                style='basic-style',
                label=_('refresh FollowMe'),
                prim_name='followmerefresh',
                help_string=_('Search for a connected camera.'))
        self.tw.lc.def_prim('followmerefresh', 0,
            Primitive(self.refresh))
        special_block_colors['followmerefresh'] = COLOR_PRESENT[:]

        palette.add_block('savecalibration',
                style='basic-style-1arg',
                label=_('calibration'),
                prim_name='savecalibration',
                string_or_number=True,
                default='1',
                help_string=_('store a personalized calibration'))
        self.tw.lc.def_prim('savecalibration', 1,
            Primitive(self.savecalibration, arg_descs=or_([ArgSlot(TYPE_NUMBER)], [ArgSlot(TYPE_STRING)])))

        palette.add_block('calibration',
                style='number-style-1strarg',
                label=_('calibration'),
                prim_name='calibration',
                string_or_number=True,
                default='1',
                help_string=_('return a personalized calibration'))
        self.tw.lc.def_prim('calibration', 1,
            Primitive(self.calibration, TYPE_STRING, or_([ArgSlot(TYPE_NUMBER)], [ArgSlot(TYPE_STRING)])))

        palette.add_block('follow',
                style='basic-style-1arg',
                label=_('follow'),
                help_string=_('follow a color or calibration'),
                prim_name='follow')
        self.tw.lc.def_prim('follow', 1,
             Primitive(self.follow, arg_descs=or_([ArgSlot(TYPE_NUMBER)], [ArgSlot(TYPE_STRING)])))

        palette.add_block('brightness_f',
                style='basic-style-1arg',
                label=_('brightness'),
                default=128,
                help_string=_('set the camera brightness as a value between 0 to 255.'),
                prim_name='brightness_f')
        self.tw.lc.def_prim('brightness_f', 1,
            Primitive(self.brightness, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('thresholdFollowMe',
                style='basic-style-3arg',
                hidden=True,
                label=[(_('threshold') + '  ' + 'G'), 'R', 'B'],
                default=[25, 25, 25],
                help_string=_('set a threshold for a RGB color'),
                prim_name='threshold')
        self.tw.lc.def_prim('threshold', 3,
            Primitive(self.set_threshold, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))

        palette.add_block('thresholdMacro',
                          style='basic-style-extended-vertical',
                          label=_('threshold'),
                          help_string=_('set a threshold for a RGB color'))

        global MACROS
        MACROS['thresholdMacro'] = [[0, 'thresholdFollowMe', 0, 0, [None, 1, 2, 3, None]],
                                    [1, ['number', 25], 0, 0, [0, None]],
                                    [2, ['number', 25], 0, 0, [0, None]],
                                    [3, ['number', 25], 0, 0, [0, None]]
                                   ]

        palette.add_block('camera_mode',
                style='basic-style-1arg',
                label=_('camera mode'),
                default='RGB',
                help_string=_('set the color mode of the camera: RGB; YUV or HSV'),
                prim_name='camera_mode')
        self.tw.lc.def_prim('camera_mode', 1,
             Primitive(self.camera_mode, arg_descs=[ArgSlot(TYPE_STRING)]))

        palette.add_block('brightness_w',
                style='box-style',
                label=_('get brightness'),
                help_string=_('get the brightness of the ambient light'),
                prim_name='brightness_w')
        self.tw.lc.def_prim('brightness_w', 0,
             Primitive(self.luminance, TYPE_INT))

        palette.add_block('average_color',
                style='basic-style-1arg',
                label=_('average color'),
                default=1,
                help_string=_('if set to 0 then color averaging is off during calibration; for other values it is on'),
                prim_name='average_color')
        self.tw.lc.def_prim('average_color', 1,
             Primitive(self.average_color, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('xposition',
                style='box-style',
                label=_('x position'),
                help_string=_('return x position'),
                value_block=True,
                prim_name='xposition')
        self.tw.lc.def_prim('xposition', 0,
            Primitive(self.xpos, TYPE_INT))

        palette.add_block('yposition',
                style='box-style',
                label=_('y position'),
                help_string=_('return y position'),
                value_block=True,
                prim_name='yposition')
        self.tw.lc.def_prim('yposition', 0,
             Primitive(self.ypos, TYPE_INT))

        palette.add_block('pixels',
                style='box-style',
                label=_('pixels'),
                help_string=_('return the number of pixels of the biggest blob'),
                value_block=True,
                prim_name='pixels')
        self.tw.lc.def_prim('pixels', 0,
            Primitive(self.getPixels, TYPE_INT))

        global CONSTANTS
        CONSTANTS['RGB'] = _('RGB')
        palette.add_block('mode_rgb',
                style='box-style',
                label=_('RGB'),
                help_string=_('set the color mode of the camera to RGB'),
                value_block=True,
                prim_name='mode_rgb')
        self.tw.lc.def_prim('mode_rgb', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('RGB')]))

        CONSTANTS['YUV'] = _('YUV')
        palette.add_block('mode_yuv',
                style='box-style',
                label=_('YUV'),
                help_string=_('set the color mode of the camera to YUV'),
                value_block=True,
                prim_name='mode_yuv')
        self.tw.lc.def_prim('mode_yuv', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('YUV')]))

        CONSTANTS['HSV'] = _('HSV')
        palette.add_block('mode_hsv',
                style='box-style',
                label=_('HSV'),
                help_string=_('set the color mode of the camera to HSV'),
                value_block=True,
                prim_name='mode_hsv')
        self.tw.lc.def_prim('mode_hsv', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('HSV')]))

        palette.add_block('get_color',
                style='box-style',
                label=_('get color'),
                help_string=_('get the color of an object'),
                value_block=True,
                prim_name='get_color')
        self.tw.lc.def_prim('get_color', 0,
            Primitive(self.get_color, TYPE_STRING))

        palette.add_block('color_dist',
                style='basic-style-1arg',
                label=_('color distance'),
                default=9000,
                help_string=_('set the distance to identify a color'),
                prim_name='color_dist')
        self.tw.lc.def_prim('color_dist', 1,
             Primitive(self.get_color_dist, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('pixels_min',
                style='basic-style-1arg',
                label=_('minimum pixels'),
                default=10,
                help_string=_('set the minimal number of pixels to follow'),
                prim_name='pixels_min')
        self.tw.lc.def_prim('pixels_min', 1,
            Primitive(self.pixels_min, arg_descs=[ArgSlot(TYPE_NUMBER)]))

    ############################### Turtle signals ############################

    def stop(self):
        self.stop_camera()

    def quit(self):
        self.stop_camera()

    ###########################################################################
            
    def refresh(self):
        self.camera_init()
        self.change_color_blocks()

    def camera_mode(self, mode):
        m = 'RGB'
        try:
            m = str(mode)
            m = m.upper()
        except:
            pass
        if (m == 'RGB') or (m == 'YUV') or (m == 'HSV'):
            self.mode = m
            self.get_camera(self.mode)
            if (self.mode == 'RGB'):
                label_0 = _('threshold') + '  ' + 'G'
                label_1 = 'R'
                label_2 = 'B'
            elif (self.mode == 'YUV'):
                label_0 = _('threshold') + '  ' + 'U'
                label_1 = 'Y'
                label_2 = 'V'
            elif (self.mode == 'HSV'):
                label_0 = _('threshold') + '  ' + 'S'
                label_1 = 'H'
                label_2 = 'V'
            for blk in self.tw.block_list.list:
                #NOTE: blocks types: proto, block, trash, deleted
                if blk.type in ['proto', 'block']:
                    if (blk.name == 'thresholdFollowMe'):
                        blk.spr.set_label(label_0, 0)
                        blk.spr.set_label(label_1, 1)
                        blk.spr.set_label(label_2, 2)
                        block_names[blk.name][0] = label_0
                        block_names[blk.name][1] = label_1
                        block_names[blk.name][2] = label_2
                        blk.refresh()

    def change_color_blocks(self):
        index = palette_name_to_index('followme')
        if index is not None:
            followme_blocks = palette_blocks[index]
            for block in self.tw.block_list.list:
                if block.type in ['proto', 'block']:
                    if block.name in followme_blocks:
                        if self.cam_present or (block.name == 'followmerefresh'):
                            special_block_colors[block.name] = COLOR_PRESENT[:]
                        else:
                            special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                        block.refresh()
            self.tw.regenerate_palette(index)
                
    def follow(self, x):
        if type(x) == str:
            self.colorc = self.str_to_tuple(x)
        else:
            self.colorc = (255, 255, 255)

    def brightness(self, x):
        self.brightness = int(x)
        self.set_camera_flags()
            
    def set_threshold(self, R, G, B):
        R = int(R)
        G = int(G)
        B = int(B)
        if (R < 0) or (R > 255):
            R = 25
        if (G < 0) or (G > 255):
            G = 25
        if (B < 0) or (B > 255):
            B = 25
        self.threshold = (R, G, B)
    
    def pixels_min(self, x):
        if type(x) == float:
            x = int(x)
        if x < 0:
            x = 1
        self.pixels_min = x

    def average_color(self, x):
        if x == 0:
            self.use_average = False
        else:
            self.use_average = True

    def get_color(self):
        self.start_camera()
        if self.cam_on:
            self.capture = self.cam.get_image(self.capture)
            color = self.capture.get_at((self.x_m, self.y_m))
            return get_color_name(color, self.color_dist)
        return -1

    def get_color_dist(self, x):
        self.color_dist = x

    def calibrate(self):
        self.colorc = (255, 255, 255)
        self.start_camera()
        x = int((self.tamanioc[0] - 50) / 2.0)
        y = int((self.tamanioc[1] - 50) / 2.0)
        if self.cam_on:
            self.screen = pygame.display.set_mode((1200,900))
            self.clock = pygame.time.Clock()
            self.clock.tick(10)
            self.run = True
            while self.run:
                while gtk.events_pending():
                    gtk.main_iteration()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run = False
                    # click o tecla
                    elif event.type == 3:
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
        return (self.colorc[0], self.colorc[1], self.colorc[2])

    def xpos(self):
        res = -1
        self.start_camera()
        if self.cam_on:
            self.get_mask()
            self.connected = self.mask.connected_component()
            if (self.connected.count() > self.pixels):
                centroid = self.mask.centroid()
                if self.flip:
                    res = centroid[0]
                else:
                    res = self.tamanioc[0] - centroid[0]
        return res

    def ypos(self):
        res = -1
        self.start_camera()
        if self.cam_on:
            self.get_mask()
            self.connected = self.mask.connected_component()
            if (self.connected.count() > self.pixels):
                centroid = self.mask.centroid()
                res = self.tamanioc[1] - centroid[1]
        return res

    def getPixels(self):
        res = -1
        self.start_camera()
        if self.cam_on:
            self.get_mask()
            self.connected = self.mask.connected_component()
            res = self.connected.count()
        return res

    def savecalibration(self, name):
        c = self.calibrate()
        s = str(c[0]) + ', ' + str(c[1]) + ', ' + str(c[2])
        self.calibrations[name] = s
        #self.tw.lc.update_label_value(name, val)

    def calibration(self, name):
        if self.calibrations.has_key(name):
            return self.calibrations[name]
        else:
            raise logoerror(_('empty calibration'))

    def str_to_tuple(self, x):
        try:
            t = x.split(',')
            return (int(t[0]), int(t[1]), int(t[2]))
        except:
            raise logoerror(_('error in string conversion'))

