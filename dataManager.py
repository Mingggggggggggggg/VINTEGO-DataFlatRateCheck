import os


def createData():
    pass

def loadData():
    pass

def addData(name, maxSize):

    pass

def editData(name, newMaxSize):
    pass

def delData(name):
    pass

def checkDataIntegrity(dataPath, dataFile):
    if (os.path.exists(os.path.join(os.getcwd(), dataPath, dataFile))):
        #  Überprüfe Format
        #  Pfad und MaxSize existiert
        #  Duplikate Pfade -> exit
        pass
    else:
        os.makedirs(os.path.join(dataPath, dataFile))
        print("data.json wurde erstellt. Bitte befüllen.")

def runCheck():
    loadData()
    pass