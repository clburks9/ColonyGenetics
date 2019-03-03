"""
***********************************************************
File: colonyView.py
Author: Luke Burks
Date: March 2019

Implements an Interface for visulaization of recessive trait 
spread among small colonys of space travelers
***********************************************************
"""


__author__ = "Luke Burks"
__copyright__ = "Copyright 2019"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Luke Burks"
__email__ = "clburks9@gmail.com"
__status__ = "Development"



#TODO: Need population sizing dynamics and viability inheritance. Don't keep below threshold

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *; 
from PyQt5.QtGui import *;
from PyQt5.QtCore import *;


import sys,os
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure, SubplotParams
import matplotlib.pyplot as plt

from colonyModel import Colony; 


class SimulationWindow(QWidget):

	def __init__(self):

		super(SimulationWindow,self).__init__()
		offset = 532; 
		#self.setGeometry(-10,-10,684,812)
		self.setGeometry(-10+offset,-10,924,592)
		self.setFixedSize(924,592); 
		self.setStyleSheet("background-color:slategray;")
		self.layout = QGridLayout(); 
		self.setLayout(self.layout); 
		self.layout.setColumnStretch(0,1); 
		self.layout.setColumnStretch(1,2);

		self.viaRule = [0.25,1,0.5]
		self.preference = [0.5,0.5]; 
		self.popSize = 100; 


		self.resetSim(first = True); 

		self.CONTROL_FREQUENCY = 1; #Hz
		self.paused = False

		self.populateInterface(); 


		self.controlTimerStart(); 

		self.show()


	def populateInterface(self):
		

		#Colony Display
		##################################
		self.vLayout = QVBoxLayout(); 
		self.hLayout = QHBoxLayout(); 

		self.buttonLayout = QGridLayout(); 
		self.buttonArray = []; 


		self.buttonLayout.setSpacing(0); 
		self.buttonLayout.setContentsMargins(0,0,0,0); 

		self.hLayout.addStretch(1); 
		self.hLayout.addLayout(self.buttonLayout); 
		self.hLayout.addStretch(1); 

		self.vLayout.addLayout(self.hLayout); 
		self.vLayout.addStretch(1); 

		upper = int(self.model.size()/5); 
		for i in range(0,upper):
			self.buttonArray.append([]); 
			for j in range(0,5):
				b = QPushButton(); 
				b.setFixedSize(40,30);
				self.buttonArray[-1].append(b); 
				self.buttonLayout.addWidget(b,i,j);
				self.buttonLayout.setColumnMinimumWidth(j,40); 
			self.buttonLayout.setRowMinimumHeight(i,26);  
		self.setButtonColors(); 
		self.layout.addLayout(self.vLayout,0,0,2,1); 


		#Controls
		##################################
		self.controlLayout = QGridLayout(); 

		self.generationLabel = QLabel("Generation: {}".format(self.generation)); 
		self.controlLayout.addWidget(self.generationLabel,0,0)

		self.playPause = QPushButton("Pause"); 
		self.playPause.clicked.connect(lambda: self.togglePause()); 
		self.playPause.setStyleSheet("background-color: red"); 
		self.controlLayout.addWidget(self.playPause,0,1); 

		self.updateButton = QPushButton("Update"); 
		self.updateButton.clicked.connect(lambda: self.resetSim(update=True)); 
		self.controlLayout.addWidget(self.updateButton,0,2); 

		self.reset = QPushButton("Reset"); 
		self.reset.clicked.connect(lambda: self.resetSim()); 
		self.controlLayout.addWidget(self.reset,0,3); 


		#Preference Control for resets
		self.prefControlRed = QSlider(Qt.Horizontal); 
		self.prefControlRed.setSliderPosition(int(self.preference[1]*100))
		self.prefControlRed.setTickPosition(QSlider.NoTicks)
		self.prefControlRed.setTickInterval(10);  



		tmp = QLabel("Initial Distribution: "); 
		self.controlLayout.addWidget(tmp,1,0,1,1); 
		tmp = QLabel("Red"); 
		tmp.setAlignment(Qt.AlignCenter)
		self.controlLayout.addWidget(tmp,1,1,1,1); 
		tmp = QLabel("Green"); 
		tmp.setAlignment(Qt.AlignCenter)
		self.controlLayout.addWidget(tmp,1,2,1,1); 


		self.controlLayout.addWidget(self.prefControlRed,2,1,1,2); 


		#Viability Control For Resets
		self.viaControlRed = QSlider(Qt.Horizontal); 
		self.viaControlRed.setSliderPosition(int(self.viaRule[0]*100))
		self.viaControlRed.setTickPosition(QSlider.NoTicks)
		self.viaControlRed.setTickInterval(10); 

		self.viaControlYellow = QSlider(Qt.Horizontal); 
		self.viaControlYellow.setSliderPosition(int(self.viaRule[1]*100))
		self.viaControlYellow.setTickPosition(QSlider.NoTicks)
		self.viaControlYellow.setTickInterval(10);

		self.viaControlGreen = QSlider(Qt.Horizontal); 
		self.viaControlGreen.setSliderPosition(int(self.viaRule[2]*100))
		self.viaControlGreen.setTickPosition(QSlider.NoTicks)
		self.viaControlGreen.setTickInterval(10);  



		tmp = QLabel("Viability Rule: "); 
		self.controlLayout.addWidget(tmp,3,0,1,1); 
		tmp = QLabel("Red"); 
		tmp.setAlignment(Qt.AlignCenter)
		self.controlLayout.addWidget(tmp,3,1,1,1); 
		tmp = QLabel("Yellow"); 
		tmp.setAlignment(Qt.AlignCenter)
		self.controlLayout.addWidget(tmp,3,2,1,1); 
		tmp = QLabel("Green"); 
		tmp.setAlignment(Qt.AlignCenter)
		self.controlLayout.addWidget(tmp,3,3,1,1); 

		self.controlLayout.addWidget(self.viaControlRed,4,1,1,1);
		self.controlLayout.addWidget(self.viaControlYellow,4,2,1,1); 
		self.controlLayout.addWidget(self.viaControlGreen,4,3,1,1); 


		#Viability control for resets

		self.speedSlider = QSlider(Qt.Horizontal); 
		self.speedSlider.setSliderPosition(3)
		self.speedSlider.setTickPosition(QSlider.TicksBelow)
		self.speedSlider.setTickInterval(1); 
		self.speedSlider.setRange(0,5);
		self.speedSlider.valueChanged.connect(lambda: self.changeInterval()); 
		self.controlLayout.addWidget(self.speedSlider,5,0,1,4); 

		self.layout.addLayout(self.controlLayout,0,1,1,1); 


		#Stats Graph
		##################################
		self.graphView = QGraphicsView(self); 
		self.graphScene = QGraphicsScene(self); 
		self.graphPixmap = self.graphScene.addPixmap(QPixmap()); 
		self.graphView.setScene(self.graphScene); 
		self.makeGraph(); 

		self.layout.addWidget(self.graphView,1,1,1,1); 

	def setButtonColors(self):
		upper = int(self.model.size()/5); 
		for i in range(0,self.model.size()):

			g = self.model[i].gene; 
			if(g[0] == 0 and g[1] == 0):
				#self.buttonArray[i%5][i%upper].setStyleSheet("background-color: red"); 
				self.buttonArray[i//5][i%5].setStyleSheet("background-color: red"); 
			elif((g[0] == 1 and g[1] == 0) or (g[0] == 0 and g[1] == 1)):
				#self.buttonArray[i%5][i%upper].setStyleSheet("background-color: yellow"); 
				self.buttonArray[i//5][i%5].setStyleSheet("background-color: yellow"); 
			elif(g[0] == 1 and g[1] == 1):
				#self.buttonArray[i%5][i%upper].setStyleSheet("background-color: green"); 
				self.buttonArray[i//5][i%5].setStyleSheet("background-color: green"); 

	def makeGraph(self):
		
		#Set up plotting objects
		##################################
		sp = SubplotParams(left=0.,bottom=0.,right=1.,top=1.); 
		fig = Figure(subplotpars=sp); 
		canvas = FigureCanvas(fig); 
		ax = fig.add_subplot(111); 

		#Get Data
		##################################
		genes = self.model.getGenes(); 
		tmp = {'Empty':0,'Half':0,'Full':0}
		for g in genes:
			if(g[0] == 0 and g[1] == 0):
				tmp['Empty'] += 1; 
			elif((g[0] == 0 and g[1] == 1) or (g[0] == 1 and g[1] == 0)):
				tmp['Half'] += 1; 
			elif(g[0] == 1 and g[1] == 1):
				tmp['Full'] += 1; 

		for key in tmp.keys():
			self.stateTrace[key].append(tmp[key]); 


		colors = {'Empty':'r','Half':'y','Full':'g'}; 
		sizeHintX = 0; 
		for key in self.stateTrace.keys():
			ax.plot(self.stateTrace[key],c=colors[key],linewidth = 3); 
			sizeHintX = 5*len(self.stateTrace[key])/4

		ax.set_xlim([0,int(sizeHintX)]); 
		ax.set_ylim([-3,len(genes)+3]); 
		

		canvas.draw(); 

		#canvas = makeBeliefMap(wind); 
		size = canvas.size(); 
		width,height = size.width(),size.height(); 
		im = QImage(canvas.buffer_rgba(),width,height,QtGui.QImage.Format_ARGB32); 
		im = im.rgbSwapped(); 
		pm = QPixmap(im); 
		pm = pm.scaled(150*4,150*3);

		self.graphPixmap.setPixmap(pm); 


	def controlTimerStart(self):
		self.controlTimer = QtCore.QTimer(self); 
		self.controlTimer.timeout.connect(lambda: self.controlTimerTimeout()); 
		self.controlTimer.start((1/self.CONTROL_FREQUENCY)*1000); 

	def togglePause(self):
		if(self.paused):
			self.paused = False;
			self.playPause.setText("Pause")
			self.playPause.setStyleSheet("background-color: red");  
		else:
			self.paused = True;
			self.playPause.setText("Play")
			self.playPause.setStyleSheet("background-color: green");  


	def changeInterval(self):
		#Want 0 to be 0.1, want 100 to be 10
		sl = self.speedSlider.sliderPosition(); 
		c = 1; 
		if(sl == 0):
			c = 0.1; 
		elif(sl == 1):
			c = 0.5; 
		elif(sl == 2):
			c = 1; 
		elif(sl == 3):
			c = 2; 
		elif(sl == 4):
			c = 5; 
		elif(sl == 5):
			c = 10;
		self.CONTROL_FREQUENCY = c; 
		self.controlTimer.setInterval((1/self.CONTROL_FREQUENCY)*1000)

	def controlTimerTimeout(self):
		if(not self.paused):
			self.model.update(); 
			self.setButtonColors(); 
			self.makeGraph(); 
			self.generation += 1; 
			self.generationLabel.setText("Generation: {}".format(self.generation)); 
		

	def resetSim(self,first = False,update=False):

		#get current prefences
		if(not first):

			if(not update):
				self.preference = [1-self.prefControlRed.sliderPosition()/100,self.prefControlRed.sliderPosition()/100]; 

			self.viaRule = [self.viaControlRed.sliderPosition()/100,self.viaControlYellow.sliderPosition()/100,self.viaControlGreen.sliderPosition()/100]; 

		

		if(not update):
			self.model = Colony(N=self.popSize,persSet = self.preference,viaRule = self.viaRule); 
			self.generation = 0; 
			self.stateTrace = {'Empty':[],'Half':[],'Full':[]}; 
		else:
			self.model.modViability(self.viaRule); 



if __name__ == '__main__':


	app = QApplication(sys.argv); 
	ex = SimulationWindow(); 
	sys.exit(app.exec_()); 
