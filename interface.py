#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from pyqtgraph.Qt import QtGui
from lase.gui import WelcomeWidget
import pyqtgraph as pg
from PyQt4.QtCore import SIGNAL 
import os
import ctypes
import platform

class KWindow(QtGui.QMainWindow):
    """
    Main window of the interface    
    """
    
    def __init__(self, app):
        super(KWindow, self).__init__()

        self.setStyleSheet("""background-color: white; font-family: lato""")

        self.current_path = os.getcwd()
        self.bitstreams_path = os.path.join(self.current_path,'bitstreams')
        self.img_path = os.path.join(self.current_path, 'static', 'img')
        self.static_path = os.path.join(self.current_path, 'static')
        self.tmp_path = os.path.join(self.current_path,'tmp')
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)
        
        self.data_path = os.path.join(self.tmp_path, 'data')
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            
        self.ip_path = os.path.join(self.tmp_path, 'ip')
        if not os.path.exists(self.ip_path):
            os.makedirs(self.ip_path)
        
        # Init const
        self.app = app
        self.session_opened = True
        self.setWindowTitle('Lase') # Title
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.img_path,'icon_koheron.png')))
        self.resize(1400, 900) # Size
        self.frame_rate = 0
        
        # Layout        
        self.stacked_widget = QtGui.QStackedWidget()
        self.welcome_widget = WelcomeWidget(self, ip_path=self.ip_path)
        self.stacked_widget.addWidget(self.welcome_widget)        
        self.setCentralWidget(self.stacked_widget)
        
        self.show()
        
        self.stacked_widget.currentWidget().setFocus()
        self.connect(self, SIGNAL('triggered()'), self.closeEvent)
       
        self.start_time = time.time()
        self.prev_time = 0

    def update(self):
        if self.stacked_widget.currentIndex() == 0:
            self.session_opened = self.welcome_widget.select_opened
            time.sleep(0.02)
        else:
            widget = self.stacked_widget.currentWidget()
            if widget.driver.opened:                
                widget.frame_rate = self.frame_rate
                widget.update()
            else:                                
                widget.driver.close()
                self.stacked_widget.removeWidget(widget)
                self.stacked_widget.currentWidget().setFocus()
                
    def closeEvent(self, event):
        if self.stacked_widget.currentIndex() != 0:     
                self.stacked_widget.currentWidget().driver.close()
        self.session_opened = False
        self.close()
        
def main():
    
    app = QtGui.QApplication.instance()    
    pg.setConfigOptions(background='k')  
    pg.setConfigOptions(foreground='d')  
    if app == None:
        app = QtGui.QApplication([])
    app.quitOnLastWindowClosed()    
    
    # Icon to show in task bar for Windows
    if platform.system() == 'Windows':
	myappid = 'koheron.lase'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    window = KWindow(app)
        
    prev_time = 0
    i = 0
    # Start the update loop:
    while window.session_opened:         
        i = i+1  
        window.update()
        time_ = time.time() 
        window.frame_rate = 0.90 * window.frame_rate + 0.1/(0.001+time_-prev_time)        
        QtGui.QApplication.processEvents()
        prev_time = time_

if __name__ == '__main__':
    main()
