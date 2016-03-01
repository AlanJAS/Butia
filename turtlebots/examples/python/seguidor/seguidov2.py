#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutinas para seguidor de lineas junto con el plugin de marcas
al correr levanta dos hilos uno para el manejo del butia (ClaseMain) y otra para el teclado (ClaseTecla)
- para salir presionar c + enter
- para ver los valores de los sensores de grises, G +enter, luego 1 para ver el derecho o
2 para el izquierdo, para salir S+enter, para ver el otro poner nuevamente G y el numero correspondiente.
- Para que comienze a hacer caminar el Robot m + enter, se sale con S y enter


"""

import sys
import os.path

if os.path.exists('/home/olpc/Activities/TurtleBots.activity'):
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/butia")

if os.path.exists("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection/library"):
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection")

from pybot import usb4butia
from library import patternsAPI
import threading
import time

class ClaseData:

    def __init__(self):
        self.lock = threading.Lock()
        self.codigo = ""

    def set_codigo(self, cod):
        self.lock.acquire()
        self.codigo = cod
        self.lock.release()

    def get_codigo(self):
        self.lock.acquire()
        cod = self.codigo
        self.lock.release()
        return cod


class ClaseMain(threading.Thread):

    def __init__(self, data):
        print "Inicio ClaseMain"
        threading.Thread.__init__(self)
        self.detect = patternsAPI.detection()
        self.detect.init()
        self.data = data
        #self.butia = pybot_client.robot()
        self.butia = usb4butia.USB4Butia()
        self.idIzq = "4"
        self.idDer = "2"
        self.negroDer = 40000
        self.negroIzq = 30000
        self.distMinimalSignal = 500
        print str(self.detect.arMultiGetIdsMarker().split(";"))
        #print str(self.butia.getModulesList())
        #self.detect.isMarkerPresent("Right")


    def run(self):
        salir = False
        while not salir:
            cod = self.data.get_codigo()
            #print "main" + cod
            if cod== "C":
                salir = True
            elif cod == "M":
                print "motor"
                self.mover()
            elif cod == "V":
                print "Vision"
                self.ver_distancias()
            elif cod == "G":
                print "grises"
                salirG = False
                while not salirG:
                    cod = self.data.get_codigo()
                    if cod =="S":
                        salirG = True
                    elif cod == "C":
                        salirG = True
                        salir = True
                    elif cod == "1":
                        print "sensor der: " + self.idDer + " valor " + str(self.butia.getGray(self.idDer))
                    elif cod == "2":
                        print "sensor izq: " + self.idIzq + " valor " + str(self.butia.getGray(self.idIzq ))
        self.detect.cleanup()
        print "FIN ClaseMain"

    def mover(self):
        salirM = False
        while not salirM:
            cod = self.data.get_codigo()
            if cod == "S":
                print "salir motor"
                salirM = True
                self.butia.set2MotorSpeed("0","0","0","0")
            else:
                #rutina que mira las marcas
                self.buscar_senial()
                #rutina de seguidor de lineas
                self.butia.set2MotorSpeed("0","600", "0", "600")
                if self.butia.getGray(self.idDer) > self.negroDer: #si derecha negro
                    self.corregir_izquierda()
                    print "corrijo izq"
                elif self.butia.getGray(self.idIzq) > self.negroIzq: # si izquierda negro
                    self.corregir_derecha()
                    print "corrijo der"
                #elif  self.butia.getGray(self.idIzq) < self.negroIzq and self.butia.getGray(self.idDer) < self.negroDer:
                    #while self.butia.getGray(self.idIzq) < self.negroIzq and self.butia.getGray(self.idDer) < self.negroDer:
                        #self.butia.set2MotorSpeed("0","700", "0", "700")

    def ver_distancias(self):
        salir = False
        while not salir:
            cod = self.data.get_codigo()
            if cod == "S":
                salir = True
            elif cod == "1":
                print "Left dist: " + str(self.detect.getMarkerTrigDist("Left"))
            elif cod == "2":
                print "Right dist: " + str(self.detect.getMarkerTrigDist("Right"))
            elif cod == "3":
                print "Stop dist: " + str(self.detect.getMarkerTrigDist("Stop"))
            elif cod == "4":
                print "Yield dist: " + str(self.detect.getMarkerTrigDist("Yield"))

    def buscar_senial(self):
        print "entro"
        if self.detect.isMarkerPresent("Left") and self.detect.getMarkerTrigDist("Left") < self.distMinimalSignal:
            print "estoy cerca de la senia iquierda"
            self.girar_iquierda()
        elif self.detect.isMarkerPresent("Left") and self.detect.getMarkerTrigDist("Left") < self.distMinimalSignal:
            print "estoy cerca de la senia iquierda"
            self.girar_iquierda()

        elif self.detect.isMarkerPresent("Yield") and self.detect.getMarkerTrigDist("Yield") < self.distMinimalSignal:
            print "paro los X segundos"
            self.stopNgo()
        elif self.detect.isMarkerPresent("Stop") and self.detect.getMarkerTrigDist("Stop") < self.distMinimalSignal:
            self.stop()


    def stop(self):
        self.data.set_codigo("S")

    def stopNgo(self):
        #paro X segundos
        #luego sigo derecho hasta no ver la marca
        salir = False
        self.butia.set2MotorSpeed("0", "0", "0", "0")
        time.sleep(3)
        self.detect.isMarkerPresent("Stop")
        self.detect.isMarkerPresent("Stop")
        self.detect.isMarkerPresent("Stop")
        while self.detect.isMarkerPresent("Stop") and not salir:
            cod = self.data.get_codigo()
            if cod == "S":
                salir = True
            self.butia.set2MotorSpeed("0","500", "0", "500")
        print "salgo parar"

    def girar_derecha(self):
        # giro hacia la izquieda hasta que el grisizquierda este en negro y el
        #gris izquierda en blanco
        salir = False
        while self.butiabot.getGray(self.idDer) < self.negroDer and not salir :#and self.butiabot.getGray(self.idIzq)  > self.negroIzq and not salir:
            cod = self.data.get_codigo()
            if cod == "S":
                salir = True
            self.butiabot.set2MotorSpeed("1", "400", "0", "400") #giro hacia la izquierda
        self.butiabot.set2MotorSpeed("0", "0", "0", "0")

    def girar_izquierda(self):
       salir = False
       print "encontre negro"
       while self.butiabot.getGray(self.idIzq) < self.negroIzq and not salir :#and self.butiabot.getGray(self.idIzq)  > self.negroIzq and not salir:
           cod = self.data.get_codigo()
           if cod == "S":
               salir = True
           self.butiabot.set2MotorSpeed("0", "400", "1", "400") #giro hacia la izquierda
       self.butiabot.set2MotorSpeed("0", "0", "0", "0")



    def corregir_izquierda(self):
        # busco linea a la derecha
        salir = False
        #self.butia.set2MotorSpeed("0","0", "0", "0")
        while self.butia.getGray(self.idDer)  > self.negroDer and not salir:
            cod = self.data.get_codigo()
            if cod =="S":
                salir = True
            self.butia.set2MotorSpeed("0", "500", "1", "500") #giro hacia la derecha
        #self.butia.set2MotorSpeed("0","500", "0", "500")

    def corregir_derecha(self):
        # busco linea a la izquierda
        #self.butia.set2MotorSpeed("0","0", "0", "0")
        salir = False
        while self.butia.getGray(self.idIzq) > self.negroIzq and not salir:
            cod = self.data.get_codigo()
            if cod =="S":
                salir = True
            self.butia.set2MotorSpeed("1", "400", "0", "400") #giro hacia la izquierda
        #self.butia.set2MotorSpeed("0","500", "0", "500")

    def busco_camino_izquierda(self):
        # giro a la izquierda hasta que el sensor derecho este en negro
        salir = False
        while self.butia.getGray(self.idDer) < self.negroDer  and not salir:
            #print "giro " +str()
            cod = self.data.get_codigo()
            if cod =="S":
                salir = True
            self.butia.set2MotorSpeed("0", "400", "1", "400") #giro hacia la izquierda

    def busco_camino_derecha(self):
        salir = False
        while self.butia.getGray(self.idIzq) != self.negro and not salir:
            cod = self.data.get_codigo()
            if cod =="S":
                salir = True
            self.butia.set2MotorSpeed("1", "400", "0", "400") #giro hacia la derecha

class ClaseTecla(threading.Thread):

    def __init__(self,data):
        print "Inicio ClaseTecla"
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        salir = False
        while not salir:
            a = raw_input('')
            #print "letra" + a
            if a.upper() =='C':
                salir = True
                self.data.set_codigo("C")
            else:
                self.data.set_codigo(a.upper())

        print "FIN ClaseTecla"




print "Soy el hilo principal"

pp = ClaseData()
l = ClaseMain(pp)
t = ClaseTecla(pp)
l.start()
t.start()


l.join()
t.join()
print "FIN"