import os
import logger

log = []

def getFileNames(userPath):
    print("Profile werden über Ordnerverzeichnis abgerufen. Es kann einen Moment dauern.")    
    log.append("Profile werden über Ordnerverzeichnis abgerufen.")
    try:
        for name in os.listdir(userPath):
            if name.lower() in excludeUsersDir:
                continue

            fullPath = os.path.join(userPath, name)
            if not os.path.isdir(fullPath):
                continue

            dirProfiles.append([name, fullPath])
    except Exception as e:
        log.append(f"Fehler beim Auslesen des Ordnerverzeichnisses: {e}")
        print(f"Fehler beim Auslesen des Ordnerverzeichnisses: {e}")
    return dirProfiles
    pass