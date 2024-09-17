from PyQt5.QtGui import QColor


tableHeaderStyle = """
    QHeaderView::section {
        background-color: lightgreen;
        color: #000000;
        font-weight: bold;
    }
"""

def getBackgroundColor(block):
        if block == 'Overt':
            return QColor('lightblue')
        elif block == 'Inert':
            return QColor('lightgreen')
        return QColor('white')
    
def getTextColor(stimulus):
    if stimulus == 'Fixation':
        return QColor('blue')
    elif stimulus == 'StartSaying':
        return QColor('green')
    elif stimulus == 'StartBlockReading':
        return QColor('orange')
    elif stimulus == 'ITI':
        return QColor('red')
    return QColor('black')

def getFileNameFromPath(filePath):
    filename = filePath.split('/')[-1]
    return filename


def setAllItemsToReadOnlyInLayout(layout):
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        if widget:
            try:
                widget.setReadOnly(True)
            except:
                continue