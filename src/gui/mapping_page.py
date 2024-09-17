from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QHeaderView, QSplitter
from PyQt5.QtWidgets import QVBoxLayout, QLabel,QLineEdit ,QTableWidget,QTableWidgetItem,  QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pyqtgraph as pg
import numpy as np
from pathlib import Path
from scipy.io.wavfile import write
import soundfile as sf
import os
from src.gui.utils import setAllItemsToReadOnlyInLayout, getBackgroundColor, getTextColor, tableHeaderStyle

import src.config as config
import sys
from PyQt5.QtWidgets import QPushButton

class SaveBidsFiles(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    def __init__(self, eegAudioData, subjectId, sessionId, runId, taskName):
        super().__init__()
        self.eegAudioData = eegAudioData
        self.subjecId = subjectId
        self.sessionId = sessionId
        self.runId = runId
        self.taskName = taskName

    def run(self):
        try:
            self.eegAudioData.setUpBidsInfo(self.subjecId, self.sessionId, self.runId, self.taskName)
            self.eegAudioData.createAnnotations()
            self.eegAudioData.createEDFFile()
            self.eegAudioData.createAudio()
            self.eegAudioData.createEventsFileForAudio()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))



class EegAudioMappingWindow(QMainWindow):
    aboutToClose = pyqtSignal()

    def __init__(self, eegAudioData):
        super().__init__()
        self.eegAudioData = eegAudioData
        self.audioSamplingRate = 44100 #self.eegAudioData.audioData.samplingFrequency
        self.eegSamplingRate = self.eegAudioData.eegData.samplingFrequency

        self.setWindowTitle('Mapping EEG and AUDIO Data')
        self.setGeometry(500, 300, 1300, 300)
        self.setWindowIcon(QIcon(config.windowIconPath)) 

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainlayout = QHBoxLayout()
        centralWidget.setLayout(self.mainlayout)

        mappingInfoLayout = self.setUpMappingInfoLayout()
        plotsAndOtherLayout = self.setUpPlotsAndOtherLayout()
        
        mappingInfoLayoutWidget = QWidget()
        plotsAndOtherLayoutWidget = QWidget()

        mappingInfoLayoutWidget.setLayout(mappingInfoLayout)
        plotsAndOtherLayoutWidget.setLayout(plotsAndOtherLayout)

        self.mainlayout.addWidget(mappingInfoLayoutWidget)
        self.mainlayout.addWidget(plotsAndOtherLayoutWidget)

        self.mainlayout.setStretch(0, 7)
        self.mainlayout.setStretch(1, 3)

        self.updateMappingInfoTable()
        self.setUpConnectionSignals()
        self.updateEventInfoOnPage(0)

        self.timer = QTimer()
        self.eegTimer = QTimer()
        self.timer.timeout.connect(self.updateAudioPlot)
        self.eegTimer.timeout.connect(self.updateEEGPlot)
        self.audioIndex = 0
        self.eegIndex = 0

        self.mediaPlayer = QMediaPlayer()
        self.setEEGStyles()

    def setUpConnectionSignals(self):
        self.createBidsFilesButton.clicked.connect(self.createBidsFiles)
        self.synchronizedEventsTable.cellClicked.connect(self.updateEventInfoOnPage)
        self.playButton.clicked.connect(self.playAudio)
        self.pauseButton.clicked.connect(self.pauseAudio)
        self.nextButton.clicked.connect(self.nextEvent)
        self.previousButton.clicked.connect(self.previousEvent)

    ##########################################################################################################
    ############################################ MAPPING TABLE LAYOUT ########################################
    ##########################################################################################################

    def setUpMappingInfoLayout(self):
        layout = QVBoxLayout()

        self.synchronizedEventsTable = QTableWidget()
        self.synchronizedEventsTable.setColumnCount(8)
        self.synchronizedEventsTable.setHorizontalHeaderLabels(
            ['Block', 'TrialType', 'Word', 'EegStart', 'AudioStart', 'Duration', 'eegStartIndex', 'AudioStartIndex', 'Eeg Start Time', 'Audio Start Time']
        )
        self.synchronizedEventsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.synchronizedEventsTable.horizontalHeader().setStyleSheet(tableHeaderStyle)

        layout.addWidget(self.synchronizedEventsTable)

        return layout
    
    ##########################################################################################################
    ########################################## PLOTS AND OTHER LAYOUT ########################################
    ##########################################################################################################
    
    def setUpPlotsAndOtherLayout(self):
        layout = QVBoxLayout()
        plotsLayoutWidget = self.setupPlotsWidget()
        self.blockInfoLayout = self.setUpBlockInfoLayout()
        plotsButtonsLayout = self.setUpPlotsButtonsLayout()
        bidsInfolayout = self.setUpBidsInfoLayout()
           
        layout.addWidget(plotsLayoutWidget)
        layout.addLayout(plotsButtonsLayout)
        layout.addLayout(bidsInfolayout)  
        self.createBidsFilesButton = QPushButton('Create BIDS Files')
        layout.addWidget(self.createBidsFilesButton)
        return layout 
    
    def setUpBidsInfoLayout(self):
        layout = QHBoxLayout()
        self.subjectIdTextBox = QLineEdit()
        self.sessionIdTextBox = QLineEdit()
        self.runIdTextBox  = QLineEdit()
        self.taskNameTextBox = QLineEdit()
        layout.addWidget(QLabel('Subject ID:'))
        layout.addWidget(self.subjectIdTextBox)
        layout.addWidget(QLabel('Session ID:'))
        layout.addWidget(self.sessionIdTextBox)
        layout.addWidget(QLabel('Run ID:'))
        layout.addWidget(self.runIdTextBox)
        layout.addWidget(QLabel('Task Name:'))
        layout.addWidget(self.taskNameTextBox)
        return layout
    
    def setUpBlockInfoLayout(self):
        layout = QVBoxLayout()

        self.blockTextBox = QLineEdit()
        self.trialTypeTextBox = QLineEdit()
        self.wordTextBox = QLineEdit()
        self.eegStartTextBox = QLineEdit()
        self.audioStartTextBox = QLineEdit()
        self.durationTextBox = QLineEdit()
        self.eegStartIndexTextBox = QLineEdit()
        self.audioStartIndexTextBox = QLineEdit()

        blockInfolayout1 = QHBoxLayout()
        blockInfolayout1.addWidget(QLabel('Block:'))
        blockInfolayout1.addWidget(self.blockTextBox)
        blockInfolayout1.addWidget(QLabel('TrialType:'))
        blockInfolayout1.addWidget(self.trialTypeTextBox)
        blockInfolayout1.addWidget(QLabel('Word:'))
        blockInfolayout1.addWidget(self.wordTextBox)
        blockInfolayout1.addWidget(QLabel('EegStart:'))
        blockInfolayout1.addWidget(self.eegStartTextBox)
        setAllItemsToReadOnlyInLayout(blockInfolayout1)

        blockInfolayout2 = QHBoxLayout()
        blockInfolayout2.addWidget(QLabel('AudioStart:'))
        blockInfolayout2.addWidget(self.audioStartTextBox)
        blockInfolayout2.addWidget(QLabel('Duration:'))
        blockInfolayout2.addWidget(self.durationTextBox)
        blockInfolayout2.addWidget(QLabel('EegStartIndex:'))
        blockInfolayout2.addWidget(self.eegStartIndexTextBox)
        blockInfolayout2.addWidget(QLabel('AudioStartIndex:'))
        blockInfolayout2.addWidget(self.audioStartIndexTextBox)
        setAllItemsToReadOnlyInLayout(blockInfolayout2)

        layout.addLayout(blockInfolayout1)
        layout.addLayout(blockInfolayout2)

        return layout
    
    def setUpPlotsButtonsLayout(self):
        layout = QVBoxLayout()

        buttonsLayout = QHBoxLayout()
        self.playButton = QPushButton('Play')
        self.pauseButton = QPushButton('Pause')
        self.nextButton = QPushButton('Next')
        self.previousButton = QPushButton('Previous')

        buttonsLayout.addWidget(self.previousButton)
        buttonsLayout.addWidget(self.playButton)
        buttonsLayout.addWidget(self.pauseButton)
        buttonsLayout.addWidget(self.nextButton)

        blockInfoLayout = self.setUpBlockInfoLayout()
        
        layout.addLayout(buttonsLayout)
        layout.addLayout(blockInfoLayout)

        return layout

    def setupPlotsWidget(self):
        plotsLayout = QHBoxLayout()
        widget = QWidget()  
        widget.setLayout(plotsLayout)  
      
        self.eegPlotWidget = self.setupEEGPlotWidget()
        self.audioPlotWidget = self.setupAudioPlotWidget()

        plotsLayout.addWidget(self.eegPlotWidget)
        plotsLayout.addWidget(self.audioPlotWidget)

        return widget 
 
    def setupAudioPlotWidget(self):
        audioPlotWidget = pg.PlotWidget(title="Audio Visualizer")
        audioPlotWidget.setBackground('w')
        audioPlotWidget.getPlotItem().showGrid(True, True)
        self.audioPlotDataItem = audioPlotWidget.plot(pen='red')
        
        return audioPlotWidget

    def setupEEGPlotWidget(self):
        eegplotWidget = pg.PlotWidget(title="EEG Activity")
        #eegplotWidget.plot([0, 1, 2, 3], [10, 20, 15, 30])
        eegplotWidget.setBackground('w')
        eegplotWidget.getPlotItem().showGrid(True, True)
        self.eegPlotDataItem = eegplotWidget.plot(pen='b')
        
        return eegplotWidget
    
    ##########################################################################################################
    ######################################### MAPPING LAYOUT FUNCTIONS #######################################
    ##########################################################################################################
    

    def updateMappingInfoTable(self):

        data = self.eegAudioData.synchronizedEvents
        self.synchronizedEventsTable.setRowCount(len(data))
        
        for rowIndex, event in enumerate(data):
            self.synchronizedEventsTable.setItem(rowIndex, 0, QTableWidgetItem(str(event[8])))    
            self.synchronizedEventsTable.setItem(rowIndex, 1, QTableWidgetItem(str(event[9])))    
            self.synchronizedEventsTable.setItem(rowIndex, 2, QTableWidgetItem(str(event[10])))    
            self.synchronizedEventsTable.setItem(rowIndex, 3, QTableWidgetItem(str(event[0])))    
            self.synchronizedEventsTable.setItem(rowIndex, 4, QTableWidgetItem(str(event[3])))    
            self.synchronizedEventsTable.setItem(rowIndex, 5, QTableWidgetItem(str(event[1])))    
            self.synchronizedEventsTable.setItem(rowIndex, 6, QTableWidgetItem(str(event[2])))    
            self.synchronizedEventsTable.setItem(rowIndex, 7, QTableWidgetItem(str(event[5])))
            self.synchronizedEventsTable.setItem(rowIndex, 8, QTableWidgetItem(str(event[6])))
            self.synchronizedEventsTable.setItem(rowIndex, 9, QTableWidgetItem(str(event[7])))
            

            backgroundColor = getBackgroundColor(event[8])
            textColor = getTextColor(event[9])   

            for col in range(self.synchronizedEventsTable.columnCount()):
                item = self.synchronizedEventsTable.item(rowIndex, col)
                if item:
                    item.setBackground(backgroundColor)
                    item.setForeground(textColor)           

    def setUpBidsInfo(self):
        self.subjecId = self.subjectIdTextBox.text()
        self.sessionId = self.sessionIdTextBox.text()  
        self.runId = self.runIdTextBox.text()
        self.taskName = self.taskNameTextBox.text()     

    def createBidsFiles(self):
        print('Creating BIDS Files Clicked')
        self.setUpBidsInfo()
        if all([self.subjecId, self.sessionId, self.runId, self.taskName]):
            self.saveMessageBox = self.showWaitingMessage('Saving BIDS Files')
            self.saveMessageBox.setWindowTitle('Saving')
            self.saveBidsFiles = SaveBidsFiles(self.eegAudioData, self.subjecId, self.sessionId, self.runId, self.taskName) 
            self.saveBidsFiles.finished.connect(self.onSaveFinished)
            self.saveBidsFiles.error.connect(self.onSaveError)
            self.saveBidsFiles.start()
            self.saveMes
        else:
            QMessageBox.warning(self, 'Error', 'Please enter all the required fields')


    ##########################################################################################################
    ############################################ BIDS INFO FUNCTIONS #########################################
    ##########################################################################################################
    
    def updateEventInfoOnPage(self, eventIndex):
        eventData = self.extractRowFromTable(eventIndex)
        self.blockTextBox.setText(str(eventData[0]))
        self.trialTypeTextBox.setText(str(eventData[1]))
        self.wordTextBox.setText(str(eventData[2]))
        self.eegStartTextBox.setText(eventData[3].split('.')[0] +'.' +  eventData[3].split('.')[1][:2])
        self.audioStartTextBox.setText(eventData[4].split('.')[0] + '.' + eventData[4].split('.')[1][:2])
        self.durationTextBox.setText(eventData[5].split('.')[0] + '.' + eventData[5].split('.')[1][:2])
        self.eegStartIndexTextBox.setText(str(eventData[6]))
        self.audioStartIndexTextBox.setText(str(eventData[7]))
        self.audioStartIndex = int(eventData[7])
        self.audioDuration = float(eventData[5])
        self.eegStartIndex = int(eventData[6])

    def extractRowFromTable(self, rowIndex):
        rowData = []
        for colIndex in range(self.synchronizedEventsTable.columnCount()):
            item = self.synchronizedEventsTable.item(rowIndex, colIndex)
            if item:
                rowData.append(item.text())
            else:
                rowData.append('')  
        return rowData
    
    ##########################################################################################################
    ##################################### PLAY AND OTHER BUTTON FUNCTIONS ####################################
    ##########################################################################################################

    def playAudio(self):
        os.makedirs(config.audioPlayerDir, exist_ok=True)
        self.extractAudioForPlay()
        self.extractEEGForPlay()

    def pauseAudio(self):
        self.mediaPlayer.stop()
        self.timer.stop()   
        self.eegTimer.stop()

    def nextEvent(self):
        currentRow = self.synchronizedEventsTable.currentRow()
        if currentRow < self.synchronizedEventsTable.rowCount() - 1:
            self.synchronizedEventsTable.selectRow(currentRow + 1)
            self.updateEventInfoOnPage(currentRow + 1)
    
    def previousEvent(self):
        currentRow = self.synchronizedEventsTable.currentRow()
        if currentRow > 0:
            self.synchronizedEventsTable.selectRow(currentRow - 1)
            self.updateEventInfoOnPage(currentRow - 1)

    def extractAudioForPlay(self):
        self.audioEndIndex = self.audioStartIndex + int(self.audioDuration * self.audioSamplingRate)
        self.audioSampleData = self.eegAudioData.audioData.audio[self.audioStartIndex: self.audioEndIndex].reshape(-1, 1)
        name = f'{self.audioStartIndex}.wav'
        filePathWithName = Path(config.audioPlayerDir, name)
        print(filePathWithName)
        if not os.path.exists(filePathWithName):
            write(filePathWithName, int(self.eegAudioData.audioData.samplingFrequency), self.audioSampleData)
        self.audioData, self.sampleRate = sf.read(filePathWithName, dtype='int16')
        self.audioIndex = 0
        mediaContent = QMediaContent(QUrl.fromLocalFile(str(filePathWithName)))
        self.mediaPlayer.setMedia(mediaContent)
        self.mediaPlayer.play()
        self.timer.start(30)

    def extractEEGForPlay(self):
        self.eegEndIndex = self.eegStartIndex + int(self.audioDuration * self.eegSamplingRate)
        self.eegSampleData = self.eegAudioData.eegData.eegRawData[self.eegStartIndex: self.eegEndIndex]
        print(self.eegSampleData.sahpe)
        self.eegTimer.start(30)

    def updateAudioPlot(self):
        if self.audioSampleData is not None:
            chunkSize = 1350
            endIndex = self.audioIndex + chunkSize
            if endIndex >= len(self.audioSampleData):
                endIndex = len(self.audioSampleData)
                self.timer.stop()
            dataChunk = self.audioData[self.audioIndex:endIndex]
            self.audioPlotDataItem.setData(dataChunk)
            self.audioIndex = endIndex
    
    def updateEEGPlot(self):
        if self.eegSampleData is not None:
            chunkSize = 15
            endIndex = self.eegIndex + chunkSize
            if endIndex >= len(self.eegSampleData):
                endIndex = len(self.eegSampleData)
                self.eegTimer.stop()
            dataChunk = self.eegSampleData[self.eegIndex:endIndex]
            self.eegPlotDataItem.setData(dataChunk)
            self.eegIndex = endIndex
    
    ##########################################################################################################
    ############################################ COMMON FUNCTIONS #########################################
    ##########################################################################################################

    def showWaitingMessage(self, message):
        waitingMsgBox = QMessageBox()
        waitingMsgBox.setText(message)
        waitingMsgBox.setStandardButtons(QMessageBox.NoButton)
        waitingMsgBox.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waitingMsgBox.setWindowTitle('Processing')
        waitingMsgBox.show()
        QApplication.processEvents()
        return waitingMsgBox
    
    def onSaveFinished(self):
        self.saveMessageBox.accept()
        QMessageBox.information(self, 'BIDS Files Created', 'Finished')

    def onSaveError(self):
        self.saveMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed")
        return 'Error'
    
    def setEEGStyles(self):
        self.setStyleSheet('''
            QWidget {
                border: 2px solid #d3d3d3; /* Lighter gray border for subtle separation */
                border-radius: 8px;
                padding: 12px;
                background-color: #f7f7f7; /* Very light gray background for a clean look */
            }
            QLabel {
                font-size: 14px;
                padding: 5px 0;
                color: #2c3e50; /* Darker blue-gray for a professional tone */
            }
            QLineEdit, QListWidget {
                padding: 6px;
                border: 1px solid #5dade2; /* Soft blue border for input fields */
                border-radius: 6px;
                font-weight: bold;
                background-color: #ecf0f1; /* Light gray background for fields */
                color: #2c3e50; /* Dark text for readability */
            }
            QPushButton {
                padding: 8px 14px;
                background-color: #5dade2; /* Softer, muted blue for buttons */
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db; /* Slightly darker blue on hover for interaction feedback */
            }
            /* Styling for header */
            QLabel#header {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                background-color: #34495e; /* Muted dark blue-gray header for a sleek look */
                padding: 12px;
                border-radius: 8px;
                text-align: center;
            }
            QTableWidget {
                border: 1px solid #d3d3d3; /* Subtle border around table */
                border-radius: 1px;
                padding: 0px;
                font-weight: bold;
                font-size: 16px;
                background-color: #ffffff; /* White table background for clarity */
            }
            QHeaderView::section {
                background-color: #5dade2; /* Muted blue for table headers */
                color: white;
                font-weight: bold;
                padding: 6px;
                height: 50px;
                border: 1px solid #bdc3c7; /* Light border for section separation */
            }
        ''')
