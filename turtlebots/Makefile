# Makefile for butia
#
# Copyright (C) 2008 Guillermo Reisch (greisch@fing.edu.uy)
# Copyright (C) 2010 Andres Aguirre (aaguirre@fing.edu.uy)
# Copyright (C) 2012, 2016 Alan Aguiar (alanjas@hotmail.com)
#
# Butia is a free open plataform for robotics projects
# http://www.fing.edu.uy/inco/proyectos/butia
# Universidad de la República del Uruguay
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#versions to checkout before build
TURTLEBLOCKS_VERSION = f21373084a3cec86f63da8a7e62ba9d566f43362
EXTRAS_VERSION = fbd88b928d1c9da21183d7e730073c05bd2f430d
NXT_VERSION = bfa27b7d0f509c987f7fd6201de83934f245faa9
WEDO_VERSION = ad432528d5883a39e6c9dcfb5e5dc9a353fa5761
ARDUINO_VERSION = ea6ae5b0fb22ab6778fdfc457a51dde8f914e977
PYUSB_VERSION = 1f66ccd5d252e969b1de9bf91bf24e5c64294b8d
RODI_VERSION = 34e4d86e0cc55a67c6667d2aee67c247d2f6184c

SHELL = /bin/sh
# check work in "sh" instad of bash, make it more portable!!!
INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = $(INSTALL) -m 644
LESS = less
BUILDDIR = tmp
TMPBUILDDIR = /tmp/build
NOGIT =

#intallation directorys
#prefix = /usr/local   ###change to build debian package...###
prefix = /usr
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin
sbindir = $(exec_prefix)/sbin
libexecdir = $(exec_prefix)/libexec
datarootdir = $(prefix)/share
datadir = $(datarootdir)
sysconfdir = $(prefix)/etc
sharedstatedir = $(prefix)/com
localstatedir = $(prefix)/var
includedir = $(prefix)/include
oldincludedir = $(prefix)/include
docdir = $(datarootdir)/doc/tortubots
infodir = $(datarootdir)/info
libdir = $(exec_prefix)/lib
localedir = $(datarootdir)/locale
mandir = $(datarootdir)/man
man1dir = $(mandir)/man1
man2dir = $(mandir)/man2 # etc... etc...
activitiesdir = $(datadir)/sugar/activities



all: apply_hard_plugins


help:
	if [ -e /usr/bin/less ] ; then $(LESS) INSTALL ; fi
	# if the user not have less command...
	cat INSTALL

############################## Init of submodules ##############################

first:
	(cd .. && git submodule update --init)

################################ Dependencies ##################################

install-dependencies:
	sudo apt-get install libglib2.0-dev libgstreamer0.10-dev debhelper python-gtk2 

#################### Initialization of "especific" submodules ##################

mainline/.git:
	$(MAKE) first

WeDoMore/.git:
	$(MAKE) first

turtle-extras/.git:
	$(MAKE) first

nxt_plugin/.git:
	$(MAKE) first

arduino/.git:
	$(MAKE) first

pyusb/.git:
	$(MAKE) first

rodi/.git:
	$(MAKE) first

######################## Checkout a version of submodule #######################

SUBMODULE = mainline
SUBMODULEVER = master

checkoutsm:
ifndef NOGIT
	(cd $(SUBMODULE) && git clean -xdf ) 
	(cd $(SUBMODULE) && if (git checkout $(SUBMODULEVER) ); then echo OK ; else git fetch ; git checkout $(SUBMODULEVER) ; fi )
endif

################## Checkout a especific version of submodules ##################

walterGIT: mainline/.git
	$(MAKE) SUBMODULE=mainline SUBMODULEVER=$(TURTLEBLOCKS_VERSION) checkoutsm

extrasGIT: turtle-extras/.git
	$(MAKE) SUBMODULE=turtle-extras SUBMODULEVER=$(EXTRAS_VERSION) checkoutsm

wedoGIT: WeDoMore/.git
	$(MAKE) SUBMODULE=WeDoMore SUBMODULEVER=$(WEDO_VERSION) checkoutsm

nxtGIT: nxt_plugin/.git
	$(MAKE) SUBMODULE=nxt_plugin SUBMODULEVER=$(NXT_VERSION) checkoutsm

arduinoGIT: arduino/.git
	$(MAKE) SUBMODULE=arduino SUBMODULEVER=$(ARDUINO_VERSION) checkoutsm

pyusbGIT: pyusb/.git
	$(MAKE) SUBMODULE=pyusb SUBMODULEVER=$(PYUSB_VERSION) checkoutsm

rodiGIT: rodi/.git
	$(MAKE) SUBMODULE=rodi SUBMODULEVER=$(RODI_VERSION) checkoutsm

sourceGIT: walterGIT extrasGIT wedoGIT nxtGIT arduinoGIT pyusbGIT rodiGIT
	echo sourceGIT

################################# Construction #################################

mktmpfolder:
	#making folders and copying mainline
	rm -rf $(BUILDDIR)
	cp -rL mainline $(BUILDDIR)
	rm -rf $(BUILDDIR)/.git
	rm -f  $(BUILDDIR)/.gitignore
	rm -f  $(BUILDDIR)/turtleblocks
	rm -f  $(BUILDDIR)/turtleblocks.desktop
	rm -f  $(BUILDDIR)/setup.py
	# patch the activity.info and add some icons (TurtleBlocks => TurtleBots)
	cp -rLf stagin/activity $(BUILDDIR)/
	cp -f stagin/turtlebots $(BUILDDIR)/
	cp -f stagin/turtlebots.desktop $(BUILDDIR)/
	cp -f stagin/bundlebuilder.py $(BUILDDIR)/setup.py

apply_localization: sourceGIT mktmpfolder
	# let's add localization (if is not already in taextras.py)
	(cd turtle-extras && ./merge.py turtlebots $(BUILDDIR))
	#cp turtle-extras/taextras.py $(BUILDDIR)
	# fix localization (compile .po)
	(cd $(BUILDDIR) && python setup.py build)

apply_hard_plugins: apply_localization sourceGIT pattern_detection_compile
	cp -rLf ardrone               $(BUILDDIR)/plugins/
	cp -rLf atyarandu             $(BUILDDIR)/plugins/
	cp -rLf ax12                  $(BUILDDIR)/plugins/
	cp -rLf butia                 $(BUILDDIR)/plugins/
	cp -rLf sumtia                $(BUILDDIR)/plugins/
	cp -rLf fischer               $(BUILDDIR)/plugins/
	cp -rLf followme              $(BUILDDIR)/plugins/
	cp -rLf colorview             $(BUILDDIR)/plugins/
	cp -rLf nxt_plugin            $(BUILDDIR)/plugins/
	cp -rLf rodi                  $(BUILDDIR)/plugins/
	cp -rLf WeDoMore/wedo_plugin  $(BUILDDIR)/plugins/
	cp -rLf arduino               $(BUILDDIR)/plugins/
	cp -rLf pattern_detection     $(BUILDDIR)/plugins/
	cp -rLf xevents               $(BUILDDIR)/plugins/
	# remove nxt trash
	rm -rf $(BUILDDIR)/plugins/nxt_plugin/.git
	rm -f $(BUILDDIR)/plugins/nxt_plugin/.gitignore
	rm -rf $(BUILDDIR)/plugins/nxt_plugin/usb
	# we add pybluez as dependency
	rm -rf $(BUILDDIR)/plugins/nxt_plugin/nxt/bluetooth
	# remove arduino trash
	rm -rf $(BUILDDIR)/plugins/arduino/.git
	rm -f $(BUILDDIR)/plugins/arduino/.gitignore
	# remove rodi trash
	rm -rf $(BUILDDIR)/plugins/rodi/.git
	rm -f $(BUILDDIR)/plugins/rodi/.gitignore
	# add pyusb extra information
	cp pyusb/ACKNOWLEDGEMENTS   $(BUILDDIR)/plugins/butia/pybot/usb
	cp pyusb/LICENSE            $(BUILDDIR)/plugins/butia/pybot/usb
	cp pyusb/README.rst         $(BUILDDIR)/plugins/butia/pybot/usb
	# update pyusb for others plugins
	cp -rLf $(BUILDDIR)/plugins/butia/pybot/usb $(BUILDDIR)/plugins/nxt_plugin/
	cp -rLf $(BUILDDIR)/plugins/butia/pybot/usb $(BUILDDIR)/plugins/wedo_plugin/
	cp -rLf $(BUILDDIR)/plugins/butia/pybot/usb $(BUILDDIR)/plugins/fischer/
	cp WeDoMore/README.rst $(BUILDDIR)/plugins/wedo_plugin/
	cp WeDoMore/LICENSE $(BUILDDIR)/plugins/wedo_plugin/
	# put pattern_examples into turtle examples folder
	mv $(BUILDDIR)/plugins/pattern_detection/doc/turtleArtExamples $(BUILDDIR)/samples/pattern_examples
	# put butia examples into turtle examples folder
	cp -rf examples/turtle $(BUILDDIR)/samples/butia
	cp -rf examples/followme $(BUILDDIR)/samples/
	# put xevents examples into turtle examples folder
	cp -rf xevents/samples $(BUILDDIR)/samples/xevents
	# put arduino examples into turtle examples folder
	mv $(BUILDDIR)/plugins/arduino/examples $(BUILDDIR)/samples/arduino
	# remove unnecessary .o files of pattern_detection
	rm $(BUILDDIR)/plugins/pattern_detection/library/patterns/*.o
	# remove ARTollkit binaries
	rm -rf $(BUILDDIR)/plugins/pattern_detection/library/ARToolkit

pattern_detection_compile:
	$(MAKE) -C pattern_detection/library

apply_sym_plugins: sourceGIT apply_localization pattern_detection_compile
	# let's make symlinks, it lets you, edit and try, more easily!
	ln -s `pwd`/ardrone                $(BUILDDIR)/plugins/ardrone
	ln -s `pwd`/atyarandu              $(BUILDDIR)/plugins/atyarandu
	ln -s `pwd`/ax12                   $(BUILDDIR)/plugins/ax12
	ln -s `pwd`/butia                  $(BUILDDIR)/plugins/butia
	ln -s `pwd`/sumtia                 $(BUILDDIR)/plugins/sumtia
	ln -s `pwd`/fischer                $(BUILDDIR)/plugins/fischer
	ln -s `pwd`/followme               $(BUILDDIR)/plugins/followme
	ln -s `pwd`/colorview              $(BUILDDIR)/plugins/colorview
	ln -s `pwd`/nxt_plugin             $(BUILDDIR)/plugins/nxt_plugin
	ln -s `pwd`/WeDoMore/wedo_plugin   $(BUILDDIR)/plugins/wedo_plugin
	ln -s `pwd`/arduino                $(BUILDDIR)/plugins/arduino
	ln -s `pwd`/pattern_detection      $(BUILDDIR)/plugins/pattern_detection
	ln -s `pwd`/rodi                   $(BUILDDIR)/plugins/rodi
	ln -s `pwd`/xevents                $(BUILDDIR)/plugins/xevents
	# add pyusb for wedo
	ln -s `pwd`/pyusb/usb              $(BUILDDIR)/plugins/wedo_plugin/usb

xo:
	$(MAKE) BUILDDIR=$(TMPBUILDDIR) apply_hard_plugins
	# dist_xo no work in the tmp folder -> use /tmp
	# workarround for double locale .mo files
	(cd $(TMPBUILDDIR) && rm -rf locale)
	(cd $(TMPBUILDDIR) && git init)
	(cd $(TMPBUILDDIR) && git add *)
	(cd $(TMPBUILDDIR) && git commit -m 'all files')
	(cd $(TMPBUILDDIR) && python setup.py build)
	(cd $(TMPBUILDDIR) && python setup.py dist_xo)
	cp $(TMPBUILDDIR)/dist/*.xo .
	$(MAKE) BUILDDIR=$(TMPBUILDDIR) clean-builddir

dev: apply_sym_plugins
	rm -rf ~/Activities/TurtleBots.activity
	mkdir -p ~/Activities
	(cd $(BUILDDIR) && python setup.py dev)


################################## Plugins #####################################

plugin-ardrone: apply_hard_plugins
	cp stagin/plugins/ardrone/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf ardrone_plugin.tar.gz ardrone/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/ardrone_plugin.tar.gz .

plugin-atyarandu: apply_hard_plugins
	cp stagin/plugins/atyarandu/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf atyarandu_plugin.tar.gz atyarandu/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/atyarandu_plugin.tar.gz .

plugin-ax12: apply_hard_plugins
	cp stagin/plugins/ax12/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf ax12_plugin.tar.gz ax12/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/ax12_plugin.tar.gz .

plugin-butia: apply_hard_plugins
	cp stagin/plugins/butia/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf butia_plugin.tar.gz butia/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/butia_plugin.tar.gz .

plugin-fischer: apply_hard_plugins
	cp stagin/plugins/fischer/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf fischer_plugin.tar.gz followme/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/fischer_plugin.tar.gz .

plugin-followme: apply_hard_plugins
	cp stagin/plugins/followme/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf followme_plugin.tar.gz followme/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/followme_plugin.tar.gz .

plugin-colorview: apply_hard_plugins
	cp stagin/plugins/colorview/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf colorview_plugin.tar.gz followme/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/colorview_plugin.tar.gz .

plugin-nxt: apply_hard_plugins
	cp stagin/plugins/nxt_plugin/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf nxt_plugin.tar.gz nxt_plugin/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/nxt_plugin.tar.gz .

plugin-wedo: apply_hard_plugins
	cp stagin/plugins/wedo_plugin/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf wedo_plugin.tar.gz wedo_plugin/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/wedo_plugin.tar.gz .

plugin-arduino: apply_hard_plugins
	cp stagin/plugins/arduino/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf arduino_plugin.tar.gz arduino/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/arduino_plugin.tar.gz .

plugin-marcas: apply_hard_plugins
	cp stagin/plugins/pattern_detection/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf pattern_detection.tar.gz pattern_detection/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/pattern_detection.tar.gz .

plugin-rodi: apply_hard_plugins
	cp stagin/plugins/rodi/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf rodi_plugin.tar.gz rodi/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/rodi_plugin.tar.gz .

plugin-xevents: apply_hard_plugins
	cp stagin/plugins/xevents/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf xevents_plugin.tar.gz xevents/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/xevents_plugin.tar.gz .

plugins: plugin-butia plugin-followme plugin-colorview plugin-nxt plugin-wedo \
         plugin-marcas plugin-arduino plugin-rodi plugin-xevents plugin-ax12

plugin-all: plugins

############################## Install procedures ##############################

install-activity: xo
	sugar-install-bundle *.xo

install-xo: install-activity

install: all
	$(MAKE) prefix= install-rules
	mkdir -p $(DESTDIR)$(activitiesdir)
	cp -r $(BUILDDIR) $(DESTDIR)$(activitiesdir)/TurtleBots.activity
	mkdir -p $(DESTDIR)$(bindir)
	$(INSTALL) stagin/turtlebots $(DESTDIR)$(bindir)/
	mkdir -p $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps
	$(INSTALL_DATA) stagin/activity/turtlebots.svg $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps/
	mkdir -p $(DESTDIR)$(datadir)/applications
	$(INSTALL_DATA) $(BUILDDIR)/turtlebots.desktop $(DESTDIR)$(datadir)/applications/

install-strip: install
	#strip $(DESTDIR) file...

install-rules:
	if [ -e $(DESTDIR)/lib/udev/rules.d/60-usb4all.rules ] ; then \
		echo Rules already exists ; \
	else \
		cp `pwd`/rules/60-lego-nxt.rules $(DESTDIR)/lib/udev/rules.d; \
		cp `pwd`/rules/60-usb4all.rules $(DESTDIR)/lib/udev/rules.d; \
		cp `pwd`/rules/60-fischertechnik.rules $(DESTDIR)/lib/udev/rules.d; \
		cp `pwd`/rules/60-lego-wedo.rules $(DESTDIR)/lib/udev/rules.d; \
	fi ;
	if [ -e $(DESTDIR)/etc/group ] ; then \
		./permissions.sh ; \
	fi ;

############################# UNInstall procedures #############################

uninstall-activity:
	rm -rf ~/Activities/TurtleBots.activity

uninstall-xo: uninstall-activity

uninstall-dev: uninstall-activity

uninstall-strip: uninstall
	#unstrip $(DESTDIR) file...

uninstall:
	$(MAKE) prefix= uninstall-rules
	rm -rf $(DESTDIR)$(activitiesdir)/TurtleBots.activity
	rmdir -p --ignore-fail-on-non-empty $(DESTDIR)$(activitiesdir)
	rm -f $(DESTDIR)$(bindir)/turtlebots
	rmdir -p --ignore-fail-on-non-empty $(DESTDIR)$(bindir)
	rm -f  $(DESTDIR)$(datadir)/applications/turtlebots.desktop
	rmdir -p --ignore-fail-on-non-empty $(DESTDIR)$(datadir)/applications
	rm -f $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps/turtlebots.svg
	rmdir -p --ignore-fail-on-non-empty $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps

uninstall-rules:
	rm -f $(DESTDIR)/lib/udev/rules.d/60-lego-nxt.rules
	rm -f $(DESTDIR)/lib/udev/rules.d/60-usb4all.rules
	rm -f $(DESTDIR)/lib/udev/rules.d/60-fischertechnik.rules
	rm -f $(DESTDIR)/lib/udev/rules.d/60-lego-wedo.rules
	if [ -e $(DESTDIR)/etc/group ] ; then \
		if (delgroup --system robots) ; then echo group removed... ; fi ; \
	fi ;

################################# CLEAN STUFF ##################################

clean: clean-tmp clean-plugins clean-xo clean-builddir
	$(MAKE) -C pattern_detection/library clean
	# this remove only if it's a symlink ; don't remove if installed
	rm -f ~/Activities/TurtleBots.activity

clean-tmp:
	rm -rf tmp

clean-builddir:
	rm -rf $(BUILDDIR)

clean-xo:
	rm -f *.xo

clean-plugins:
	rm -f *.tar.gz

.SUFFIXES: .c .o .py .pyc .po .pot

# targets that not represent generated files
.PHONY: all help \
 clean clean-tmp clean-builddir clean-xo clean-plugins \
 first walterGIT extrasGIT wedoGIT nxtGIT arduinoGIT rodiGIT pyusbGIT \
 xo mktmpfolder apply_hard_plugins apply_sym_plugins \
 install install-strip install-dependencies \
 uninstall uninstall-strip \
 plugin-butia plugin-followme plugin-nxt plugin-wedo plugins plugin-all \
 dev pattern_detection_compile plugin-arduino plugin-rodi plugin-fischer \
 plugin-colorview plugin-xevents plugin-ax12 plugin-atyarandu plugin-ardrone
