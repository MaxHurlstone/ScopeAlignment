import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
# from PyQt5 import QtGui
import PyQt5
import sys
import datetime
import numpy as np
import queue

from aiohttp import web
import socketio
import ssl

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as tkr

import skyfield
from skyfield.api import Loader, Topos, Star
from skyfield import almanac
from skyfield.data import hipparcos

import what3words

import datetime
import time
import math
import scipy
from scipy.signal import lfilter
from pykalman import KalmanFilter

# import server

class PyQtPlotter():



    def __init__(self, oQ, aQ):
        self.oQ = oQ
        self.aQ = aQ
        self.oData = (0,0)
        self.initZ = 0
        self.initY = 0
        self.FOVz = 360
        self.FOVy = 90
        self.onRight = False
        self.driftZ = 0
        self.driftY = 0
        self.calibZ = 0
        self.calibY = 0
        self.textPos = [10,10]
        self.moveText = False
        self.oldTime = ""

        self.movingAverageZ = np.zeros((10,1))
        self.movingAverageY = np.zeros((10,1))

        self.z = 0
        self.y = 0
        self.targetZ = 0
        self.targetY = 0
        self.moveFOV = False
        self.ErrZ = 0
        self.ErrY = 0

        self.testErr = False


        self.text = ""
        self.input = ""

        self.target = ""
        self.typeTarget = ""
        self.exposureT = ""
        self.location = ""
        self.locName = ""
        self.lat = ""
        self.lng = ""

        # Noise removal experimenting
        self.noiseRemoval = False
        self.n = 15
        self.b = [1.0/self.n]*self.n
        self.a = 1

        # pykalman experimenting
        self.kalmanActive = False
        self.calibrating =  False
        self.calibrationDP =  1000 # 100000 # 10 seconds of tracking assuming 1ms per update
        self.transMatrix = [[1, 1, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 1],
                            [0, 0, 0, 1]]
        self.obsMatrix = [[1, 0, 0, 0],
                          [0, 0, 1, 0]]
        self.initStateMu = []
        self.measurements = np.zeros((self.calibrationDP,2))
        self.xNow = []
        self.pNow = []


        # Set up data sets
        self.load = Loader('C:\Max\Programming\js\ScopeAlignment\SFData')
        self.data = self.load("de421.bsp")

        with self.load.open(hipparcos.URL) as f:
            self.df = hipparcos.load_dataframe(f)
        self.ts = self.load.timescale()

        self.earth = self.data["earth"]

        self.shutterOpen = False
        self.tStart = 0
        self.firstRequest = True
        self.prevData = [0,0]
        self.currData = [0,0]
        self.deltaData = [0,0]
        self.targetSet = False

        # Plotting window
        self.app = QtGui.QApplication([])
        self.mw = QtGui.QMainWindow()
        self.mw.resize(800,800)
        self.view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
        self.mw.setCentralWidget(self.view)
        self.mw.show()
        self.mw.setWindowTitle('StarTracker')

        self.w1 = self.view.addPlot(enableMouse = False)

        self.t1 = pg.TextItem()
        self.w1.addItem(self.t1)
        self.t1.setPos(10,10)

        self.t2 = pg.TextItem()
        self.t2.setText("")
        self.w1.addItem(self.t2)


        self.s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None))
        self.s2 = pg.PlotDataItem() #pg.ScatterPlotItem(size=10, pen=pg.mkPen("b", width=3))
        self.w1.setRange(xRange=[0,360], yRange=[0,90])
        self.w1.addItem(self.s1)
        self.w1.addItem(self.s2)


        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update)
        self.timer.start()


        # UI window
        self.inputApp = QtGui.QApplication([])

        ## Define a top-level widget to hold everything
        self.inputW = QtGui.QWidget()

        ## Create some widgets to be placed inside
        self.btn1 = QtGui.QPushButton('Test error')
        self.btn1.clicked.connect(self.btn1state)
        self.btn1.setCheckable(True)
        self.btn2 = QtGui.QPushButton('Remove zeroing')
        self.btn2.clicked.connect(self.btn2state)
        self.btn2.setCheckable(True)
        self.btn3 = QtGui.QPushButton('Accurately zero')
        self.btn3.clicked.connect(self.btn3state)
        self.btn3.setCheckable(True)
        self.btn4 = QtGui.QPushButton('Enable eyepiece (reduce FOV)')
        self.btn4.clicked.connect(self.btn4state)
        self.btn4.setCheckable(True)
        self.btn5 = QtGui.QPushButton('Enable large FOV')
        self.btn5.clicked.connect(self.btn5state)
        self.btn5.setCheckable(True)
        self.btn6 = QtGui.QPushButton('Calibrate Kalman Filter')
        self.btn6.clicked.connect(self.btn6state)
        self.btn6.setCheckable(True)
        self.btn7 = QtGui.QPushButton('Activate Kalman Filter')
        self.btn7.clicked.connect(self.btn7state)
        self.btn7.setCheckable(True)
        self.btn7.toggle()
        self.btn8 = QtGui.QPushButton('Enter text command')
        self.btn8.clicked.connect(self.btn8state)
        self.btn8.setCheckable(True)



        self.text1 = QtGui.QLineEdit('moon/skyfield') #11767/star/10/loves.spenders.opened #moon/skyfield/60/loves.spenders.opened
        self.text1.textChanged.connect(self.text1changed)
        # self.text1.editingFinished.connect(self.enterPress)

        ## Create a grid layout to manage the widgets size and position
        self.layout = QtGui.QGridLayout()
        self.inputW.setLayout(self.layout)

        ## Add widgets to the layout in their proper positions
        self.layout.addWidget(self.btn1, 1, 0)
        self.layout.addWidget(self.btn2, 2, 0)
        self.layout.addWidget(self.btn3, 3, 0)
        self.layout.addWidget(self.btn4, 4, 0)
        self.layout.addWidget(self.btn5, 5, 0)
        self.layout.addWidget(self.btn6, 6, 0)
        self.layout.addWidget(self.btn7, 7, 0)
        self.layout.addWidget(self.btn8, 8, 0)   # button goes in upper-left
        self.layout.addWidget(self.text1, 9, 0)   # text edit goes in middle-left

        ## Display the widget as a new window
        self.inputW.show()

        self.run()



    def update(self):
        # print(self.oQ.qsize())
        self.oData = self.oQ.get()
        self.oQ.queue.clear()

        self.aData = self.aQ.get()
        self.aQ.queue.clear()

        #print("Pre-data: " + str(self.oData))

        # aX = self.aData[0]
        # aZ = self.aData[2]
        # aY = self.aData[1]
        #
        # gaX = self.aData[3]
        # gaZ = self.aData[4]
        # gaY = self.aData[5]
        #
        # gX = gaX -
        # gY = gaY - aY
        # print(gY)
        # yA = math.asin(gY/9.807)

        if self.calibrating:
            if self.measurements[0][0] == 0:
                #print("Compiling training data")
                self.measurements = np.append(self.measurements, [self.oData], axis=0)
                self.measurements = np.delete(self.measurements, 0, 0)
            else:
                print("Training and initialising Kalman filter")
                self.initStateMu = [self.measurements[0, 0],0,self.measurements[0, 1],0]
                self.trainKalman()
                self.calibrating = False
                self.kalmanActive = True
        else:
            pass

        if self.kalmanActive:
            print("Kalman filter active")
            self.xNow, self.pNow = self.kf.filter_update(filtered_state_mean = self.xNow,
                                                          filtered_state_covariance = self.pNow,
                                                          observation = self.oData)

            #print("Post-data: " + str(self.xNow))

            zO = self.xNow[0]
            yO = self.xNow[2]
        else:
            zO = self.oData[0]
            yO = self.oData[1]




        # print("zO: " + str(zO) + " yO: " + str(yO) + "yA: " + str(yA))

        ### THIS IS sAVGOL FILTERING
        # self.movingAverageZ = np.append(self.movingAverageZ, [[z]], axis=0)
        # self.movingAverageY = np.append(self.movingAverageY, [[y]], axis=0)
        #
        # #print(self.movingAverage)
        #
        # if self.noiseRemoval:
        #     noiseRedArrZ = scipy.signal.savgol_filter(self.movingAverageZ, 9, 1, axis=0)
        #     noiseRedArrY = scipy.signal.savgol_filter(self.movingAverageY, 9, 1, axis=0)
        #     # print(noiseRedArr)
        #     z = np.average(noiseRedArrZ, axis=0)
        #     y = np.average(noiseRedArrY, axis=0)
        #     #self.oData = np.average(noiseRedArr, axis=0)
        #
        # else:
        #     #self.oData = np.average(self.movingAverage, axis=0)
        #     z = np.average(self.movingAverageZ, axis=0)
        #     y = np.average(self.movingAverageY, axis=0)
        #     #print(self.movingAverage)
        #
        #
        # self.movingAverageZ = np.delete(self.movingAverageZ, 0, 0)
        # self.movingAverageY = np.delete(self.movingAverageY, 0, 0)

        # z = self.oData[0]
        # y = self.oData[1]

        self.z = zO #[0]
        self.y = yO #[0]
        # print(type(self.z))
        #
        # print(self.z)
        # print(type(self.z))

        if self.targetSet:
            self.targetZ, self.targetY = self.calcAzAlt(self.ts.now())
        else:
            pass

        if self.moveText:
            self.textPos = [self.targetZ-0.25, self.targetY-0.20]
        else:
            pass

        if self.testErr:
            self.calcError()
        else:
            pass


        self.s1.setData([360-self.z+self.initZ,self.targetZ], [self.y+self.initY,self.targetY], brush=[pg.mkBrush(252,61,33),pg.mkBrush(218,200,36)], symbol=["+", "o"], size=[30,4])

        self.t1.setText(text = "Scope\nAz: " + str(round(360-self.z,2)) + "\nAlt: " + str(round(self.y,2)))
        self.t2.setText(text = self.target + "\nAz: " + str(round(self.targetZ, 2)) + "\nAlt: " + str(round(self.targetY, 2)))

        self.t1.setPos(self.textPos[0], self.textPos[1])
        self.t2.setPos(self.targetZ,self.targetY)

        if self.moveFOV:
            self.w1.setRange(xRange=[self.targetZ-0.25,self.targetZ+0.25], yRange=[self.targetY-0.25,self.targetY+0.25])
        else:
            pass

        self.w1.addItem(self.s1)
        self.w1.addItem(self.t1)
        self.w1.addItem(self.t2)



    def run(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        ## Start the UI window Qt event loop
        self.inputApp.exec_()



    def calcError(self):

        diff =  time.time() - self.oldTime
        print(diff)
        if diff > 300:
            self.ErrZ = self.targetZ - (360-self.z+self.initZ)
            self.ErrY = self.targetY - (self.y+self.initY)
            self.testErr = False
        else:
            pass


    def trainKalman(self):
        self.kf = KalmanFilter(transition_matrices = self.transMatrix,
                  observation_matrices = self.obsMatrix,
                  initial_state_mean = self.initStateMu,
                  em_vars=['transition_covariance', 'initial_state_covariance'])

        self.kf = self.kf.em(self.measurements, n_iter=5)
        self.filterStateMu, self.filterStateCov = self.kf.filter(self.measurements)

        self.kf = KalmanFilter(transition_matrices = self.transMatrix,
                  observation_matrices = self.obsMatrix,
                  initial_state_mean = self.initStateMu,
                  observation_covariance=10*self.kf.observation_covariance,
                  em_vars=['transition_covariance', 'initial_state_covariance'])

        self.kf = self.kf.em(self.measurements, n_iter=5)
        self.filterStateMu, self.filterStateCov = self.kf.filter(self.measurements)

        self.xNow = self.filterStateMu[-1,:]
        self.pNow = self.filterStateCov[-1,:]




    def btn1state(self):
        if self.btn1.isChecked():
            self.oldTime = time.time()
            self.testErr = True



    def btn2state(self):
        if self.btn2.isChecked():
            self.initZ = 0
            self.initY = 0
            print(str(self.ErrZ) + str(self.ErrY))



    def btn3state(self):
        if self.btn3.isChecked():
            self.initZ = self.targetZ - (360-self.z)
            self.initY = self.targetY - self.y



    def btn4state(self):
        if self.btn4.isChecked():
            self.moveFOV = True
            self.FOVy = 0.5
            self.FOVx = 0.5
            self.w1.setRange(xRange=[(360-self.z)-0.25,(360-self.z)+0.25], yRange=[self.y-0.25,self.y+0.25])
            self.moveText = True



    def btn5state(self):
        if self.btn5.isChecked():
            self.moveFOV = False
            self.FOVy = 90
            self.FOVx = 360
            self.w1.setRange(xRange=[0,360], yRange=[0,90])
            self.moveText = False
            # self.t1.setPos(10,10)
            self.textPos = [10,10]
            #self.textPos = [0,0]

    def btn6state(self):
        if self.btn6.isChecked():
            print("Prepare to calibrate filter in:")
            for i in range(5):
                print(5-(i))
                time.sleep(1)
            print("Calibrating Kalman Filter")
            self.calibrating = True
            # self.noiseRemoval = True
        # else:
        #     print("Noise removal disabled")
        #     self.noiseRemoval = False

    def btn7state(self):
        if self.btn7.isChecked():
            print("Activating Kalman Filter")
            self.kalmanActive = True
        else:
            print("Deactivating Kalman Filter")
            self.kalmanActive = False

    def btn8state(self):
        if self.btn7.isChecked():
            print("Processing user input")
            self.configureInfo(self.text)


    def text1changed(self, text):
        self.text = text



    # def enterPress(self):
    #     self.input = self.text
    #     self.configureInfo(self.input)
    #
    #     print(self.input)



    def configureInfo(self, input):
        # try:
        target, type = input.split("/")

        self.target = target
        self.type = type

        print("Target set to: " + target + "(" + type + ")")

        self.lat = "51.989772 N"
        self.lng = "0.213651 E"

        #Confirm with message to user
        print("Latitude: " + self.lat + "\nLongitude: " + self.lng)

        self.location = self.earth + Topos(str(self.lat), str(self.lng))

        #Drawing trace of objects daily motion
        # trace = np.empty((1,2))
        #
        # if self.type == "skyfield":
        #     try:
        #         val = int(self.target)
        #         target = self.data[int(self.target)]
        #     except ValueError:
        #         target = self.data[str(self.target)]
        #
        # elif self.type == "star":
        #     target = int(self.target)
        #     target = Star.from_dataframe(self.df.loc[target])
        #
        # now = datetime.datetime.now()
        #
        # t0 = self.ts.utc(now.year, now.month, now.day-1)
        # t1 = self.ts.utc(now.year, now.month, now.day+1)
        # f = almanac.risings_and_settings(self.data, target, Topos(str(self.lat), str(self.lng)))
        # t, y = almanac.find_discrete(t0, t1, f)
        #
        # for ti, yi in zip(t, y):
        #     if yi:
        #         riseTime = ti.utc_datetime()
        #     else:
        #         setTime = ti.utc_datetime()
        #     # print(ti.utc_datetime(), 'Rise' if yi else 'Set')
        #
        # t = riseTime
        # while t < setTime:
        #     pos = self.calcAzAlt(self.ts.utc(t))
        #     # print(np.shape([pos]))
        #     # print(np.shape(trace))
        #     trace = np.append(trace, [pos], axis=0)
        #     t += datetime.timedelta(minutes=1)#hours = 1)
        #
        # #print(trace)
        #
        # self.w1.removeItem(self.s2)
        # self.s2 = pg.PlotDataItem(trace, pen=pg.mkPen("b", width=0.5))
        # self.w1.addItem(self.s2)


        self.targetSet = True

        # except Exception as e:
        #     print("Error: " + str(e))
        #     print("Probably something wrong with your input, try again")



    def calcAzAlt(self, time):

        t = time

        if self.type == "skyfield":
            try:
                val = int(self.target)
                target = self.data[int(self.target)]
            except ValueError:
                target = self.data[str(self.target)]

            astro = self.location.at(t).observe(target)
        elif self.type == "star":
            target = int(self.target)
            target = Star.from_dataframe(self.df.loc[target])
            astro = self.location.at(t).observe(target)

        #Compute altitude and azimuth
        app = astro.apparent()
        alt, az, distance = app.altaz()

        # print([az.degrees,alt.degrees])

        return [az.degrees,alt.degrees]




class CenteredArrowItem(pg.ArrowItem):
    def setData(self, x, y, angle):
        self.opts['angle'] = angle
        opt = dict([(k, self.opts[k]) for k in ['headLen', 'tipAngle', 'baseAngle', 'tailLen', 'tailWidth']])
        path = pg.functions.makeArrowPath(**opt)
        b = path.boundingRect()
        tr = pg.QtGui.QTransform()
        tr.rotate(angle)
        tr.translate(-b.x() - b.width() / 2, -b.y() - b.height() / 2)
        self.path = tr.map(path)
        self.setPath(self.path)
        self.setPos(x, y)
