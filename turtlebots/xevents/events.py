#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
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


from Xlib import X
from Xlib import display
from Xlib import ext
from Xlib.ext import xtest
#Do not remove the following imports as this gives some errores
from Xlib.ext import record
from Xlib.ext import shape
from Xlib.ext import xinerama

from gi.repository import Gtk

import os
import signal
import subprocess
import logging
import webbrowser
import re

from sendkey import SendKey

import time
#import gconf

COLORS = {'red': "#E61B00",
          'orange': "#FF9201",
          'yellow': "#FFE900",
          'green': "#0FEF1E",
          'cyan': "#0EF5EE",
          'blue': "#0000FF",
          'purple': "#C61DCC",
          'white': "#FFFFFF",
          'black': "#000000"}

CALL_DELAY = 200
#ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

class Events:

    def __init__(self, debug=False):

        self._debug = debug

        if self._debug:
            logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')

        self._display = display.Display()


        self._screen = self._display.screen()
        self._x = self._screen.root
        self._window = gtk.Window(gtk.WINDOW_POPUP)
        self._window.set_keep_above(True)
        self._window.set_opacity(1)
        self._window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#234fdb"))
        self._window.set_decorated(False)
        self._window.add_events(gtk.gdk.KEY_PRESS_MASK |
                                gtk.gdk.POINTER_MOTION_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK |
                                gtk.gdk.SCROLL_MASK)

        self._last_call_time = 0
        #Current open programs
        self._pids = {}

        #GConf
        #self._gc = gconf.client_get_default()



    def get_screen_resolution(self):
        """Returns the screen resolution """
        resolution = self._display.screen().root.get_geometry()
        return resolution.width, resolution.height


    def set_line_opacity(self, opacity):
        """Sets the line opacity """
        self._window.set_opacity(opacity)


    def set_line_width_and_height(self, width, height):

        self._window.resize(int(width), int(height))

        if self._debug:
            print("width:%s" % width)
            print(self._window.get_size_request())


    def show_line(self, active):

        if active:
            self._window.show()
        else:
            self._window.hide()


    def set_line_color(self, color_name):

        color = gtk.gdk.color_parse(COLORS[str(color_name)])
        self._window.modify_bg(gtk.STATE_NORMAL, color)

        if self._debug:
            print(color_name.get_number_name())


    '''        
    def set_line_color_rgb(self, red, green, blue):

        # Numbers must be between 0-255
        r, g, b = (min(255, max(0, c)) for c in (red, green, blue))

        red_hex = hex(int(r))[2:].zfill(2)
        green_hex = hex(int(g))[2:].zfill(2)
        blue_hex = hex(int(b))[2:].zfill(2)
        c_hex = "#%s%s%s" % (red_hex, green_hex, blue_hex)

        color = gtk.gdk.color_parse(c_hex)
        self._window.modify_bg(gtk.STATE_NORMAL, color)
    '''


    def create_relative_mouse_event(self, dx, dy):

        # move pointer to set relative location
        self._display.warp_pointer(dx, dy)
        self._display.sync()


    def get_mouse_position(self):

        data = self._display.screen().root.query_pointer()._data
        return data['root_x'], data['root_y']



    def create_absolute_mouse_event(self, x, y, stopped):

        self._x.warp_pointer(x, y)
        if stopped != 1:
            gtk.gdk.flush()
            self._window.move(x, y)
            gtk.gdk.flush()
            self._window.set_keep_above(True)
        self._display.sync()


    def press_button(self, button):
        """Simulates pressing a button
        press button 1, for middle mouse button use 2, for opposite button use 3"""

        ext.xtest.fake_input(self._display, X.ButtonPress, button)
        self._display.sync()


    def release_button(self, button):
        """Simulates releasing a button"""

        ext.xtest.fake_input(self._display, X.ButtonRelease, button)
        self._display.sync()


    def _click(self, button):

        self.press_button(button)
        # to make click we need to release the same button
        self.release_button(button)

        '''self.press_button(button)
        self.release_button(button)'''


    def click_button(self, button):
        """Simulates clicking a button"""

        x, y = self.get_mouse_position()
        self._x.warp_pointer(x, y)
        self._window.set_keep_above(False)
        self._window.set_keep_below(True)

        # press button 1, for middle mouse button use 2, for opposite button use 3
        gtk.gdk.flush()
        self._window.hide()
        gtk.gdk.flush()

        self._click(button)


    def double_click_button(self, button):
        """Simulates double clicking a button"""

        x, y = self.get_mouse_position()
        self._x.warp_pointer(x, y)
        self._window.set_keep_above(False)
        self._window.set_keep_below(True)

        # press button 1, for middle mouse button use 2, for opposite button use 3
        gtk.gdk.flush()
        self._window.hide()
        gtk.gdk.flush()

        self._click(button)
        self._click(button)


    def copy_event(self):

        SendKey.send_special_key("xe_ctrl c")
        if self._debug:
            print("copy event called")


    def paste_event(self):

        SendKey.send_special_key("xe_ctrl v")

        if self._debug:
            print("paste event called")


    def _allow_event(self):
        """Checks if the event is not called too fast"""

        current_time = int(round(time.time()*1000))
        if (current_time - self._last_call_time) > CALL_DELAY:
            self._last_call_time = current_time
            return True
        else:
            return False


    def simulate_key(self, text):

        if self._allow_event():

            #It's a special key
            if (("xe_ctrl" in text) or ("xe_shift" in text) or 
                ("xe_alt" in text) or ("xe_alt_gr" in text)):
                SendKey.send_special_key(text)
            elif ("xe_" in text):
                 SendKey.send_key(text)
            #It's a text
            else:

                splitted_text = list(text)

                for key in splitted_text:
                    SendKey.send_key(key)

            if self._debug:
                print("Simulate Key: " + text)


    def browser(self,url):

        webbrowser.open(url, new=0, autoraise=True)


    def _add_pid(self, program, pid):

        if not self._pids.has_key(program):
            self._pids[program] = []
      
        self._pids[program].append(pid)

        print(pid)


    def _remove_pid(self, program):

        self._pids[program].pop(0)


    def _pid_exists(self, pid):        
        """ Check For the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def _clean_pids(self, program):

        if self._pids.has_key(program):
            for p in self._pids[program]:
                if (not self._pid_exists(p)):
                    self._remove_pid(p)


    def open_program(self, program):

        arguments = ""

        try:
            command = "{0} {1}".format(program, arguments)
            p = subprocess.Popen(command, stderr=subprocess.STDOUT, shell=True,preexec_fn=os.setsid)

            self._add_pid(program,p.pid)

        #except OSError:
        except subprocess.CalledProcessError:

            #Move to binaries folder
            os.chdir("/usr/bin")
            r = subprocess.Popen("find -type f -executable -exec file -i '{}' \;", shell=True, stdout=subprocess.PIPE).stdout.read()
            results = r.split("\n")

            filtered_results = []

            #Filter results
            for f in results:
                filtered_results.append(f.split(":")[0])


            if self._debug:
                print("Retrieving executables list")

            found = False
            i = 0

            while (not found) and (i < len(filtered_results)):
                f = filtered_results[i]
                i += 1

                if self._debug:
                    print("Processing " + f)

                if re.search(program,f):
                    found = True
                    if self._debug:
                        print(f + " found")
            
            if found:
                self._p = subprocess.Popen(f, stderr=subprocess.STDOUT, shell=True,preexec_fn=os.setsid)
                self._add_pid(program,p.pid)
                #os.system("sh {0} {1}".format(file, arguments))
                

    def close_program(self, program):

        if self._pids.has_key(program) and (len(self._pids[program]) > 0):

            self._clean_pids(program)

            try:
                os.killpg(os.getpgid(self._pids[program][0]), signal.SIGTERM)
                self._remove_pid(program)
            except OSError:
                print("Error: The pid does not exists.")

    '''
    def save_value(self, key, val):

        self._gc.set_float(ROOT_DIR + '/conf/' + key, val)


    def get_value(self,key):

        return self._gc.get_float(ROOT_DIR + '/conf/' + key)
    '''
