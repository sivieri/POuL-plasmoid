# -*- coding: utf-8 -*-
#
# Author: Alessandro Sivieri <alessandro.sivieri@gmail.com>
# Date: sab dic 12 2009, 13:28:17
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation; either version 2, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
#
# You should have received a copy of the GNU Library General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kio import *
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

import commands
import os
import os.path
import sys

class PoulPlasmoid(plasmascript.Applet):
    def __init__(self, parent, args = None):
        plasmascript.Applet.__init__(self, parent)

    def init(self):
        # Status things
        self.status = -1
        self.sleep = 300000
        
        # Graphics
        self.layout = QGraphicsLinearLayout(Qt.Horizontal, self.applet)
        self.icon = Plasma.IconWidget(KIcon("dialog-error"), "", self.applet)
        self.label = Plasma.Label()
        self.label.setText("Stato sconosciuto")
        self.layout.addItem(self.icon)
        self.layout.addItem(self.label)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.resize(200, 70)
        self.setHasConfigurationInterface(False)
        
        # Notifications & icons
        gc = self.config()
        if gc.readEntry("notification", "0") == "0":
            kdehome = unicode(KGlobal.dirs().localkdedir())
            if not os.path.exists(kdehome+"share/apps/poulplasmoid/poulplasmoid.notifyrc"):
                if os.path.exists(kdehome+"share/apps"):
                    self.createNotifyrc(kdehome)
                    gc.writeEntry("notification", "1")
        if gc.readEntry("icon", "0") == "0":
            self.installIcon()
            gc.writeEntry("icon", "1")
        
        # Timer
        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.getStatus)
        self.timer.start(self.sleep)
        
        # Startup check
        self.getStatus()
    
    def contextualActions(self):
        actions = list()
        refresh = QAction(KIcon("view-refresh"), "Refresh", self.applet)
        self.connect(refresh, SIGNAL("triggered(bool)"), self.getStatus)
        actions.append(refresh)
        return actions
    
    def getStatus(self):
        self.setBusy(True)
        url = KUrl("http://bits.otacon22.it/read_app.txt")
        # Hopefully, KIO should use main proxy settings
        job = KIO.storedGet(url, KIO.Reload, KIO.HideProgressInfo)
        self.connect(job, SIGNAL("result(KJob*)"), self.resultData)
    
    def resultData(self, job):
        if job.error() == 0:
            try:
                status = int(job.data())
            except ValueError:
                self.setStatus(-1)
            self.setStatus(status)
        else:
            self.setStatus(-1)
        self.update()
        self.setBusy(False)
    
    def setStatus(self, status):
        if status != self.status:
            if status == 1:
                self.updateStatus("user-online", "Sede aperta")
            elif status == 0:
                self.updateStatus("user-offline", "Sede chiusa")
            else:
                self.updateStatus("dialog-error", "Stato sconosciuto")
            self.status = status
    
    def updateStatus(self, icon, text):
        self.icon.setIcon(KIcon(icon))
        self.label.setText(text)
        KNotification.event(KNotification.Notification, text)
    
    def createDirectory(self, d):
        if not os.path.isdir(d):
            try:
                os.mkdir(d)
            except:
                print "Problem creating directory: "+d
                print "Unexpected error:", sys.exc_info()[0]
    
    def createNotifyrc(self, kdehome):
        # Create poulplasmoid directory if required
        self.createDirectory(kdehome+"share/apps/poulplasmoid")
        # File to create
        fn = kdehome+"share/apps/poulplasmoid/poulplasmoid.notifyrc"
        # File contents
        c = []
        c.append("[Global]\n")
        c.append("Comment=POuL Plasmoid\n")
        c.append("Name=POuL Plasmoid\n")
        c.append("\n")
        c.append("[Event/update]\n")
        c.append("Name=Status updated\n")
        c.append("Action=Popup\n")
        # Write file
        try:
            f = open(fn,"w")
            f.writelines(c)
            f.close()
        except:
            print "Problem writing to file: "+fn
            print "Unexpected error:", sys.exc_info()[0]
    
    def installIcon(self):
        out = commands.getstatusoutput("xdg-icon-resource install --size 128 " + unicode(self.package().path()) + "contents/icons/poul-128x128.png poul-plasmoid")
        if out[0] == 0:
            print "gmail-plasmoid icon installed"
        else:
            print "Error installing gmail-plasmoid icon:", out

def CreateApplet(parent):
    return PoulPlasmoid(parent)
