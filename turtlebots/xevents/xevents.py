#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Andrés Aguirre Dorelo <aaguirre@fing.edu.uy>
# Rafael Carlos Cordano Ottati <rafael.cordano@gmail.com>
# Lucía Carozzi <lucia.carozzi@gmail.com>
# Maria Eugenia Curi <mauge8@gmail.com>
# Leonel Peña <lapo26@gmail.com>
# Andrés Vasilev <andresvasilev@gmail.com>
#
# MINA/INCO/UDELAR
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

import os
import sys
import time
import gconf
import types
import gtk.gdk

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from gettext import gettext as _
from collections import Counter

from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg, or_
from TurtleArt.tatype import TYPE_INT, TYPE_NUMBER, TYPE_COLOR, TYPE_STRING
from events import Events
from TurtleArt.taconstants import CONSTANTS, MACROS
from TurtleArt.tabasics import Palettes


import logging
LOGGER = logging.getLogger('turtleart-activity x11 events plugin')

GCONF_XEVENTS_PATH = '/desktop/sugar/activities/turtlebots/xevents'

class Xevents(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self.init_gconf()
        self._parent = parent
        self.running_sugar = self._parent.running_sugar
        self._status = True
        self.pause = 0
        self._events = Events()
        self._buttons = {} #previous values from buttons {key:[value, lastDebounceTime]}
        self._last_event = 0
        self._program_name = ''
        self._defaults ={} # local default values for conf keys
        self._last_button_state = 0

    def setPause(self):
        self.pause = True

    def unsetPause(self):
        self.pause = False    

    def getPause(self):
        return self.pause
        
    def setup(self):
        # set up X11 events specific blocks
        global CONSTANTS

        CONSTANTS['xe_left_click'] = 1
        CONSTANTS['xe_right_click'] = 3
        CONSTANTS['xe_scroll_up'] = 4
        CONSTANTS['xe_scroll_down'] = 5

        CONSTANTS['TRUE'] = True
        CONSTANTS['FALSE'] = False

        CONSTANTS['xe_buffer_size'] = 30
        CONSTANTS['xe_ctrl'] = "xe_ctrl"
        CONSTANTS['xe_shift'] = "xe_shift"
        CONSTANTS['xe_alt'] = "xe_alt"
        CONSTANTS['xe_alt_gr'] = "xe_alt_gr"
        CONSTANTS['xe_left_arrow'] = "xe_left_arrow"
        CONSTANTS['xe_right_arrow'] = "xe_right_arrow"
        CONSTANTS['xe_up_arrow'] = "xe_up_arrow"
        CONSTANTS['xe_down_arrow'] = "xe_down_arrow"
        CONSTANTS['xe_f4'] = "xe_f4"
        CONSTANTS['xe_f5'] = "xe_f5"
        CONSTANTS['xe_spacebar'] = "xe_spacebar"
        CONSTANTS['xe_tab'] = "xe_tab"
        CONSTANTS['xe_return'] = "xe_return"
        CONSTANTS['xe_escape'] =  "xe_escape"
        CONSTANTS['xe_enter'] =  "xe_enter"


        global MACROS
        '''MACROS['setLineColorRGBmacro'] = [[0, 'setLineColorRGB', 0, 0, [None, 1, 2, 3, None]],
                                          [1, ['number', 0], 0, 0, [0, None]],
                                          [2, ['number', 0], 0, 0, [0, None]],
                                          [3, ['number', 0], 0, 0, [0, None]]
                                         ]
        '''

        MACROS['setLineWidthAndHeightmacro'] = [[0, 'setLineWidthAndHeight', 0, 0, [None, 1, 2, None]],
                                                [1, ['number', 0], 0, 0, [0, None]],
                                                [2, ['number', 0], 0, 0, [0, None]]
                                               ]
        

        palette = make_palette('xlib-bots',
                               colors=["#FF6060", "#A06060"],
                               help_string=_('Palette of X11 event blocks'))
        # Extra palette
        palette2 = make_palette('xlib-bots-extra', 
                                colors=["#FF6060", "#A06060"], 
                                help_string=_('Palette of X11 extra event blocks'))


        palette.add_block('setX11mouse',
                          style='basic-style-2arg',
                          label=_('setXY'),
                          value_block=True,
                          default=[0, 0],
                          help_string=_('set the mouse pointer to x y coordinates'),
                          prim_name='set_x11_mouse')

        self._parent.lc.def_prim(
            'set_x11_mouse', 2,
            Primitive(self.set_x11_mouse, arg_descs=[ArgSlot(TYPE_NUMBER),
                                                     ArgSlot(TYPE_NUMBER)]))

        palette.add_block('getX11mouseX',
                          style='box-style',
                          label=_('getMouseX'),
                          value_block=True,
                          help_string=_('get the mouse pointer x coordinate'),
                          prim_name='get_x11_mouse_x')

        self._parent.lc.def_prim(
            'get_x11_mouse_x', 0,
            Primitive(self.get_x11_mouse_x, TYPE_INT))


        palette.add_block('getX11mouseY',
                          style='box-style',
                          label=_('getMouseY'),
                          value_block=True,
                          help_string=_('get the mouse pointer y coordinate'),
                          prim_name='get_x11_mouse_y')

        self._parent.lc.def_prim(
            'get_x11_mouse_y', 0,
            Primitive(self.get_x11_mouse_y, TYPE_INT))


        palette.add_block('getScreenWidth',
                          style='box-style',
                          label=_('getScreenWidth'),
                          value_block=True,
                          help_string=_('get the screen width'),
                          prim_name='get_screen_width')

        self._parent.lc.def_prim(
            'get_screen_width', 0,
            Primitive(self.get_screen_width, TYPE_INT))


        palette.add_block('getScreenHeight',
                          style='box-style',
                          label=_('getScreenHeight'),
                          value_block=True,
                          help_string=_('get the screen height'),
                          prim_name='get_screen_height')

        self._parent.lc.def_prim(
            'get_screen_height', 0,
            Primitive(self.get_screen_height, TYPE_INT))


        palette.add_block('click',
                          style='basic-style-1arg',
                          label=_('click'),
                          value_block=True,
                          default=[1],
                          help_string=_('simulate a mouse click'),
                          prim_name='click')

        self._parent.lc.def_prim(
            'click', 1,
            Primitive(self.click, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('doubleClick',
                          style='basic-style-1arg',
                          label=_('double click'),
                          value_block=True,
                          default=[1],
                          help_string=_('simulate a mouse double click'),
                          prim_name='double_click')

        self._parent.lc.def_prim(
            'double_click', 1,
            Primitive(self.double_click, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('pressButton',
                          style='basic-style-1arg',
                          label=_('pressButton'),
                          value_block=True,
                          default=[0],
                          help_string=_('keeps button pressed'),
                          prim_name='press_button')

        self._parent.lc.def_prim(
            'press_button', 1,
            Primitive(self.press_button, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('releaseButton',
                          style='basic-style-1arg',
                          label=_('releaseButton'),
                          value_block=True,
                          default=[0],
                          help_string=_('releases button'),
                          prim_name='release_button')

        self._parent.lc.def_prim(
            'release_button', 1,
            Primitive(self.release_button, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('leftClick',
                          style='box-style',
                          label=_('leftClick'),
                          value_block=True,
                          help_string=_('click left click'),
                          prim_name='left_click')

        self._parent.lc.def_prim(
            'left_click', 0,
            Primitive(CONSTANTS.get, TYPE_INT, [ConstantArg('xe_left_click')]))


        palette.add_block('rightClick',
                          style='box-style',
                          label=_('rightClick'),
                          value_block=True,
                          help_string=_('click right click'),
                          prim_name='right_click')

        self._parent.lc.def_prim(
            'right_click', 0,
            Primitive(CONSTANTS.get, TYPE_INT, [ConstantArg('xe_right_click')]))


        palette.add_block('scrollUp',
                          style='box-style',
                          label=_('scrollUp'),
                          value_block=True,
                          help_string=_('simulate mouse scroll up event'),
                          prim_name='scroll_up')

        self._parent.lc.def_prim(
            'scroll_up', 0,
            Primitive(CONSTANTS.get, TYPE_INT, [ConstantArg('xe_scroll_up')]))


        palette.add_block('scrollDown',
                          style='box-style',
                          label=_('scrollDown'),
                          value_block=True,
                          help_string=_('simulate mouse scroll down event'),
                          prim_name='scroll_down')

        self._parent.lc.def_prim(
            'scroll_down', 0,
            Primitive(CONSTANTS.get, TYPE_INT, [ConstantArg('xe_scroll_down')]))


        palette.add_block('freeze',
                          style='basic-style',
                          label=_('freezeBar'),
                          value_block=True,
                          help_string=_('freeze the bar'),
                          prim_name='freeze')

        self._parent.lc.def_prim(
            'freeze', 0,
            Primitive(self.setPause))


        palette.add_block('unfreeze',
                          style='basic-style',
                          label=_('unfreezeBar'),
                          value_block=True,
                          help_string=_('unfreeze the bar'),
                          prim_name='unfreeze')

        self._parent.lc.def_prim(
            'unfreeze', 0,
            Primitive(self.unsetPause))


        palette.add_block('showLine',
                          style='basic-style',
                          label=_('showLine'),
                          value_block=True,
                          help_string=_('show vertical line over mouse'),
                          prim_name='show_line')

        self._parent.lc.def_prim(
            'show_line', 0,
            Primitive(self.show_line))


        palette.add_block('hideLine',
                          style='basic-style',
                          label=_('hideLine'),
                          value_block=True,
                          help_string=_('hide vertical line over mouse'),
                          prim_name='hide_line')

        self._parent.lc.def_prim(
            'hide_line', 0,
            Primitive(self.hide_line))


        '''
        palette.add_block('setLineColorRGB',
                          hidden=True,
                          style='basic-style-3arg',
                          label=_('setLineColorRGB'),
                          value_block=True,
                          default=[0, 0, 0],
                          help_string=_('set line color from rgb value'),
                          prim_name='set_line_color_rgb')

        self._parent.lc.def_prim(
            'set_line_color_rgb', 3,
            Primitive(self.set_line_color_rgb,
                      arg_descs=[ArgSlot(TYPE_INT),
                                 ArgSlot(TYPE_INT),
                                 ArgSlot(TYPE_INT)]))


        palette.add_block('setLineColorRGBmacro',
                          style='basic-style-extended-vertical',
                          label=_('setLineColorRGB'),
                          help_string=_('set line color from rgb value'))

        '''

        palette.add_block('setLineColor',
                          style='basic-style-1arg',
                          label=_('setLineColor'),
                          value_block=True,
                          help_string=_('set line color'),
                          prim_name='set_line_color')

        self._parent.lc.def_prim(
            'set_line_color', 1,
            Primitive(self.set_line_color, arg_descs=[ArgSlot(TYPE_COLOR)]))


        palette.add_block('setLineOpacity',
                          style='basic-style-1arg',
                          label=_('setLineOpacity'),
                          value_block=True,
                          default=[1],
                          help_string=_('set line opacity'),
                          prim_name='set_line_opacity')

        self._parent.lc.def_prim(
            'set_line_opacity', 1,
            Primitive(self.set_line_opacity, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('setLineWidthAndHeight',
                          hidden=True,
                          style='basic-style-2arg',
                          label=_('setLineWidthAndHeight'),
                          value_block=True,
                          default=[0, 0],
                          help_string=_('set width and height of line over mouse'),
                          prim_name='set_line_width_and_height')

        self._parent.lc.def_prim(
            'set_line_width_and_height', 2,
            Primitive(self.set_line_width_and_height,
                      arg_descs=[ArgSlot(TYPE_NUMBER),
                                 ArgSlot(TYPE_NUMBER)]))

        palette.add_block('setLineWidthAndHeightmacro',
                          style='basic-style-extended-vertical',
                          label=_('setLineWidthAndHeight'),
                          help_string=_('set width and height of line over mouse'))


        palette2.add_block('simulateKey',
                          style='basic-style-1arg',
                          label=_('simulateKey'),
                          help_string=_('simulates pressing a key'),
                          prim_name='simulate_key')

        self._parent.lc.def_prim(
            'simulate_key', 1,
            Primitive(self.simulate_key, arg_descs=[ArgSlot(TYPE_STRING)]))


        palette2.add_block('spaceBar',
                          style='box-style',
                          label=_('spaceBar'),
                          value_block=True,
                          help_string=_('space bar'),
                          prim_name='spacebar')

        self._parent.lc.def_prim(
            'spacebar', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_spacebar')]))


        palette2.add_block('leftArrow',
                          style='box-style',
                          label=_('leftArrow'),
                          value_block=True,
                          help_string=_('left arrow'),
                          prim_name='left_arrow')

        self._parent.lc.def_prim(
            'left_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_left_arrow')]))


        palette2.add_block('rightArrow',
                          style='box-style',
                          label=_('rightArrow'),
                          value_block=True,
                          help_string=_('right arrow'),
                          prim_name='right_arrow')

        self._parent.lc.def_prim(
            'right_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_right_arrow')]))


        palette2.add_block('upArrow',
                          style='box-style',
                          label=_('upArrow'),
                          value_block=True,
                          help_string=_('up arrow'),
                          prim_name='up_arrow')

        self._parent.lc.def_prim(
            'up_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_up_arrow')]))


        palette2.add_block('downArrow',
                          style='box-style',
                          label=_('downArrow'),
                          value_block=True,
                          help_string=_('down arrow'),
                          prim_name='down_arrow')

        self._parent.lc.def_prim(
            'down_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_down_arrow')]))


        palette2.add_block('CtrlKey',
                          style='box-style',
                          label=_('ctrlKey'),
                          value_block=True,
                          help_string=_('ctrl key'),
                          prim_name='ctrl_key')

        self._parent.lc.def_prim(
            'ctrl_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_ctrl')]))


        palette2.add_block('ShiftKey',
                          style='box-style',
                          label=_('shiftKey'),
                          value_block=True,
                          help_string=_('shift key'),
                          prim_name='shift_key')

        self._parent.lc.def_prim(
            'shift_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_shift')]))


        palette2.add_block('AltKey',
                          style='box-style',
                          label=_('altKey'),
                          value_block=True,
                          help_string=_('alt key'),
                          prim_name='alt_key')

        self._parent.lc.def_prim(
            'alt_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_alt')]))

        '''
        palette2.add_block('AltGrKey',
                          style='box-style',
                          label=_('altGrKey'),
                          value_block=True,
                          help_string=_('alt gr key'),
                          prim_name='altgr_key')

        
        self._parent.lc.def_prim(
            'altgr_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_alt_gr')]))
        '''

        palette2.add_block('tabKey',
                          style='box-style',
                          label=_('tabKey'),
                          value_block=True,
                          help_string=_('tab key'),
                          prim_name='tab_key')

        

        self._parent.lc.def_prim(
            'tab_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_tab')]))


        palette2.add_block('returnKey',
                          style='box-style',
                          label=_('returnKey'),
                          value_block=True,
                          help_string=_('return key'),
                          prim_name='return_key')

        self._parent.lc.def_prim(
            'return_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_return')]))


        palette2.add_block('escapeKey',
                          style='box-style',
                          label=_('escapeKey'),
                          value_block=True,
                          help_string=_('escape key'),
                          prim_name='escape_key')

        self._parent.lc.def_prim(
            'escape_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_escape')]))


        palette2.add_block('enterKey',
                          style='box-style',
                          label=_('enterKey'),
                          value_block=True,
                          help_string=_('enter key'),
                          prim_name='enter_key')

        self._parent.lc.def_prim(
            'enter_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_enter')]))


        palette2.add_block('f4Key',
                          style='box-style',
                          label=_('f4Key'),
                          value_block=True,
                          help_string=_('f4 key'),
                          prim_name='f4_key')

        self._parent.lc.def_prim(
            'f4_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_f4')]))


        palette2.add_block('f5Key',
                          style='box-style',
                          label=_('f5Key'),
                          value_block=True,
                          help_string=_('f5 key'),
                          prim_name='f5_key')

        self._parent.lc.def_prim(
            'f5_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_f5')]))



        palette2.add_block('combineKeys',
                        style='number-style-block',
                        label=[_('combine'), _('key1'), _('key2') ],
                        help_string=_('Combines two keys. e.g : ctrl + c'),
                        prim_name='combine_keys')
        

        self._parent.lc.def_prim(
          'combine_keys', 2,
          Primitive(self.combine_keys,TYPE_STRING, arg_descs=[ArgSlot(TYPE_STRING),
                                              ArgSlot(TYPE_STRING)]))

        palette2.add_block('debounce',
                        style='number-style-block',
                        label=[_('debounce'), _('name'), _('button') ],
                        default=["name"],
                        help_string=_('Debouncing - The name must be unique'),
                        prim_name='debounce')
        

        self._parent.lc.def_prim(
          'debounce', 2,
          Primitive(self.debounce, arg_descs=[ArgSlot(TYPE_STRING),
                                              ArgSlot(TYPE_NUMBER)]))

        palette2.add_block('edgeDetector',
                        style='number-style-block',
                        label=[_('edge detector'), _('name'), _('button') ],
                        default=["name"],
                        help_string=_('Edge Detector - The name must be unique'),
                        prim_name='edge_detector')
        

        self._parent.lc.def_prim(
          'edge_detector', 2,
          Primitive(self.edge_detector, arg_descs=[ArgSlot(TYPE_STRING),
                                              ArgSlot(TYPE_NUMBER)]))

        palette2.add_block('openBrowser',
                          style='basic-style-1arg',
                          label=_('openBrowser'),
                          default=[_("http://www.example.com")],
                          help_string=_('Simulates opening a web browser'),
                          prim_name='browser')

        self._parent.lc.def_prim(
            'browser', 1,
            Primitive(self.browser, arg_descs=[ArgSlot(TYPE_STRING)]))

        palette2.add_block('openProgram',
                           style='basic-style-1arg',
                           label=_("openProgram"),
                           default=[_("name")],
                           help_string=_('Opens a program'),
                           prim_name='open_program'
                           )

        self._parent.lc.def_prim(
            'open_program', 1,
            Primitive(self.open_program, arg_descs=[ArgSlot(TYPE_STRING)])
        )

        palette2.add_block('closeProgram',
                           style='basic-style-1arg',
                           label=_("closeProgram"),
                           default=[_("name")],
                           help_string=_('close a program'),
                           prim_name='close_program'
                           )

        self._parent.lc.def_prim(
            'close_program', 1,
            Primitive(self.close_program, arg_descs=[ArgSlot(TYPE_STRING)])
        )

        palette2.add_block('minimizeWindow',
                  style='basic-style',
                  label=_('minimizeWindow'),
                  value_block=True,
                  help_string=_('minimize the window'),
                  prim_name='minimize_window')

        self._parent.lc.def_prim(
            'minimize_window', 0,
            Primitive(self.minimize_window))

        palette2.add_block('saveValue',
                    style='basic-style-2arg',
                    label=[_('saveValue'), _('key'), _('value') ],
                    default=["key"],
                    help_string=_('save value - The key must be unique'),
                    prim_name='save_value')
    

        self._parent.lc.def_prim(
          'save_value', 2,
          Primitive(self.save_value, arg_descs=[ArgSlot(TYPE_STRING),
                                              ArgSlot(TYPE_NUMBER)]))


        palette2.add_block('getValue',
                   style='number-style-1arg',
                   label=_("getValue"),
                   default=[_("key")],
                   help_string=_('get a value saved with save value block'),
                   prim_name='get_value'
                   )

        self._parent.lc.def_prim(
            'get_value', 1,
            Primitive(self.get_value, arg_descs=[ArgSlot(TYPE_STRING)])
        )


        palette2.add_block('defaultValue',
                    style='basic-style-2arg',
                    label=[_('defaultValue'), _('key'), _('value') ],
                    default=["key"],
                    help_string=_('default value - The key must be unique'),
                    prim_name='default_value')
    

        self._parent.lc.def_prim(
          'default_value', 2,
          #save a color
          Primitive(self.default_value,
                          arg_descs=or_(
                              [ArgSlot(TYPE_STRING),ArgSlot(TYPE_COLOR)],
                              [ArgSlot(TYPE_STRING),ArgSlot(TYPE_NUMBER)],
                              [ArgSlot(TYPE_STRING),ArgSlot(TYPE_STRING)]) ))
          # or_(Primitive(self.default_value,
          #                 arg_descs=[ArgSlot(TYPE_STRING),
          #                            ArgSlot(TYPE_COLOR)]),
          #       # ... or save a number
          #       Primitive(self.default_value,
          #                 arg_descs=[ArgSlot(TYPE_STRING),
          #                            ArgSlot(TYPE_NUMBER)]),
          #       # ... or save a string
          #       Primitive(self.default_value,
          #                 arg_descs=[ArgSlot(TYPE_STRING),
          #                            ArgSlot(TYPE_STRING)]) ))
        
        palette2.add_block('setProgramName',
                           style='basic-style-1arg',
                           label=_("setProgramName"),
                           default=[_("my program")],
                           help_string=_('name this program'),
                           prim_name='set_program_name'
                           )

        self._parent.lc.def_prim(
            'set_program_name', 1,
            Primitive(self.set_program_name, arg_descs=[ArgSlot(TYPE_STRING)])
        )

        
        palette2.add_block('getColorAt',
                           style='number-style-block',
                           label=_("getColorAt"),
                           default=[0, 0],
                           help_string=_("Get rgb color from specific display position"),
                           prim_name='get_color_at'
                           )
        self._parent.lc.def_prim(
            'get_color_at', 2,
            Primitive(self.get_color_at, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)])
        )
        
    ############################# Turtle calls ################################


    def start(self):
        pass

    def stop(self):
        self._events.show_line(False)

    def quit(self):
        pass


    ################################# Primitives ##############################

    def set_x11_mouse(self, x, y):
        self._events.create_absolute_mouse_event(int(x), int(y), self.getPause())

    def get_x11_mouse_x(self):
        return self._events.get_mouse_position()[0]

    def get_x11_mouse_y(self):
        return self._events.get_mouse_position()[1]

    def get_screen_width(self):
        return self._events.get_screen_resolution()[0]

    def get_screen_height(self):
        return self._events.get_screen_resolution()[1]

    def click(self, button):
        self._events.click_button(button)

    def double_click(self, button):
        self._events.double_click_button(button)

    def press_button(self, button):
        self._events.press_button(button)

    def release_button(self, button):
        self._events.release_button(button)

    def show_line(self):
        self._events.show_line(True)

    def hide_line(self):
        self._events.show_line(False)    

    def set_line_color(self, color_name):
        self._events.set_line_color(color_name)

    def set_line_opacity(self, opacity):
        self._events.set_line_opacity(opacity)

    def set_line_color_rgb(self, red, green, blue):
        self._events.set_line_color_rgb(red, green, blue)

    def set_line_width_and_height(self, width, height):
        self._events.set_line_width_and_height(width, height)

    def simulate_key(self,key):
        self._events.simulate_key(key)
    
    def browser(self, url):
        self._events.browser(url)

    def combine_keys(self, key1, key2):
      return key1 + " " + key2 

    def _listMode(self, l):

        data = Counter(l)
        if len(data) > 0:
            data.most_common() # Returns all unique items and their counts
            return data.most_common(1)[0][0] # Returns the highest occurring item
        else:
            return 0

    def debounce(self, buttonName, buttonState):

      current_time = int(round(time.time()*1000))
      self._last_event = current_time

      #deboucing - recolectar lecturas en cierto tiempo y evaluar la cantidad de 0 y 1's
      #self.buttons -> key:[]
      if not self._buttons.has_key(buttonName):
        self._buttons[buttonName] = []
      
      self._buttons[buttonName].append(buttonState)

      #Keep the buffer at xe_buffer_size
      if len(self._buttons[buttonName]) > CONSTANTS['xe_buffer_size']:
        self._buttons[buttonName].pop(0)

      if self._listMode(self._buttons[buttonName]) == 1:    
        return 1      
      else:
        return 0


    def edge_detector(self, buttonName, buttonState):

      falling_edge = 0;
      rising_edge = 0

      '''
      if not self._buttons.has_key(buttonName):
        self._buttons[buttonName] = []
        self._buttons[buttonName].append(0)

      if (buttonState != self._buttons[buttonName][-1]):
        #falling edge
        if (buttonState == 0):
          falling_edge = 1
        #rising edge  
        else:
          rising_edge = 1  
         
      self._buttons[buttonName].append(buttonState)

      #Keep the buffer at xe_buffer_size
      while len(self._buttons[buttonName]) > CONSTANTS['xe_buffer_size']:
        self._buttons[buttonName].pop(0)

      '''
      if (buttonState != self._last_button_state):
        #falling edge
        if (buttonState == 0):
          falling_edge = 1
        #rising edge  
        else:
          rising_edge = 1  
           
      self._last_button_state = buttonState
      
      #return falling_edge
      return rising_edge


    def open_program(self, program):
        self._events.open_program(program)

    def close_program(self, program):
        self._events.close_program(program)

    def init_gconf(self):
      
      try:
        self.gconf_client = gconf.client_get_default()
      except Exception, err:
        debug_output(_('ERROR: cannot init GCONF client: %s') % err)
        self.gconf_client = None
      

    def get_gconf(self, key):

      casts = {gconf.VALUE_BOOL:   gconf.Value.get_bool,
               gconf.VALUE_INT:    gconf.Value.get_int,
               gconf.VALUE_FLOAT:  gconf.Value.get_float,
               gconf.VALUE_STRING: gconf.Value.get_string}
 
      try:
        #res = float(self.gconf_client.get_string(key))

        val = self.gconf_client.get(key)
        if val == None:
          ret = None
        res = casts[val.type](val)

      except:
        return None

      return res


    def set_gconf(self, key, value):

      casts = {types.BooleanType: gconf.Client.set_bool,
              types.IntType:     gconf.Client.set_int,
              types.FloatType:   gconf.Client.set_float,
              types.StringType:  gconf.Client.set_string}
      
      try:
        casts[type(value)](self.gconf_client, key, value)
        #self.gconf_client.set_float(key, value)
      except:
        pass


    def save_value(self, key, value):

      #if value does not exist, create it
      gconf_key = GCONF_XEVENTS_PATH + "_" + key
      if (hasattr(self,"_program_name")):
        gconf_key = GCONF_XEVENTS_PATH + "_" + self._program_name + "_" + key

      self.set_gconf(gconf_key, value)
      self._defaults[gconf_key] =  value
      self._parent.lc.prim_set_box( key, value)


    def get_value(self, key):

      #if value does not exist, create it
      gconf_key = GCONF_XEVENTS_PATH + "_" + key
      if (hasattr(self,"_program_name")):
        gconf_key = GCONF_XEVENTS_PATH + "_" + self._program_name + "_" + key

      return self._defaults.get(gconf_key,self.get_gconf(gconf_key))


    def default_value(self, key, value):

      #if value does not exist, create it
      gconf_key = GCONF_XEVENTS_PATH + "_" + key

      if (hasattr(self,"_program_name")):
        gconf_key = GCONF_XEVENTS_PATH + "_" + self._program_name + "_" + key
      try:
        running_from_py =(self._parent.parent.__class__.__name__=='DummyTurtleMain')
      except:
        running_from_py = True

      if (running_from_py):
        if (self.get_gconf(gconf_key ) is not None ) :
          # There is already a value, using it instead of default
          value = self.get_gconf(gconf_key)
        else:
          # First run, setting gconf
          self.set_gconf(gconf_key , value)
        
        self._parent.lc.boxes[key] = value
 
      else:
        self._defaults[gconf_key] =  value
        self._parent.lc.prim_set_box( key, value)
        self._parent.lc.update_label_value('box', value, label=key)
        
    
    def set_program_name(self, value):

      #Convert name to lowercase
      value.lower()
      #Remove whitespace characters at start and end
      value.strip()
      #Replace whitespace with underscores
      value.replace(" ", "_")
      self._program_name = value


    def minimize_window(self):

      self._parent.lc.tw.activity.win.iconify()
     
    def get_color_at(self, cx, cy):
      rw = gtk.gdk.get_default_root_window()
      pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
      pixbuf = pixbuf.get_from_drawable(rw, rw.get_colormap(), int(cx), int(cy), 0, 0, 1, 1)
      return '#%02x%02x%02x' % (tuple(pixbuf.pixel_array[0, 0]))
    

