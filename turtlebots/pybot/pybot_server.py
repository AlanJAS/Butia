#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# Pybot server
#
# Copyright (c) 2012-2020 Alan Aguiar alanjas@hotmail.com
# Copyright (c) 2012-2020 Butiá Team butia@fing.edu.uy
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
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

import sys
import select
import socket
import usb4butia
import com_chotox

PYBOT_PORT = 2009
BUFSIZ = 1024
MAX_CLIENTS = 4

class Server():

    def __init__(self, debug=False, chotox=False):
        self.debug = debug
        self.run = True
        self.clients = {}
        # Socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", PYBOT_PORT))
        self.socket.listen(MAX_CLIENTS)
        # Modo robot
        self.chotox_mode = chotox
        if self.chotox_mode:
            self.robot = com_chotox.Chotox(debug=self.debug)
        else:
            self.robot = usb4butia.USB4Butia(debug=self.debug)

    def init_server(self):

        inputs = [self.socket]

        while self.run:
            try:
                inputready,outputready,exceptready = select.select(inputs, [], [], 5.0)
            except Exception as err:
                print('Error en select:', err)
                break

            for s in inputready:
                if s is self.socket:
                    self._accept_client(inputs)
                else:
                    self._handle_client(s, inputs)

        self._shutdown()

    def _accept_client(self, inputs):
        client, addr = self.socket.accept()
        print('New client:', addr)
        inputs.append(client)
        self.clients[client] = addr

    def _handle_client(self, s, inputs):
        try:
            data = s.recv(BUFSIZ)
            if data:
                request = data.decode().strip()
                response = self._process_command(request)
                s.sendall((response + '\n').encode())
            else:
                self._disconnect_client(s, inputs)
        except Exception as err:
            print('Error con cliente:', err)
            self._disconnect_client(s, inputs)

    def _process_command(self, request):
        parts = request.split()
        command = 'cmd_' + parts[0].upper()
        args = parts[1:]

        handler = getattr(self, command)

        if not handler:
            return f"Unknown command '{command}'"
        try:
            return str(handler(args))
        except Exception as err:
            print('Error con cliente:', err)

    def _disconnect_client(self, s, inputs):
        print('Cliente desconnected:', self.clients.get(s))
        inputs.remove(s)
        self.clients.pop(s, None)
        s.close()

    def _shutdown(self):
        print('Closing server')
        self.socket.close()
        self.robot.close()

    #### COMMANDS ###

    def cmd_QUIT(self, args):
        """Close PyBot server"""
        self.run = False
        return 'BYE'

    def cmd_REFRESH(self, args):
        """Search for new devices"""
        self.robot.refresh()
        return ''

    def cmd_OPEN(self, args):
        """Open an 'openable' module such as motors, butia.."""
        if len(args) == 1:
            module = args[0]
            return self.robot.moduleOpen(module)
        return ''

    def cmd_CLOSE(self, args):
        """Close an 'openable' module such as motors, butia.."""
        if len(args) == 1:
            module = args[0]
            return self.robot.moduleClose(module)
        return ''

    def cmd_DESCRIBE(self, args):
        """Get the list of functions and parameters of a module"""
        if len(args) == 1:
            module = args[0]
            return self.robot.describe(module)
        return ''

    def cmd_BUTIA_COUNT(self, args):
        """Get the number of boards connected"""
        return self.robot.getButiaCount()

    def cmd_LISTI(self, args):
        """Get a list of instanciables modules of the board"""
        board = 0
        if len(args) >= 1:
            board = args[0]
        l = self.robot.getListi(board)
        return ','.join(l)

    def cmd_LIST(self, args):
        """Get a list of open modules in a board"""
        l = self.robot.getModulesList()
        return ','.join(l)

    def cmd_CLIENTS(self, args):
        """Get a list of current clients in PyBot server"""
        l = []
        for c in self.clients:
            addr = self.clients[c]
            l.append(str(addr[0]) + ', ' + str(addr[1]))
        return '\n'.join(l)

    def cmd_CALL(self, args):
        """Call a function of certain module"""
        if len(args) >= 2:
            split = self.robot._split_module(args[0])
            return self.robot.callModule(split[1], split[2], split[0], args[1], args[2:])
        return ''

    def cmd_HELP(self, args):
        """Return a list of commands or the use of specific one"""
        a = dir(self)
        l = []
        for e in a:
            if e.startswith('cmd_'):
                l.append(e[4:])
        if len(args) == 0:
            return ', '.join(l)
        else:
            com = args[0].upper()
            if com in l:
                f = getattr(self, 'cmd_' + com)
                return f.__doc__
            return ""

    def cmd_VERSION(self, args):
        """Return the current version of PyBot library"""
        return self.robot._get_pybot_version()


def show_help():
    print("Open PyBot server in PORT 2009")
    print("")
    print("Usage:")
    print(" pybot_server.py [OPTIONS]")
    print("")
    print("Opciones:")
    print(" -h, --help                 muestra esta ayuda")
    print(" chotox                     simulador de robot")
    print(" DEBUG                      habilita los mensajes de depuración")
    print("")

if __name__ == "__main__":
    argv = sys.argv[:]
    if ("-h" in argv) or ("--help" in argv):
        show_help()
    else:
        chotox = 'chotox' in argv
        debug = 'DEBUG' in argv
        s = Server(debug, chotox)
        s.init_server()

