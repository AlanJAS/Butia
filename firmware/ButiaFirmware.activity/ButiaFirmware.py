#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import platform
import subprocess
import time
import configparser
import gettext
from gettext import gettext as _

from pybot import usb4butia


class Flash():

    def __init__(self, parent=None):
        self.parent = parent
        self._base_path = os.path.dirname(os.path.abspath(__file__))
        self._flashing = False
        self._buttons = []
        self._version = None
        self.firmware_hex = None
        self.get_translations()
        self.get_hex()

    def get_translations(self):
        file_activity_info = configparser.ConfigParser()
        activity_info_path = os.path.join(self._base_path, 'activity', 'activity.info')
        file_activity_info.read(activity_info_path, encoding='utf-8')
        bundle_id = file_activity_info.get('Activity', 'bundle_id')
        self.activity_name = file_activity_info.get('Activity', 'name')
        path = os.path.join(self._base_path, 'locale')
        gettext.bindtextdomain(bundle_id, path)
        gettext.textdomain(bundle_id)
        global _
        _ = gettext.gettext

    def get_hex(self):
        self.firmware_hex = None
        self._version = None
        for f in sorted(os.listdir(self._base_path)):
            path = os.path.join(self._base_path, f)
            if f.lower().endswith('.hex') and os.path.isfile(path):
                self.firmware_hex = path
        if self.firmware_hex is None:
            print(_('Firmware hex not found'))
            #self._no_firmware_message()
            return
        print(_('Current firmware hex: %s') % self.firmware_hex)
        stem = os.path.splitext(os.path.basename(self.firmware_hex))[0]
        try:
            self._version = int(stem.rsplit('-', 1)[1])
        except (IndexError, ValueError):
            return
        print(_('Current firmware version: %s') % self._version)

    def build_window(self):
        win = Gtk.Window()
        self.parent = win
        win.set_title(_('Butia Firmware Upgrader'))
        win.connect('delete_event', self._quit)
        canvas = self.build_canvas()
        win.add(canvas)
        win.show_all()
        Gtk.main()

    def _quit(self, win, e):
        if self._flashing:
            return True
        Gtk.main_quit()
        return False

    def _message_dialog(self, message_type, buttons, text):
        return Gtk.MessageDialog(
            transient_for=self.parent,
            modal=True,
            destroy_with_parent=True,
            message_type=message_type,
            buttons=buttons,
            text=text)
        
    def build_canvas(self):

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        img = Gtk.Image()
        img.set_from_file(os.path.join(self._base_path, 'activity', 'fua-icon.svg'))
        img.show()
        box.add(img)

        boxH = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        button_check = Gtk.Button(label=_("Check version"))
        button_check.connect("clicked", self.check_message)
        button_check.show()
        boxH.add(button_check)

        button_accept = Gtk.Button(label=_("Burn Firmware"))
        button_accept.connect("clicked", self.warning_message)
        self._buttons = [button_check, button_accept]
        button_accept.show()
        boxH.add(button_accept)

        boxH.show()
        box.add(boxH)
        box.show()
        return box

    def warning_message(self, widget=None):
        if self._flashing:
            return
        if self.firmware_hex is None:
            self._no_firmware_message()
            return
        version = self._version if self._version is not None else os.path.basename(self.firmware_hex)
        msg = _('You will upgrade to the USB4Butia v%s firmware.\n') % version
        msg = msg + _('Not disconnect the board and not close this activity.\n')
        msg = msg + _('You want to continue?')
        dialog = self._message_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, msg)
        dialog.set_title(_('Burning USB4Butia board...'))
        res = dialog.run()
        dialog.destroy()
        if res == Gtk.ResponseType.OK:
            self.flash()

    def check_message(self, widget=None):
        if self._flashing:
            return
        ver = self.get_version()
        if ver == -1:
            msg = _('Error reading Firmware version.\nTry again or test USB connection...')
            dialog = self._message_dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
        else:
            msg = _('The current version of the Firmware\nis %s') % ver
            dialog = self._message_dialog(Gtk.MessageType.INFO, Gtk.ButtonsType.OK, msg)
        dialog.set_title(_('USB4Butia firmware version...'))
        dialog.run()
        dialog.destroy()

    def flash(self):
        if self._flashing:
            return
        if self.firmware_hex is None or not os.path.isfile(self.firmware_hex):
            self._no_firmware_message()
            return

        started = time.monotonic()
        architecture = platform.machine()
        if architecture == 'x86_64':
            directory = 'x64'
        elif architecture.startswith('arm'):
            directory = 'arm'
        else:
            directory = 'x32'
        path = os.path.join(self._base_path, 'fsusb', directory, 'fsusb')

        self._flashing = True
        for button in self._buttons:
            button.set_sensitive(False)
        dialog = None
        try:
            dialog = self.initing()
            result = None
            for option in ('--force_program', '--program'):
                print('Trying %s option' % option)
                proc = subprocess.Popen([path, option, self.firmware_hex])
                self.wait_proc(proc)
                result = proc.returncode
                if result == 0:
                    break
        except OSError as err:
            result = err
        finally:
            if dialog is not None:
                dialog.destroy()
            self._flashing = False
            for button in self._buttons:
                button.set_sensitive(True)

        if result == 0:
            self.sucess(int(time.monotonic() - started))
        else:
            self.unsucess(result)

    def initing(self):
        msg = _('Burning USB4Butia board...')
        dialog = self._message_dialog(Gtk.MessageType.INFO, Gtk.ButtonsType.NONE, msg)
        dialog.set_title(_('Burning...'))
        self.pbar = Gtk.ProgressBar()
        content = dialog.get_content_area() 
        content.add(self.pbar)
        self.pbar.show()
        # Run es bloqueante
        #dialog.run()
        dialog.set_deletable(False)
        dialog.show_all()
        return dialog

    def progress_timeout(self):
        self.pbar.pulse()

    def wait_proc(self, proc):
        self.pbar.set_fraction(0.0)
        while proc.poll() is None:
            time.sleep(0.1)
            self.progress_timeout()
            while Gtk.events_pending():
                Gtk.main_iteration()
        self.pbar.set_fraction(1.0)

    def sucess(self, seconds):
        msg = _('The upgrade ends successfully!\nThe process takes %s seconds') % seconds
        dialog = self._message_dialog(Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, msg)
        dialog.set_title(_('Burning USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def unsucess(self, err):
        msg = _('The upgrade fails. Try again.\nError: %s') % err
        dialog = self._message_dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, msg)
        dialog.set_title(_('Burning USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def get_version(self):
        board = None
        try:
            board = usb4butia.USB4Butia(get_modules=False)
            return board.getFirmwareVersion()
        except Exception as err:
            print('Error reading firmware version:', err)
            return -1
        finally:
            if board is not None:
                board.close()

    def _no_firmware_message(self):
        msg = _('Firmware hex not found')
        dialog = self._message_dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    f = Flash()
    f.build_window()
