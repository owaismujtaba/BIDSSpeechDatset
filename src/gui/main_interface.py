from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView
from PyQt5.QtWidgets import QPushButton, QListWidget, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QBrush, QFont

from src.utils import unixToRealTime
from src.eeg_data_utils import EegDataProcessor
from src.audio_data_utils import AudioDataProcessor
from src.gui.utils import  getFileNameFromPath, getBackgroundColor, getTextColor
from src.eeg_audio_data import EegAudioDataProcessor
from src.gui.mapping_page import EegAudioMappingWindow
import src.config as config

class LoadEegThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath

    def run(self):
        try:
            eegData = EegDataProcessor(self.filePath)
            self.finished.emit(eegData)
        except Exception as e:
            self.error.emit(str(e))


class LoadAudioThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath

    def run(self):
        try:
            audioData = AudioDataProcessor(self.filePath)
            self.finished.emit(audioData)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('EEG and Audio Annotator')
        self.setGeometry(300, 100, 1200, 600)
        self.setWindowIcon(QIcon(config.windowIconPath)) 


        self.eegData = None
        self.audioData = None
        self.audioFilepath = None
        self.eegFilepath = None
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        mainlayout = QVBoxLayout()
        centralWidget.setLayout(mainlayout)
        
        # Set up EEG and Audio Layouts
        layout = QHBoxLayout()
        self.eegLayout = self.setupEEGLayout()
        self.audioLayout = self.setupAudioLayout()

        layout.addLayout(self.eegLayout)
        layout.addLayout(self.audioLayout)
        

        mainlayout.addLayout(layout)
        self.synchronizeEegAudioButton = QPushButton('Synchronize EEG and Audio Data')
        mainlayout.addWidget(self.synchronizeEegAudioButton)

        self.setupConnectionSignals()

    def setupConnectionSignals(self):
        self.eegSelectFileButton.clicked.connect(self.openFileExplorer)
        self.eegLoadFileButton.clicked.connect(self.loadEegFile)
        self.eegAddAllChannelButton.clicked.connect(self.eegAddAllChannelsToSelectedChannelsList)
        self.eegRemoveAllChannelButton.clicked.connect(self.eegRemoveAllChannelsFromSelectedList)   
        self.eegAddChannelButton.clicked.connect(self.eegAddChannelToSelectedChannelsList)  
        self.eegRemoveChannelButton.clicked.connect(self.eegRemoveChannelFromSelectedChannelsList)
        self.eegVisualizeButton.clicked.connect(self.eegVisualizeSelectedChannels)

        self.audioSelectFileButton.clicked.connect(self.openFileExplorer)
        self.audioLoadFileButton.clicked.connect(self.loadAudioFile)
        self.updateTimeDifferenceButton.clicked.connect(self.updateAudioTimeDifference)
        
        self.synchronizeEegAudioButton.clicked.connect(self.openSynchronizationPage)


    ##########################################################################################################
    ######################################## EEG LAYOUT FUNCTIONS ############################################
    ##########################################################################################################

    
    def loadEegFile(self):
        if self.eegFilepath:
            
            self.waitingMessgaeBox = self.showWaitingMessage('Loadinf EEG Data')
            self.loadEegThread = LoadEegThread(self.eegFilepath)
            self.loadEegThread.finished.connect(self.onLoadEegFinished)
            self.loadEegThread.error.connect(self.onLoadError)
            self.loadEegThread.start()

    def onLoadEegFinished(self, eegData):
        self.eegData = eegData
        self.updateEegInfoOnPage()
        self.waitingMessgaeBox.accept()
    
    def updateEegInfoOnPage(self):
        self.eegSamplingFreqText.setText(str(self.eegData.samplingFrequency))
        self.eegDurationText.setText(str(self.eegData.duration))
        self.eegStartTimeText.setText(str(unixToRealTime(self.eegData.timeStamps[0])))
        self.eegEndTimeText.setText(str(unixToRealTime(self.eegData.timeStamps[-1])))
        self.eegAvailableChannelsList.addItems(self.eegData.channelNames)
        self.addEegDataToEventsTable()

    def addEegDataToEventsTable(self):
        data = self.eegData.eegEvents
        nRows = len(data)
        self.eegEventsTable.setRowCount(nRows)
        for rowIndex in range(nRows):
            for colIndex in range(len(data[0])):
                item = QTableWidgetItem(str(data[rowIndex][colIndex]))
                item.setBackground(QBrush(getBackgroundColor(data[rowIndex][1])))
                item.setForeground(QBrush(getTextColor(data[rowIndex][0])))
                self.eegEventsTable.setItem(rowIndex, colIndex, item)

    def eegVisualizeSelectedChannels(self):
        if self.eegData:
            selectedChannels = [self.eegSelectedChannelsList.item(i).text() for i in range(self.eegSelectedChannelsList.count())]
            if not selectedChannels:
                QMessageBox.warning(self, "No Channels Selected", "Please select at least one channel to visualize.")
                return
            plotData = self.eegData.rawData.copy()
            eegDataSelectedChannels = plotData.pick(selectedChannels)
            eegDataSelectedChannels.plot(duration=60, show_options=True)

    def eegRemoveAllChannelsFromSelectedList(self):
        while self.eegSelectedChannelsList.count() > 0:
            item = self.eegSelectedChannelsList.takeItem(0)
            self.eegAvailableChannelsList.addItem(item.text())

    def eegAddAllChannelsToSelectedChannelsList(self):
        while self.eegAvailableChannelsList.count() > 0:
            item = self.eegAvailableChannelsList.takeItem(0)
            self.eegSelectedChannelsList.addItem(item.text())

    def eegRemoveChannelFromSelectedChannelsList(self):
        selectedChannels = self.eegSelectedChannelsList.selectedItems()
        for channel in selectedChannels:
            self.eegAvailableChannelsList.addItem(channel.text())
            self.eegSelectedChannelsList.takeItem(self.eegSelectedChannelsList.row(channel))
    
    def eegAddChannelToSelectedChannelsList(self):
        selectedChannels = self.eegAvailableChannelsList.selectedItems()
        for channel in selectedChannels:
            self.eegSelectedChannelsList.addItem(channel.text())
            self.eegAvailableChannelsList.takeItem(self.eegAvailableChannelsList.row(channel))
    
    ##########################################################################################################
    ######################################## COMMON FUNCTIONS ################################################
    ##########################################################################################################
    
    def onLoadError(self, errorMessage):
        self.waitingMessageBox.accept()
        QMessageBox.critical(self, "Error", f"Failed to load EEG data: {errorMessage}")

    def openFileExplorer(self):
        fileDialog = QFileDialog()
        filePath, _ = fileDialog.getOpenFileName(self, "Open EDF.XDF File", "", "EEG Files (*.edf *.xdf);;All Files (*)")
        if filePath.endswith('.edf'):
            self.eegFilepath = filePath
            file = getFileNameFromPath(filePath)
            file = 'File:: ' + file
            self.eegFileNameTextbox.setText(file)
        elif  filePath.endswith('.xdf'):
            self.audioFilepath = filePath
            file = getFileNameFromPath(filePath)
            file = 'File:: ' + file
            self.audioFileNameTextbox.setText(file)

    def showWaitingMessage(self, message):
        waitingMsgBox = QMessageBox()
        waitingMsgBox.setText(message)
        waitingMsgBox.setStandardButtons(QMessageBox.NoButton)
        waitingMsgBox.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        waitingMsgBox.setWindowTitle('Processing')
        waitingMsgBox.show()
        QApplication.processEvents()
        return waitingMsgBox

    ###########################################################################################################
    ###########################################################################################################
                                        # EEG AND AUDIO LAYOUT  #
    ###########################################################################################################
    ###########################################################################################################

    

    def setupEEGLayout(self):
        layout = QVBoxLayout()
        
        # EEG Header
        header = QLabel('EEG (.edf) File Information')
        header.setObjectName('header')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        
        
        # EEG File Selection and Loading
        fileLoadingLayout = QHBoxLayout()
        self.eegFileNameTextbox = QLineEdit('Select EEG file...')
        self.eegSelectFileButton = QPushButton('Browse')
        self.eegLoadFileButton = QPushButton('Load')
        fileLoadingLayout.addWidget(self.eegFileNameTextbox)
        fileLoadingLayout.addWidget(self.eegSelectFileButton)
        fileLoadingLayout.addWidget(self.eegLoadFileButton)
        layout.addLayout(fileLoadingLayout)

        # EEG Sampling Frequency and Duration
        sfreqDurationLayout = QHBoxLayout()
        self.eegSamplingFreqText = QLineEdit('')
        self.eegDurationText = QLineEdit('')
        sfreqDurationLayout.addWidget(QLabel('Sampling Frequency:'))
        sfreqDurationLayout.addWidget(self.eegSamplingFreqText)
        sfreqDurationLayout.addWidget(QLabel('Duration:'))
        sfreqDurationLayout.addWidget(self.eegDurationText)
        layout.addLayout(sfreqDurationLayout)

         # EEG Sampling Frequency and Duration
        startEndTimeLayout = QHBoxLayout()
        self.eegStartTimeText = QLineEdit('')
        self.eegEndTimeText = QLineEdit('')
        startEndTimeLayout.addWidget(QLabel('Start Time:'))
        startEndTimeLayout.addWidget(self.eegStartTimeText)
        startEndTimeLayout.addWidget(QLabel('End Time:'))
        startEndTimeLayout.addWidget(self.eegEndTimeText)
        layout.addLayout(startEndTimeLayout)
        
        

        # EEG Channels
        channelsLayout = QHBoxLayout()
        self.eegAvailableChannelsList = QListWidget()
        self.eegSelectedChannelsList = QListWidget()
        addRemoveButtons = QVBoxLayout()
        self.eegAddChannelButton = QPushButton('Add >>')
        self.eegRemoveChannelButton = QPushButton('<< Remove')
        self.eegAddAllChannelButton = QPushButton('Add All >>')
        self.eegRemoveAllChannelButton = QPushButton('<< Remove All')
        self.eegVisualizeButton = QPushButton('Visualize Channel Data')
        addRemoveButtons.addWidget(self.eegAddChannelButton)
        addRemoveButtons.addWidget(self.eegRemoveChannelButton)
        channelsLayout.addWidget(self.eegAvailableChannelsList)
        addRemoveButtons.addWidget(self.eegAddAllChannelButton)
        addRemoveButtons.addWidget(self.eegRemoveAllChannelButton)
        addRemoveButtons.addWidget(self.eegVisualizeButton)
        channelsLayout.addLayout(addRemoveButtons)
        channelsLayout.addWidget(self.eegSelectedChannelsList)
        
        layout.addLayout(channelsLayout)

        # EEG Events Table
        self.eegEventsTable = QTableWidget(0, 5)
        self.eegEventsTable.setHorizontalHeaderLabels(['Stimulus', 'Block', 'Onset', 'Duration', 'OnsetIndex'])
        self.eegEventsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.eegEventsTable.horizontalHeader().setVisible(True)
        layout.addWidget(self.eegEventsTable)
        self.setEEGStyles()
        return layout   

    def setupAudioLayout(self):
        layout = QVBoxLayout()

        # Audio Header
        header = QLabel('AUDIO (.xdf) File Information')
        header.setObjectName('header')  
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

       
        # Audio File Selection and Loading
        fileLoadingLayout = QHBoxLayout()
        self.audioFileNameTextbox = QLineEdit('Select Audio file...')
        self.audioSelectFileButton = QPushButton('Browse')
        self.audioLoadFileButton = QPushButton('Load')
        fileLoadingLayout.addWidget(self.audioFileNameTextbox)
        fileLoadingLayout.addWidget(self.audioSelectFileButton)
        fileLoadingLayout.addWidget(self.audioLoadFileButton)
        layout.addLayout(fileLoadingLayout)

        # Time Difference 
        timeDifferenceLayout = QHBoxLayout()
        self.timeDifferenceText = QLineEdit('0')
        self.updateTimeDifferenceButton = QPushButton('Update')
        timeDifferenceLayout.addWidget(QLabel('Time Difference (in hours):'))   
        timeDifferenceLayout.addWidget(self.timeDifferenceText)
        timeDifferenceLayout.addWidget(self.updateTimeDifferenceButton)
        layout.addLayout(timeDifferenceLayout)

        # Audio Sampling Frequency and Duration
        sfreqDurationLayout = QHBoxLayout()
        self.audioSamplingFreqText = QLineEdit()
        self.audioDurationText = QLineEdit()
        sfreqDurationLayout.addWidget(QLabel('Sampling Frequency:'))
        sfreqDurationLayout.addWidget(self.audioSamplingFreqText)
        sfreqDurationLayout.addWidget(QLabel('Duration:'))
        sfreqDurationLayout.addWidget(self.audioDurationText)
        layout.addLayout(sfreqDurationLayout)

        # Audio Start and End Time
        audioStartEndTimeLayout = QHBoxLayout() 
        self.audioStartTimeText = QLineEdit()
        self.audioEndTimeText = QLineEdit()
        audioStartEndTimeLayout.addWidget(QLabel('Audio Start Time:'))
        audioStartEndTimeLayout.addWidget(self.audioStartTimeText)
        audioStartEndTimeLayout.addWidget(QLabel('Audio End Time:'))
        audioStartEndTimeLayout.addWidget(self.audioEndTimeText)
        layout.addLayout(audioStartEndTimeLayout)

        # Marker Start and End Time
        markerStartEndTimeLayout = QHBoxLayout() 
        self.markerStartTimeText = QLineEdit()
        self.markerEndTimeText = QLineEdit()
        markerStartEndTimeLayout.addWidget(QLabel('Markers Start Time:'))
        markerStartEndTimeLayout.addWidget(self.markerStartTimeText)
        markerStartEndTimeLayout.addWidget(QLabel('Markers End Time:'))
        markerStartEndTimeLayout.addWidget(self.markerEndTimeText)
        layout.addLayout(markerStartEndTimeLayout)


        # Audio Markers
        self.audioEventsTable = QTableWidget(0, 5)
        self.audioEventsTable.setHorizontalHeaderLabels(['Event', 'Block', 'Onset', 'Duration', 'OnsetIndex'])
        self.audioEventsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.audioEventsTable)
        self.setEEGStyles()
        return layout


    ##########################################################################################################
    #################################### AUDIO LAYOUT FUNCTIONS ##############################################
    ##########################################################################################################

    def loadAudioFile(self):
        if self.audioFilepath:
            self.waitingMessageBox = self.showWaitingMessage("Loading Audio data. Please wait...")
            self.loadThread = LoadAudioThread(self.audioFilepath)
            self.loadThread.finished.connect(self.onLoadAudioFinished)
            self.loadThread.error.connect(self.onLoadError)
            self.loadThread.start() 

    def onLoadAudioFinished(self, audioData):
        self.audioData = audioData
        self.updateAudioInfoOnPage()
        self.waitingMessageBox.accept()

    def addAudioDataToEventsTable(self):
        data = self.audioData.audioEvents
        nRows = len(data)
        self.audioEventsTable.setRowCount(nRows)
        for rowIndex in range(nRows):
            for colIndex in range(len(data[0])):
                item = QTableWidgetItem(str(data[rowIndex][colIndex]))
                item.setBackground(QBrush(getBackgroundColor(data[rowIndex][1])))
                item.setForeground(QBrush(getTextColor(data[rowIndex][0])))
                self.audioEventsTable.setItem(rowIndex, colIndex, item)

    def updateAudioInfoOnPage(self):
        self.audioSamplingFreqText.setText(str(self.audioData.samplingFrequency))
        self.audioDurationText.setText(str(self.audioData.audioDuration))
        self.audioStartTimeText.setText(str(unixToRealTime(self.audioData.audioStartTime)))
        self.audioEndTimeText.setText(str(unixToRealTime(self.audioData.audioEndTime)))        
        self.markerStartTimeText.setText(str(unixToRealTime(self.audioData.markersStartTime)))      
        self.markerEndTimeText.setText(str(unixToRealTime(self.audioData.markersEndTime)))
        self.addAudioDataToEventsTable()

    def updateAudioTimeDifference(self):
        if self.audioData:
            timeDifference = int(self.timeDifferenceText.text())
            self.audioData.mapAudioEvents(timeDifference=timeDifference)
            self.updateAudioInfoOnPage()

    def openSynchronizationPage(self):
        if not self.audioData or not self.eegData:
            return
        self.eegAudioData = EegAudioDataProcessor(
            eegData = self.eegData, 
            audioData= self.audioData
        )
        self.hide()
        self.mappingPageViewer = EegAudioMappingWindow(self.eegAudioData)
        self.mappingPageViewer.aboutToClose.connect(self.show)
        self.mappingPageViewer.show()

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
                font-size: 20px;
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
                background-color: #f5fffa; /* Muted blue for table headers */
                color: black;
                font-weight: bold;
                padding: 6px;
                height: 50px;
                border: 0px solid #bdc3c7; /* Light border for section separation */
            }
            QTableWidget::item {
                text-align: center;
            }
        ''')
