#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton

from ButiaFirmware import Flash

class ButiaFirmware(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.max_participants = 1
        self.build_toolbar()
        self.flash = Flash(self)
        self.set_canvas(self.flash.build_canvas())
        self.show_all()

    def can_close(self):
        return not self.flash._flashing

    def build_toolbar(self):
        toolbox = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(activity_button, -1)
        activity_button.show()
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbox.toolbar.insert(separator, -1)
        separator.show()
        stop_button = StopButton(self)
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()
        self.set_toolbar_box(toolbox)
        toolbox.show()
