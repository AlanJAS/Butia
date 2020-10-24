#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Version 2.0
# This implement API for sumo.uy
#
# Copyright (C) 2008 Guillermo Reisch (greisch@fing.edu.uy)
# Copyright (C) 2010 Andres Aguirre (aaguirre@fing.edu.uy)
#
# This is part of "sumo.uy" python API
# Sumo.uy is a robotics competition by Facultad de Ingenieria
# Universidad de la República del Uruguay
# http://www.fing.edu.uy/sumo.uy
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import socket

#tipos de mensajes
OPE_UPDATE = "update"
OPE_REPOSICIONAR = "position"
OPE_START = "start"
OPE_STOP = "stop"
OPE_ACK = "ok"

#estados del juego
REPOSICIONAR = 0
START = 1
STOP = 2

#default comunication parameters
PORT_CLIENTE = 7001
IP_SERVER = "127.0.0.1"
PORT_SERVER = 8001

class apiSumoUY:
       
    def __init__(self):
        self.cliente = None
        
        #default comunication parameters
        self.port_cliente = PORT_CLIENTE
        self.ip_server = IP_SERVER
        self.port_server = PORT_SERVER

        #estado actual del juego
        self.estado = STOP

        #posicion y puntaje de mi luchador
        self.coorX = -1
        self.coorY = -1
        self.rot = -1
        self.yukoP = 0

        #posicion y puntaje del contrincante
        self.coorXOp = -1
        self.coorYOp = -1
        self.rotOp = -1
        self.yukoPOp = 0

        #posicion en donde debe posicionarse mi luchador
        self.coorXR = -1
        self.coorYR = -1
        self.rotR = -1
    
    def setPuertos(self, port_cliente=PORT_CLIENTE, ip_server=IP_SERVER, port_server=PORT_SERVER):
        
        self.port_cliente = port_cliente
        self.ip_server = ip_server
        self.port_server = port_server
        
        print("SumoAPI: Puertos Seleccionados:")
        print(self.port_cliente)
        print(self.ip_server)
        print(self.port_server)  
    
    def conectarse(self):
        try:
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.cliente.bind((self.ip_server, self.port_cliente)) #puerto por donde voy a mandar mis comandos
            self.cliente.settimeout(1)
        except:
            print("SumoAPI: Error trying to connect...")
        
    def liberarRecursos(self):
        try:
            self.cliente.close() 
        except:
            print("SumoAPI: Closing connection error...")
        
    def enviarAck(self):
        msg = self.OPE_ACK + '*'
        try:
            self.cliente.sendto(msg.encode("ascii"),(self.ip_server, self.port_server))
        except:
            print("SumoAPI: Sending Ack error...")
        
    def enviarVelocidades(self, vel_izq = 0, vel_der = 0):
        msg = "speed*" + str(int(vel_izq)) + "*" + str(int(vel_der)) + "*" 
        try:
            self.cliente.sendto(msg,(self.ip_server, self.port_server))
            return "ok"    
        except:   
            print("SumoAPI: Sending speed error...")
        
    def getInformacion(self):
        try:
            mensaje, addr = self.cliente.recvfrom(1024)
            data = mensaje.split('*')
            opcode = data[0]
            if opcode == OPE_REPOSICIONAR:
                if (len(data) >= 4): 
                    self.coorXR = int(data[1])
                    self.coorYR = int(data[2])
                    self.rotR   = int(data[3])
                    self.estado = REPOSICIONAR
                    self.enviarAck()
            elif opcode == OPE_START:
                self.estado = START
                self.enviarAck()            
            elif opcode == OPE_STOP:
                self.estado = STOP
                self.enviarAck()
            elif opcode == OPE_UPDATE:
                if (len(data) >= 9):
                    self.coorX = int(data[1])
                    self.coorY = int(data[2])
                    self.rot   = int(data[3])
                    self.yukoP = int(data[4])
                    self.coorXOp = int(data[5])
                    self.coorYOp = int(data[6])
                    self.rotOp   = int(data[7])
                    self.yukoPOp = int(data[8])
            mensaje = None
            return 0
        except:
            print("SumoAPI: Getting information error...")
            return -1        
        
    #@return coordenada X de luchador
    def getCoorX(self):
        return self.coorX

    #@return coordenada X de luchador oponente
    def getCoorXOp(self):
        return self.coorXOp  

    #@return coordenada X donde debe posicionarse el luchador
    def getCoorXR(self):
        return self.coorXR
   
    #@return coordenada Y de luchador
    def getCoorY(self):
        return self.coorY
    
    #@return coordenada Y de luchador oponente
    def getCoorYOp(self):
        return self.coorYOp
    
    #@return coordenada Y donde debe posicionarse el luchador
    def getCoorYR(self):
        return self.coorYR

    #@return estado actual del juego
    def getEstado(self):
        return self.estado
      
    #@return rotacion del luchador
    def getRot(self):
        return self.rot

    #@return rotacion del luchador oponente
    def getRotOp(self):
        return self.rotOp
    
    #@return rotacion para reposicionar el luchador
    def getRotR(self):
        return self.rotR
    
    #@return puntos yuko del luchador
    def getYukoP(self):
        return self.yukoP
  
    #@return puntos yuko del luchador oponente
    def getYukoPOp(self):
        return self.yukoPOp     
    
